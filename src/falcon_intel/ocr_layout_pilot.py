"""Opt-in privacy-safe OCR/layout pilot diagnostics.

This module is intentionally diagnostic-only. It does not promote OCR-derived
values into verification, knowledge objects, or memory graph records.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from falcon_intel.ocr_feasibility import (
    DEFAULT_PAGE_BUCKETS,
    FIELD_ANCHOR_FAMILIES,
    OCRFeasibilityReport,
    run_local_ocr_feasibility,
)


OCR_LAYOUT_PILOT_VERSION = "1"
OUTPUT_BASENAME = "ocr-layout-pilot-report"
TARGET_FIELDS = ("inspection_date", "reviewer_name")
TARGET_PAGE_BUCKETS = {
    "inspection_date": ("first_page", "early_pages"),
    "reviewer_name": ("late_pages", "document"),
}
ANCHOR_TERMS = {
    "inspection_date": (
        "date of inspection",
        "inspection date",
        "date inspected",
        "site visit",
        "site inspection",
        "property visit",
        "date viewed",
    ),
    "reviewer_name": (
        "reviewer",
        "review appraiser",
        "reviewed by",
        "review certification",
        "appraisal review",
        "review signed",
    ),
}
DATE_RE = re.compile(
    r"\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+(?:19|20)\d{2}|"
    r"\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2})\b",
    re.I,
)
PERSON_RE = re.compile(r"^[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){1,4}(?:,?\s+[A-Z]{2,8})?$")


@dataclass(frozen=True)
class OCRLayoutDiagnostic:
    """One redacted OCR/layout diagnostic row."""

    report_index: int
    page_bucket: str
    target_field: str
    anchor_family: str
    anchor_family_detected: bool
    candidate_shape: str
    length_bucket: str
    fingerprint: str | None
    ocr_status: str
    warning_status: str | None = None


@dataclass(frozen=True)
class OCRLayoutPilotReport:
    """Privacy-safe opt-in OCR/layout pilot report."""

    pilot_version: str
    generated_at: str
    source_intake_path: str
    ocr_enabled: bool
    candidate_final_report_count: int
    analyzed_report_count: int
    target_fields: tuple[str, ...]
    diagnostics: tuple[OCRLayoutDiagnostic, ...]
    aggregate_counts: dict[str, dict[str, int]]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_local_ocr_layout_pilot(
    intake_path: str | Path,
    *,
    enable_ocr: bool = False,
    dpi: int = 170,
) -> OCRLayoutPilotReport:
    """Run the opt-in OCR/layout pilot against recommended page buckets only."""

    feasibility = run_local_ocr_feasibility(intake_path)
    intake = _load_json(intake_path)
    return build_ocr_layout_pilot_report(
        intake=intake,
        feasibility_report=feasibility,
        source_intake_path=str(intake_path),
        enable_ocr=enable_ocr,
        dpi=dpi,
    )


def build_ocr_layout_pilot_report(
    *,
    intake: dict[str, Any],
    feasibility_report: OCRFeasibilityReport | dict[str, Any],
    source_intake_path: str = "",
    enable_ocr: bool = False,
    dpi: int = 170,
    generated_at: str | None = None,
) -> OCRLayoutPilotReport:
    """Build privacy-safe OCR/layout diagnostics without storing OCR text."""

    generated_at = generated_at or datetime.now(UTC).isoformat()
    feasibility = _feasibility_payload(feasibility_report)
    files = tuple(dict(item) for item in intake.get("files", ()))
    final_reports = tuple(item for item in files if item.get("candidate_role") == "final_report")
    files_by_index = _final_report_files_by_index(final_reports)
    ocr_status = _ocr_environment_status(enable_ocr)
    diagnostics: list[OCRLayoutDiagnostic] = []
    warnings: list[str] = []

    for row in feasibility.get("rows", ()):
        row_payload = dict(row)
        report_index = int(row_payload.get("report_index") or 0)
        file_record = files_by_index.get(report_index, {})
        for field in TARGET_FIELDS:
            recommendation = dict(row_payload.get("field_recommendations", {}).get(field, {}))
            if not recommendation.get("ocr_recommended"):
                continue
            buckets = _target_buckets(field, recommendation)
            if not enable_ocr or ocr_status != "available":
                diagnostics.extend(
                    _availability_diagnostics(
                        report_index=report_index,
                        target_field=field,
                        page_buckets=buckets,
                        ocr_status=ocr_status,
                    )
                )
                continue
            rendered_rows, rendered_warnings = _ocr_pdf_buckets(
                report_index=report_index,
                file_record=file_record,
                target_field=field,
                page_buckets=buckets,
                dpi=dpi,
            )
            diagnostics.extend(rendered_rows)
            warnings.extend(rendered_warnings)

    diagnostic_tuple = tuple(diagnostics)
    return OCRLayoutPilotReport(
        pilot_version=OCR_LAYOUT_PILOT_VERSION,
        generated_at=generated_at,
        source_intake_path=str(source_intake_path),
        ocr_enabled=enable_ocr,
        candidate_final_report_count=len(final_reports),
        analyzed_report_count=len(tuple(feasibility.get("rows", ()))),
        target_fields=TARGET_FIELDS,
        diagnostics=diagnostic_tuple,
        aggregate_counts=_aggregate_counts(diagnostic_tuple),
        warnings=tuple(sorted(set(warnings))),
    )


def build_synthetic_ocr_diagnostics(
    *,
    report_index: int,
    page_bucket: str,
    target_field: str,
    ocr_text: str,
    ocr_status: str = "available",
) -> tuple[OCRLayoutDiagnostic, ...]:
    """Build redacted diagnostics from synthetic OCR-like text for tests/smokes."""

    return (_diagnostic_from_ocr_text(report_index, page_bucket, target_field, ocr_text, ocr_status=ocr_status),)


def render_ocr_layout_pilot_markdown(report: OCRLayoutPilotReport) -> str:
    """Render OCR/layout pilot diagnostics without OCR text or raw values."""

    lines = [
        "# Privacy-Safe OCR/Layout Pilot",
        "",
        "This local-only report is diagnostic-only. It does not include raw OCR text, snippets, extracted values, file names, paths, page images, screenshots, or promoted facts.",
        "",
        "## Totals",
        "",
        f"- OCR enabled: {report.ocr_enabled}",
        f"- Candidate final reports in intake: {report.candidate_final_report_count}",
        f"- Candidate final reports analyzed: {report.analyzed_report_count}",
        f"- Diagnostic rows: {len(report.diagnostics)}",
        f"- Target fields: {', '.join(report.target_fields)}",
        "",
        "## Aggregate Counts",
        "",
    ]
    for label, counts in report.aggregate_counts.items():
        lines.append(f"### {label.replace('_', ' ').title()}")
        lines.extend(_markdown_count_lines(counts))
        lines.append("")

    lines.extend(["## Diagnostics", ""])
    if not report.diagnostics:
        lines.append("- None")
    for item in report.diagnostics:
        lines.append(
            "- "
            f"report_index={item.report_index}; "
            f"bucket={item.page_bucket}; "
            f"field={item.target_field}; "
            f"anchor_family={item.anchor_family}; "
            f"anchor_detected={item.anchor_family_detected}; "
            f"shape={item.candidate_shape}; "
            f"length={item.length_bucket}; "
            f"fingerprint={item.fingerprint or 'none'}; "
            f"ocr_status={item.ocr_status}; "
            f"warning={item.warning_status or 'none'}"
        )
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in report.warnings) if report.warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_ocr_layout_pilot_outputs(
    report: OCRLayoutPilotReport,
    output_directory: str | Path,
    *,
    basename: str = OUTPUT_BASENAME,
) -> dict[str, str]:
    """Save privacy-safe OCR/layout pilot outputs under an ignored local folder."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / f"{basename}.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_ocr_layout_pilot_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _ocr_environment_status(enable_ocr: bool) -> str:
    if not enable_ocr:
        return "opt_in_required"
    try:
        import fitz  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        return "dependency_missing:pymupdf"
    try:
        import pytesseract  # type: ignore[import-not-found]
    except ImportError:
        return "dependency_missing:pytesseract"
    try:
        from PIL import Image  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        return "dependency_missing:pillow"
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        return "tesseract_executable_missing"
    return "available"


def _ocr_pdf_buckets(
    *,
    report_index: int,
    file_record: dict[str, Any],
    target_field: str,
    page_buckets: tuple[str, ...],
    dpi: int,
) -> tuple[tuple[OCRLayoutDiagnostic, ...], tuple[str, ...]]:
    path = Path(str(file_record.get("file_path") or ""))
    if str(file_record.get("extension") or "").lower() != ".pdf":
        return _availability_diagnostics(
            report_index=report_index,
            target_field=target_field,
            page_buckets=page_buckets,
            ocr_status="unsupported_source_type",
        ), ()
    if not path.exists():
        return _availability_diagnostics(
            report_index=report_index,
            target_field=target_field,
            page_buckets=page_buckets,
            ocr_status="source_missing",
        ), ()

    try:
        import fitz  # type: ignore[import-not-found]
        import pytesseract  # type: ignore[import-not-found]
        from PIL import Image  # type: ignore[import-not-found]
    except ImportError as exc:
        return _availability_diagnostics(
            report_index=report_index,
            target_field=target_field,
            page_buckets=page_buckets,
            ocr_status=f"dependency_missing:{exc.name or 'ocr'}",
        ), ()

    diagnostics: list[OCRLayoutDiagnostic] = []
    warnings: list[str] = []
    try:
        document = fitz.open(str(path))
        page_count = int(document.page_count)
        for page_index in _page_indexes_for_buckets(page_count, page_buckets):
            page = document.load_page(page_index)
            matrix = fitz.Matrix(dpi / 72, dpi / 72)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            text = pytesseract.image_to_string(image) or ""
            bucket = _page_bucket(page_index + 1, page_count)
            diagnostics.append(_diagnostic_from_ocr_text(report_index, bucket, target_field, text, ocr_status="available"))
        document.close()
    except Exception as exc:  # pragma: no cover - depends on local OCR/PDF tooling
        warnings.append(f"ocr_runtime_warning:{type(exc).__name__}")
        diagnostics.extend(
            _availability_diagnostics(
                report_index=report_index,
                target_field=target_field,
                page_buckets=page_buckets,
                ocr_status="runtime_warning",
            )
        )
    return tuple(diagnostics), tuple(warnings)


def _diagnostic_from_ocr_text(
    report_index: int,
    page_bucket: str,
    target_field: str,
    ocr_text: str,
    *,
    ocr_status: str,
) -> OCRLayoutDiagnostic:
    anchor_family = FIELD_ANCHOR_FAMILIES[target_field]
    anchor_detected = _anchor_detected(target_field, ocr_text)
    candidate = _candidate_from_ocr_text(target_field, ocr_text) if anchor_detected else None
    return OCRLayoutDiagnostic(
        report_index=report_index,
        page_bucket=page_bucket,
        target_field=target_field,
        anchor_family=anchor_family,
        anchor_family_detected=anchor_detected,
        candidate_shape=_candidate_shape(target_field, candidate),
        length_bucket=_length_bucket(len(candidate or "")),
        fingerprint=_fingerprint(target_field, candidate),
        ocr_status=ocr_status,
        warning_status=None if ocr_status == "available" else ocr_status,
    )


def _availability_diagnostics(
    *,
    report_index: int,
    target_field: str,
    page_buckets: tuple[str, ...],
    ocr_status: str,
) -> tuple[OCRLayoutDiagnostic, ...]:
    anchor_family = FIELD_ANCHOR_FAMILIES[target_field]
    return tuple(
        OCRLayoutDiagnostic(
            report_index=report_index,
            page_bucket=bucket,
            target_field=target_field,
            anchor_family=anchor_family,
            anchor_family_detected=False,
            candidate_shape="not_attempted",
            length_bucket="0",
            fingerprint=None,
            ocr_status=ocr_status,
            warning_status=ocr_status,
        )
        for bucket in page_buckets
    )


def _candidate_from_ocr_text(target_field: str, text: str) -> str | None:
    lines = [_clean_line(line) for line in text.splitlines() if _clean_line(line)]
    if target_field == "inspection_date":
        match = DATE_RE.search(" ".join(lines))
        return match.group(0) if match else None
    for index, line in enumerate(lines):
        if any(term in _normalize(line) for term in ANCHOR_TERMS[target_field]):
            for candidate in lines[index : index + 4]:
                cleaned = _clean_line(re.sub(r"(?i)^(reviewed by|review appraiser|reviewer)\s*:?\s*", "", candidate))
                if PERSON_RE.match(cleaned):
                    return cleaned
    return None


def _anchor_detected(target_field: str, text: str) -> bool:
    normalized = _normalize(text)
    return any(term in normalized for term in ANCHOR_TERMS[target_field])


def _candidate_shape(target_field: str, candidate: str | None) -> str:
    if not candidate:
        return "missing"
    if target_field == "inspection_date" and DATE_RE.search(candidate):
        return "date-like"
    if target_field == "reviewer_name" and PERSON_RE.match(candidate):
        return "person-like"
    if len(candidate) > 80:
        return "long-text"
    return "short-text"


def _target_buckets(field: str, recommendation: dict[str, Any]) -> tuple[str, ...]:
    allowed = set(TARGET_PAGE_BUCKETS[field])
    buckets = tuple(str(item) for item in recommendation.get("recommended_page_buckets", ()) if str(item) in allowed)
    if buckets:
        return tuple(dict.fromkeys(buckets))
    return tuple(DEFAULT_PAGE_BUCKETS[field])


def _page_indexes_for_buckets(page_count: int, page_buckets: tuple[str, ...]) -> tuple[int, ...]:
    indexes: list[int] = []
    for page_number in range(1, page_count + 1):
        bucket = _page_bucket(page_number, page_count)
        if bucket in page_buckets:
            indexes.append(page_number - 1)
    return tuple(dict.fromkeys(indexes))


def _page_bucket(page_number: int, total_pages: int) -> str:
    if page_number <= 1:
        return "first_page"
    if page_number <= 3:
        return "early_pages"
    if total_pages and page_number > max(3, total_pages - 3):
        return "late_pages"
    return "middle_pages"


def _final_report_files_by_index(final_reports: tuple[dict[str, Any], ...]) -> dict[int, dict[str, Any]]:
    return {index: item for index, item in enumerate(final_reports, start=1)}


def _feasibility_payload(report: OCRFeasibilityReport | dict[str, Any]) -> dict[str, Any]:
    if isinstance(report, OCRFeasibilityReport):
        return report.to_dict()
    return dict(report)


def _aggregate_counts(items: Iterable[OCRLayoutDiagnostic]) -> dict[str, dict[str, int]]:
    diagnostics = tuple(items)
    return {
        "target_field": _counter_to_dict(Counter(item.target_field for item in diagnostics)),
        "page_bucket": _counter_to_dict(Counter(item.page_bucket for item in diagnostics)),
        "anchor_family_detected": _counter_to_dict(Counter(str(item.anchor_family_detected).lower() for item in diagnostics)),
        "candidate_shape": _counter_to_dict(Counter(item.candidate_shape for item in diagnostics)),
        "length_bucket": _counter_to_dict(Counter(item.length_bucket for item in diagnostics)),
        "ocr_status": _counter_to_dict(Counter(item.ocr_status for item in diagnostics)),
        "warning_status": _counter_to_dict(Counter(item.warning_status or "none" for item in diagnostics)),
    }


def _fingerprint(target_field: str, value: str | None) -> str | None:
    if not value:
        return None
    normalized = re.sub(r"\s+", " ", value).strip().lower()
    return hashlib.sha256(f"falcon-ocr-layout-v1|{target_field}|{normalized}".encode("utf-8")).hexdigest()[:10]


def _length_bucket(length: int) -> str:
    if length == 0:
        return "0"
    if length <= 12:
        return "1-12"
    if length <= 32:
        return "13-32"
    if length <= 80:
        return "33-80"
    return "81+"


def _clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" :-\t")[:160]


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted((key, int(value)) for key, value in counter.items()))


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
