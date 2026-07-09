"""Local-only historical report intake inventory.

The intake inventory is a staging tool. It reads filesystem metadata and file
bytes only for hashing. It does not parse document bodies, OCR, upload, move,
rename, delete, or write to source folders.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import csv
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable


DEFAULT_INCLUDED_EXTENSIONS = {
    ".csv",
    ".doc",
    ".docx",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".tif",
    ".tiff",
    ".txt",
    ".xls",
    ".xlsm",
    ".xlsx",
    ".xml",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
REPORT_EXTENSIONS = {".doc", ".docx", ".pdf"}
WORKBOOK_EXTENSIONS = {".csv", ".xls", ".xlsm", ".xlsx"}

ROLE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("rent_roll", ("rent roll", "rent-roll", "rentroll", "rent_roll")),
    ("engagement_letter", ("engagement", "engagement letter", "loe", "contract")),
    ("map", ("map", "aerial", "parcel", "plat", "flood", "zoning")),
    ("photo", ("photo", "photos", "image", "front", "exterior", "interior")),
    ("draft_report", ("draft", "working", "wip", "review draft")),
    ("final_report", ("final", "signed", "complete", "completed", "report")),
    (
        "source_document",
        (
            "addendum",
            "appendix",
            "backup",
            "comparable",
            "comps",
            "deed",
            "grid",
            "insurable",
            "invoice",
            "lease",
            "prc",
            "property record",
            "sales comp",
            "source",
            "support",
            "tax",
            "taxes",
        ),
    ),
)

ORDER_ID_RE = re.compile(r"\b(?:order|job|file|assignment|project)[-_ ]?#?([a-z0-9]{3,}[-_ ]?[a-z0-9]*)\b", re.I)
UNLABELLED_ASSIGNMENT_ID_RE = re.compile(r"(?<!\d)\d{4,6}[-_ ]\d{4,8}(?!\d)")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
DATE_RE = re.compile(
    r"\b(?:(20\d{2})[-_ .]?(0[1-9]|1[0-2])[-_ .]?([0-3]\d)|"
    r"(0[1-9]|1[0-2])[-_ .]([0-3]\d)[-_ .](20\d{2}))\b"
)
ADDRESS_RE = re.compile(
    r"\b\d{2,6}\s+[a-z0-9][a-z0-9 .'-]*(?:street|st|avenue|ave|road|rd|drive|dr|"
    r"lane|ln|court|ct|boulevard|blvd|way|loop|parkway|pkwy|circle|cir|"
    r"highway|hwy|place|pl|terrace|ter|trail|square|sq)\b",
    re.I,
)


@dataclass(frozen=True)
class HistoricalIntakeConfig:
    """Configuration for a read-only historical intake inventory scan."""

    source_directories: tuple[str, ...]
    include_extensions: tuple[str, ...] = tuple(sorted(DEFAULT_INCLUDED_EXTENSIONS))
    exclude_directories: tuple[str, ...] = (
        ".git",
        "__pycache__",
        "node_modules",
        "data/historical-intake",
        "data/manifests",
        "data/profiles",
    )
    max_file_size_warning_mb: int = 50
    dry_run: bool = True
    output_directory: str = "data/historical-intake"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HistoricalIntakeConfig":
        source_directories = tuple(str(item) for item in payload.get("source_directories", ()))
        include_extensions = tuple(
            _normalize_extension(str(item)) for item in payload.get("include_extensions", sorted(DEFAULT_INCLUDED_EXTENSIONS))
        )
        exclude_directories = tuple(str(item) for item in payload.get("exclude_directories", cls.exclude_directories))
        return cls(
            source_directories=source_directories,
            include_extensions=include_extensions,
            exclude_directories=exclude_directories,
            max_file_size_warning_mb=int(payload.get("max_file_size_warning_mb", 50)),
            dry_run=bool(payload.get("dry_run", True)),
            output_directory=str(payload.get("output_directory", "data/historical-intake")),
        )


@dataclass(frozen=True)
class HistoricalFileRecord:
    """One discovered historical file candidate."""

    file_id: str
    source_root: str
    file_path: str
    file_name: str
    normalized_file_name: str
    extension: str
    size_bytes: int
    created_timestamp: str
    modified_timestamp: str
    parent_folder: str
    folder_key: str
    sha256: str
    likely_order_identifier: str | None
    likely_property_address: str | None
    likely_client: str | None
    likely_report_type: str | None
    likely_report_date: str | None
    candidate_role: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class DuplicateGroup:
    """A conservative duplicate group."""

    duplicate_type: str
    duplicate_key: str
    file_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class CandidateOrderGroup:
    """A preliminary historical order/report package."""

    group_id: str
    file_ids: tuple[str, ...]
    confidence_level: str
    grouping_key: str
    grouping_reason: str
    likely_order_identifier: str | None
    likely_property_address: str | None
    likely_client: str | None
    likely_report_date: str | None
    likely_primary_report_file_id: str | None
    missing_unknown_fields: tuple[str, ...]
    readiness_classification: str
    readiness_reason: str


@dataclass(frozen=True)
class HistoricalIntakeInventory:
    """Complete local historical intake inventory payload."""

    inventory_version: str
    generated_at: str
    dry_run: bool
    source_directories: tuple[str, ...]
    include_extensions: tuple[str, ...]
    exclude_directories: tuple[str, ...]
    files: tuple[HistoricalFileRecord, ...]
    duplicate_groups: tuple[DuplicateGroup, ...]
    candidate_order_groups: tuple[CandidateOrderGroup, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "inventory_version": self.inventory_version,
            "generated_at": self.generated_at,
            "dry_run": self.dry_run,
            "source_directories": list(self.source_directories),
            "include_extensions": list(self.include_extensions),
            "exclude_directories": list(self.exclude_directories),
            "files": [asdict(item) for item in self.files],
            "duplicate_groups": [asdict(item) for item in self.duplicate_groups],
            "candidate_order_groups": [asdict(item) for item in self.candidate_order_groups],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "summary": build_inventory_summary(self),
        }


def load_historical_intake_config(path: str | Path) -> HistoricalIntakeConfig:
    """Load a local intake config JSON file."""

    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return HistoricalIntakeConfig.from_dict(payload)


def run_historical_intake(config: HistoricalIntakeConfig) -> HistoricalIntakeInventory:
    """Build a read-only historical intake inventory."""

    if not config.source_directories:
        raise ValueError("At least one source directory is required.")
    if config.max_file_size_warning_mb < 1:
        raise ValueError("max_file_size_warning_mb must be at least 1.")

    include_extensions = tuple(sorted({_normalize_extension(item) for item in config.include_extensions}))
    warnings: list[str] = []
    errors: list[str] = []
    files: list[HistoricalFileRecord] = []
    seen_paths: set[Path] = set()

    for source_root in config.source_directories:
        root = Path(source_root).expanduser()
        try:
            resolved_root = root.resolve(strict=True)
        except FileNotFoundError:
            errors.append(f"Source directory does not exist: {source_root}")
            continue

        if not resolved_root.is_dir():
            errors.append(f"Source path is not a directory: {source_root}")
            continue
        if resolved_root.is_symlink():
            errors.append(f"Source directory cannot be a symlink: {source_root}")
            continue
        if resolved_root in seen_paths:
            warnings.append(f"Duplicate source directory skipped: {resolved_root}")
            continue
        seen_paths.add(resolved_root)

        for path in _iter_candidate_files(resolved_root, include_extensions, config.exclude_directories):
            files.append(_build_file_record(path, resolved_root, config.max_file_size_warning_mb))

    files = sorted(files, key=lambda item: item.file_path.lower())
    duplicate_groups = detect_duplicate_groups(files)
    candidate_groups = group_candidate_orders(files, duplicate_groups)

    return HistoricalIntakeInventory(
        inventory_version="1",
        generated_at=datetime.now(UTC).isoformat(),
        dry_run=config.dry_run,
        source_directories=tuple(config.source_directories),
        include_extensions=include_extensions,
        exclude_directories=tuple(config.exclude_directories),
        files=tuple(files),
        duplicate_groups=tuple(duplicate_groups),
        candidate_order_groups=tuple(candidate_groups),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def normalize_filename(name: str) -> str:
    """Normalize a file or folder label for conservative matching."""

    stem = Path(name).stem if Path(name).suffix else name
    normalized = stem.lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[_-]+", " ", normalized)
    normalized = re.sub(r"\b(final|draft|signed|complete|completed|copy|rev|revised|v\d+)\b", " ", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def classify_candidate_role(path: str | Path) -> str:
    """Classify the likely role from filename and folder names only."""

    file_path = Path(path)
    extension = file_path.suffix.lower()
    text = " ".join(part.lower() for part in file_path.parts[-4:])
    normalized_text = re.sub(r"[^a-z0-9]+", " ", text).strip()

    if extension in IMAGE_EXTENSIONS:
        return "map" if _has_any(normalized_text, ("map", "aerial", "parcel", "plat")) else "photo"

    file_label = re.sub(r"[^a-z0-9]+", " ", file_path.stem.lower()).strip()
    if extension in REPORT_EXTENSIONS and _has_any(file_label, ("appraisal", "valuation", "narrative")):
        return "final_report"
    if extension in REPORT_EXTENSIONS and "restricted" in file_label and "report" in file_label:
        return "final_report"

    for role, patterns in ROLE_PATTERNS:
        if _has_any(normalized_text, patterns):
            if role in {"final_report", "draft_report"} and extension not in REPORT_EXTENSIONS:
                continue
            return role

    if extension in WORKBOOK_EXTENSIONS and _has_any(normalized_text, ("rent", "roll", "lease", "income")):
        return "rent_roll"
    if extension in REPORT_EXTENSIONS and _has_any(normalized_text, ("appraisal", "narrative", "valuation")):
        return "final_report"
    if extension in WORKBOOK_EXTENSIONS:
        return "source_document"
    return "unknown"


def detect_duplicate_groups(files: Iterable[HistoricalFileRecord]) -> list[DuplicateGroup]:
    """Detect exact, likely, and possible duplicate groups without deleting anything."""

    file_list = list(files)
    groups: list[DuplicateGroup] = []
    assigned_exact: set[str] = set()

    by_hash: dict[str, list[HistoricalFileRecord]] = defaultdict(list)
    by_name_size: dict[tuple[str, int], list[HistoricalFileRecord]] = defaultdict(list)
    by_possible: dict[tuple[str | None, str | None, str | None], list[HistoricalFileRecord]] = defaultdict(list)

    for record in file_list:
        by_hash[record.sha256].append(record)
        by_name_size[(record.normalized_file_name, record.size_bytes)].append(record)
        possible_key = (
            _present(record.likely_order_identifier),
            _present(record.likely_property_address),
            _present(record.likely_report_date),
        )
        if sum(1 for item in possible_key if item) >= 2:
            by_possible[possible_key].append(record)

    for digest, records in sorted(by_hash.items()):
        if len(records) < 2:
            continue
        file_ids = tuple(record.file_id for record in records)
        assigned_exact.update(file_ids)
        groups.append(
            DuplicateGroup(
                duplicate_type="exact_hash",
                duplicate_key=digest,
                file_ids=file_ids,
                reason="Files have the same SHA-256 hash.",
            )
        )

    for (name, size), records in sorted(by_name_size.items()):
        file_ids = tuple(record.file_id for record in records if record.file_id not in assigned_exact)
        if len(file_ids) < 2:
            continue
        groups.append(
            DuplicateGroup(
                duplicate_type="likely_name_size",
                duplicate_key=f"{name}|{size}",
                file_ids=file_ids,
                reason="Files share the same normalized filename and file size.",
            )
        )

    for key, records in sorted(by_possible.items(), key=lambda item: str(item[0])):
        file_ids = tuple(record.file_id for record in records)
        if len(file_ids) < 2:
            continue
        groups.append(
            DuplicateGroup(
                duplicate_type="possible_order_property_date",
                duplicate_key="|".join(item or "" for item in key),
                file_ids=file_ids,
                reason="Files share at least two of order identifier, property address, and report date.",
            )
        )

    return groups


def group_candidate_orders(
    files: Iterable[HistoricalFileRecord],
    duplicate_groups: Iterable[DuplicateGroup] = (),
) -> list[CandidateOrderGroup]:
    """Group files into preliminary historical order packages."""

    file_list = list(files)
    duplicate_heavy_ids = _duplicate_heavy_file_ids(duplicate_groups)
    grouped: dict[str, list[HistoricalFileRecord]] = defaultdict(list)
    reasons: dict[str, str] = {}

    for record in file_list:
        key, reason = _group_key(record)
        grouped[key].append(record)
        reasons[key] = reason

    groups: list[CandidateOrderGroup] = []
    for index, (key, records) in enumerate(sorted(grouped.items()), start=1):
        primary = _find_primary_report(records)
        known_fields = {
            "likely_order_identifier": _most_common(record.likely_order_identifier for record in records),
            "likely_property_address": _most_common(record.likely_property_address for record in records),
            "likely_client": _most_common(record.likely_client for record in records),
            "likely_report_date": _most_common(record.likely_report_date for record in records),
        }
        missing = tuple(label for label, value in known_fields.items() if not value)
        readiness, readiness_reason = classify_readiness(records, primary, duplicate_heavy_ids)
        confidence = _group_confidence(records, reasons[key], missing)

        groups.append(
            CandidateOrderGroup(
                group_id=f"hist-group-{index:04d}",
                file_ids=tuple(record.file_id for record in records),
                confidence_level=confidence,
                grouping_key=key,
                grouping_reason=reasons[key],
                likely_order_identifier=known_fields["likely_order_identifier"],
                likely_property_address=known_fields["likely_property_address"],
                likely_client=known_fields["likely_client"],
                likely_report_date=known_fields["likely_report_date"],
                likely_primary_report_file_id=primary.file_id if primary else None,
                missing_unknown_fields=missing,
                readiness_classification=readiness,
                readiness_reason=readiness_reason,
            )
        )

    return groups


def classify_readiness(
    records: Iterable[HistoricalFileRecord],
    primary_report: HistoricalFileRecord | None = None,
    duplicate_heavy_file_ids: set[str] | None = None,
) -> tuple[str, str]:
    """Classify readiness for one candidate order/report group."""

    record_list = list(records)
    duplicate_heavy_file_ids = duplicate_heavy_file_ids or set()
    roles = Counter(record.candidate_role for record in record_list)
    has_final = roles["final_report"] > 0
    has_unknown_majority = roles["unknown"] >= max(2, len(record_list) / 2)
    duplicate_count = sum(1 for record in record_list if record.file_id in duplicate_heavy_file_ids)

    if duplicate_count >= 3 or (record_list and duplicate_count / len(record_list) >= 0.5 and duplicate_count > 1):
        return "Duplicate-heavy", "Multiple files in the package appear in duplicate groups."
    if not has_final and roles["draft_report"] > 0:
        return "Missing final report", "Draft report found, but no likely final report was identified."
    if not has_final:
        return "Missing final report", "No likely final report was identified from filename or folder heuristics."
    if has_unknown_majority:
        return "Unknown / insufficient metadata", "Most files could not be classified from filename or folder metadata."
    if len(record_list) >= 2 and (roles["source_document"] or roles["rent_roll"] or roles["map"] or roles["photo"]):
        return "Ready for future extraction", "Likely final report and supporting materials are present."
    return "Needs review", "Likely final report exists, but supporting package context is limited."


def build_inventory_summary(inventory: HistoricalIntakeInventory) -> dict[str, Any]:
    """Build machine-readable summary metrics."""

    extension_counts = Counter(record.extension for record in inventory.files)
    readiness_counts = Counter(group.readiness_classification for group in inventory.candidate_order_groups)
    role_counts = Counter(record.candidate_role for record in inventory.files)
    top_folders = Counter(record.parent_folder for record in inventory.files).most_common(10)
    largest_files = sorted(inventory.files, key=lambda item: item.size_bytes, reverse=True)[:10]

    return {
        "total_files_scanned": len(inventory.files),
        "total_candidate_order_groups": len(inventory.candidate_order_groups),
        "likely_final_reports": role_counts["final_report"],
        "likely_duplicate_groups": len(inventory.duplicate_groups),
        "unknown_files": role_counts["unknown"],
        "file_type_breakdown": dict(sorted(extension_counts.items())),
        "candidate_role_breakdown": dict(sorted(role_counts.items())),
        "readiness_breakdown": dict(sorted(readiness_counts.items())),
        "top_folders_scanned": [{"folder": folder, "file_count": count} for folder, count in top_folders],
        "largest_files": [
            {"file_id": record.file_id, "file_name": record.file_name, "size_bytes": record.size_bytes}
            for record in largest_files
        ],
        "warnings": list(inventory.warnings),
        "errors": list(inventory.errors),
    }


def render_inventory_markdown(inventory: HistoricalIntakeInventory) -> str:
    """Render a human-readable inventory summary without document text."""

    summary = build_inventory_summary(inventory)
    lines = [
        "# Historical Report Intake Summary",
        "",
        "This local inventory is metadata-only. It does not parse report bodies, OCR files, upload data, or modify source files.",
        "",
        "## Totals",
        "",
        f"- Total files scanned: {summary['total_files_scanned']}",
        f"- Candidate order groups: {summary['total_candidate_order_groups']}",
        f"- Likely final reports: {summary['likely_final_reports']}",
        f"- Likely duplicate groups: {summary['likely_duplicate_groups']}",
        f"- Unknown files: {summary['unknown_files']}",
        "",
        "## File Type Breakdown",
        "",
    ]
    lines.extend(_markdown_count_lines(summary["file_type_breakdown"]))
    lines.extend(["", "## Readiness Breakdown", ""])
    lines.extend(_markdown_count_lines(summary["readiness_breakdown"]))
    lines.extend(["", "## Top Folders Scanned", ""])
    if summary["top_folders_scanned"]:
        for item in summary["top_folders_scanned"]:
            lines.append(f"- {item['folder']}: {item['file_count']} files")
    else:
        lines.append("- None")
    lines.extend(["", "## Largest Files", ""])
    if summary["largest_files"]:
        for item in summary["largest_files"]:
            lines.append(f"- {item['file_name']}: {item['size_bytes']} bytes")
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings / Errors", ""])
    warnings = list(inventory.warnings) + list(inventory.errors)
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Suggested Next Cleanup Actions",
            "",
            "- Review duplicate-heavy groups before any future ingestion planning.",
            "- Confirm groups missing likely final reports.",
            "- Resolve unknown client, address, order identifier, and report date fields where useful.",
            "- Keep source files in place; do not move, rename, or delete based on this inventory alone.",
        ]
    )
    return "\n".join(lines) + "\n"


def save_inventory_outputs(
    inventory: HistoricalIntakeInventory,
    output_directory: str | Path,
    *,
    basename: str = "historical-intake-report",
) -> dict[str, str]:
    """Save JSON, CSV, and Markdown outputs under the configured output directory."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    csv_path = output_dir / f"{basename}.csv"
    markdown_name = "historical-intake-summary.md" if basename == "historical-intake-report" else f"{basename}-summary.md"
    markdown_path = output_dir / markdown_name

    json_path.write_text(json.dumps(inventory.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    _write_inventory_csv(inventory, csv_path)
    markdown_path.write_text(render_inventory_markdown(inventory), encoding="utf-8")
    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(markdown_path)}


def _iter_candidate_files(
    root: Path,
    include_extensions: tuple[str, ...],
    exclude_directories: tuple[str, ...],
) -> Iterable[Path]:
    excluded = {_normalize_path_fragment(item) for item in exclude_directories}
    include_set = set(include_extensions)
    for current, directory_names, file_names in os.walk(root):
        current_path = Path(current)
        directory_names[:] = [
            name
            for name in directory_names
            if not (current_path / name).is_symlink()
            and _normalize_path_fragment((current_path / name).relative_to(root).as_posix()) not in excluded
            and _normalize_path_fragment(name) not in excluded
        ]
        for file_name in file_names:
            path = current_path / file_name
            if path.is_symlink() or path.suffix.lower() not in include_set:
                continue
            yield path


def _build_file_record(path: Path, source_root: Path, max_file_size_warning_mb: int) -> HistoricalFileRecord:
    stats = path.stat()
    extension = path.suffix.lower()
    path_text = " ".join(path.parts[-5:])
    normalized_name = normalize_filename(path.name)
    warnings: list[str] = []
    max_bytes = max_file_size_warning_mb * 1024 * 1024
    if stats.st_size > max_bytes:
        warnings.append(f"File exceeds {max_file_size_warning_mb} MB warning threshold.")

    return HistoricalFileRecord(
        file_id=_file_id(path),
        source_root=str(source_root),
        file_path=str(path),
        file_name=path.name,
        normalized_file_name=normalized_name,
        extension=extension,
        size_bytes=stats.st_size,
        created_timestamp=datetime.fromtimestamp(stats.st_ctime, UTC).isoformat(),
        modified_timestamp=datetime.fromtimestamp(stats.st_mtime, UTC).isoformat(),
        parent_folder=str(path.parent),
        folder_key=normalize_filename(path.parent.name),
        sha256=_hash_file(path),
        likely_order_identifier=_infer_order_identifier(path_text),
        likely_property_address=_infer_property_address(path_text),
        likely_client=_infer_client(path),
        likely_report_type=_infer_report_type(path_text),
        likely_report_date=_infer_report_date(path_text),
        candidate_role=classify_candidate_role(path),
        warnings=tuple(warnings),
    )


def _write_inventory_csv(inventory: HistoricalIntakeInventory, path: Path) -> None:
    fieldnames = [
        "file_id",
        "file_path",
        "file_name",
        "extension",
        "size_bytes",
        "modified_timestamp",
        "parent_folder",
        "likely_order_identifier",
        "likely_property_address",
        "likely_client",
        "likely_report_type",
        "likely_report_date",
        "candidate_role",
        "sha256",
        "warnings",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in inventory.files:
            payload = asdict(record)
            payload["warnings"] = "; ".join(record.warnings)
            writer.writerow({field: payload.get(field, "") for field in fieldnames})


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_id(path: Path) -> str:
    return hashlib.sha1(str(path.resolve()).encode("utf-8")).hexdigest()[:16]


def _normalize_extension(value: str) -> str:
    stripped = value.strip().lower()
    if not stripped:
        raise ValueError("File extensions cannot be empty.")
    return stripped if stripped.startswith(".") else f".{stripped}"


def _normalize_path_fragment(value: str) -> str:
    return value.replace("\\", "/").strip("/").lower()


def _has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def _present(value: str | None) -> str | None:
    return value.lower() if value else None


def _has_explicit_order_context(text: str) -> bool:
    return bool(re.search(r"\b(order|job|file|assignment|project)[-_ ]?#?", text, re.I))


def _infer_order_identifier(text: str) -> str | None:
    match = ORDER_ID_RE.search(text)
    if match:
        return re.sub(r"\s+", "-", match.group(1).strip().upper())
    match = UNLABELLED_ASSIGNMENT_ID_RE.search(text)
    if match:
        return re.sub(r"[-_ ]+", "-", match.group(0)).upper()
    return None


def _infer_property_address(text: str) -> str | None:
    match = ADDRESS_RE.search(text)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(0)).strip().title()


def _infer_client(path: Path) -> str | None:
    for part in reversed(path.parts[-5:-1]):
        normalized = normalize_filename(part)
        if normalized.startswith("client "):
            return normalized.removeprefix("client ").title()
        if normalized.endswith(" client"):
            return normalized.removesuffix(" client").title()
    return None


def _infer_report_type(text: str) -> str | None:
    normalized = normalize_filename(text)
    if "restricted" in normalized and "report" in normalized:
        return "restricted appraisal report"
    if "appraisal" in normalized:
        return "appraisal report"
    if "retail" in normalized:
        return "retail"
    if "office" in normalized:
        return "office"
    if "industrial" in normalized or "warehouse" in normalized or "logistics" in normalized:
        return "industrial"
    if "multifamily" in normalized or "apartment" in normalized:
        return "multifamily"
    if "land" in normalized:
        return "land"
    return None


def _infer_report_date(text: str) -> str | None:
    match = DATE_RE.search(text)
    if match:
        if match.group(1):
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        return f"{match.group(6)}-{match.group(4)}-{match.group(5)}"
    year = YEAR_RE.search(text)
    return year.group(0) if year else None


def _group_key(record: HistoricalFileRecord) -> tuple[str, str]:
    if record.likely_order_identifier and _has_explicit_order_context(record.file_path):
        return f"order:{record.likely_order_identifier.lower()}", "Shared likely order identifier."
    if record.likely_property_address:
        return f"address:{normalize_filename(record.likely_property_address)}", "Shared likely property address."
    if record.likely_order_identifier:
        return f"order:{record.likely_order_identifier.lower()}", "Shared likely order identifier."
    if record.folder_key:
        return f"folder:{record.parent_folder.lower()}", "Shared parent folder."
    return f"file:{record.file_id}", "Single file fallback group."


def _find_primary_report(records: Iterable[HistoricalFileRecord]) -> HistoricalFileRecord | None:
    record_list = list(records)
    final_reports = [record for record in record_list if record.candidate_role == "final_report"]
    if final_reports:
        return sorted(final_reports, key=lambda item: (item.modified_timestamp, item.file_name), reverse=True)[0]
    report_like = [record for record in record_list if record.extension in REPORT_EXTENSIONS]
    if report_like:
        return sorted(report_like, key=lambda item: (item.modified_timestamp, item.file_name), reverse=True)[0]
    return None


def _duplicate_heavy_file_ids(duplicate_groups: Iterable[DuplicateGroup]) -> set[str]:
    ids: set[str] = set()
    for group in duplicate_groups:
        if group.duplicate_type in {"exact_hash", "likely_name_size"}:
            ids.update(group.file_ids)
    return ids


def _most_common(values: Iterable[str | None]) -> str | None:
    counter = Counter(value for value in values if value)
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def _group_confidence(records: list[HistoricalFileRecord], reason: str, missing: tuple[str, ...]) -> str:
    if reason.startswith("Shared likely order"):
        return "high"
    if reason.startswith("Shared likely property") and len(records) > 1:
        return "medium"
    if len(records) > 2 and len(missing) <= 2:
        return "medium"
    return "low"


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label or 'unknown'}: {count}" for label, count in sorted(counts.items())]
