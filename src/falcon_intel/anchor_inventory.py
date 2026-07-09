"""Privacy-safe anchor-family inventory over searchable local report text."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any, Iterable

from falcon_intel.historical_knowledge import (
    APPRAISER_CREDENTIAL_PHRASES,
    PageText,
    REPORT_TITLE_PHRASES,
    _companion_docx_by_report,
    _extract_companion_docx_pages,
    _extract_embedded_docx_text,
    _extract_embedded_pdf_text,
    _is_plausible_person_name,
)


ANCHOR_INVENTORY_VERSION = "1"
OUTPUT_BASENAME = "anchor-inventory-report"
ANCHOR_TO_FIELD_BASENAME = "anchor-to-field-diagnostics-report"
COMPANY_OR_TITLE_TERMS = {
    "appraisal",
    "appraisals",
    "associates",
    "company",
    "corp",
    "corporation",
    "group",
    "inc",
    "llc",
    "management",
    "partners",
    "realty",
    "services",
    "valuation",
}
GENERIC_TITLE_VALUES = {
    "appraisal report",
    "real estate appraisal report",
    "valuation report",
    "evaluation report",
}

ANCHOR_FAMILIES: dict[str, tuple[str, ...]] = {
    "inspection_site_visit": (
        "date of inspection",
        "inspection date",
        "date inspected",
        "site visit",
        "site inspection",
        "property visit",
        "property was inspected",
        "subject was observed",
        "date viewed",
    ),
    "appraiser_signature_certification": (
        "appraiser",
        "prepared by",
        "signed by",
        "certified general",
        "state certified",
        "real estate appraiser",
        "certification of appraisal",
        "appraiser certification",
        "appraisal certification",
    ),
    "reviewer_review": (
        "reviewer",
        "review appraiser",
        "reviewed by",
        "review certification",
        "appraisal review",
        "review signed",
    ),
    "report_title_title_block": (
        "appraisal report",
        "restricted appraisal report",
        "restricted use appraisal report",
        "valuation report",
        "evaluation report",
        "market value appraisal report",
        "narrative appraisal report",
    ),
    "client_intended_user": (
        "client",
        "client name",
        "intended user",
        "intended users",
        "intended use",
    ),
    "approach_sections": (
        "sales comparison approach",
        "income approach",
        "income capitalization approach",
        "cost approach",
    ),
}


@dataclass(frozen=True)
class AnchorInventoryRow:
    """One privacy-safe anchor-family count bucket."""

    report_index: int
    source_tier: str
    source_type: str
    page_bucket: str
    anchor_family: str
    count: int


@dataclass(frozen=True)
class AnchorInventoryReport:
    """Privacy-safe anchor-family inventory report."""

    inventory_version: str
    generated_at: str
    source_intake_path: str
    analyzed_report_count: int
    inventory_rows: tuple[AnchorInventoryRow, ...]
    aggregate_counts: dict[str, dict[str, int]]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnchorToFieldDiagnostic:
    """One redacted nearby-candidate diagnostic for an appraiser/title anchor."""

    report_index: int
    field_name: str
    anchor_family: str
    source_tier: str
    source_type: str
    page_bucket: str
    nearby_candidate_shape: str
    candidate_length_bucket: str
    rejection_reason: str
    provenance_method: str


@dataclass(frozen=True)
class AnchorToFieldDiagnosticsReport:
    """Privacy-safe anchor-to-field diagnostics for appraiser/title extraction."""

    diagnostics_version: str
    generated_at: str
    source_intake_path: str
    analyzed_report_count: int
    diagnostic_count: int
    diagnostics: tuple[AnchorToFieldDiagnostic, ...]
    aggregate_counts: dict[str, dict[str, int]]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_local_anchor_inventory(intake_path: str | Path) -> AnchorInventoryReport:
    """Inventory anchor-family counts from local searchable PDF/DOCX text."""

    payload = json.loads(Path(intake_path).read_text(encoding="utf-8-sig"))
    files = tuple(dict(item) for item in payload.get("files", []))
    companion_docx_by_report = _companion_docx_by_report(files, payload.get("candidate_order_groups", []))
    rows: list[AnchorInventoryRow] = []
    warnings: list[str] = []
    report_index = 0

    for file_record in files:
        if file_record.get("candidate_role") != "final_report":
            continue
        extension = str(file_record.get("extension") or "").lower()
        if extension not in {".pdf", ".docx"}:
            continue
        report_index += 1
        path = Path(str(file_record.get("file_path", "")))
        if extension == ".docx":
            pages, source_warnings = _extract_embedded_docx_text(path, source_label="docx final report")
            rows.extend(build_anchor_inventory_rows(report_index, pages, source_tier="final_report_docx", source_type="docx"))
        else:
            pages, source_warnings = _extract_embedded_pdf_text(path)
            rows.extend(build_anchor_inventory_rows(report_index, pages, source_tier="final_report_pdf", source_type="pdf"))
            companion_pages, companion_warnings = _extract_companion_docx_pages(companion_docx_by_report.get(str(file_record.get("file_id")), ()))
            rows.extend(
                build_anchor_inventory_rows(
                    report_index,
                    companion_pages,
                    source_tier="same_order_docx_companion",
                    source_type="docx",
                )
            )
            source_warnings = source_warnings + companion_warnings
        warnings.extend(_warning_type(item) for item in source_warnings)

    row_tuple = tuple(row for row in rows if row.count > 0)
    return AnchorInventoryReport(
        inventory_version=ANCHOR_INVENTORY_VERSION,
        generated_at=datetime.now(UTC).isoformat(),
        source_intake_path=str(intake_path),
        analyzed_report_count=report_index,
        inventory_rows=row_tuple,
        aggregate_counts=_aggregate_counts(row_tuple),
        warnings=tuple(sorted(set(warnings))),
    )


def run_local_anchor_to_field_diagnostics(intake_path: str | Path) -> AnchorToFieldDiagnosticsReport:
    """Diagnose appraiser/title anchor-to-field rejection categories without raw text."""

    payload = json.loads(Path(intake_path).read_text(encoding="utf-8-sig"))
    files = tuple(dict(item) for item in payload.get("files", []))
    companion_docx_by_report = _companion_docx_by_report(files, payload.get("candidate_order_groups", []))
    diagnostics: list[AnchorToFieldDiagnostic] = []
    warnings: list[str] = []
    report_index = 0

    for file_record in files:
        if file_record.get("candidate_role") != "final_report":
            continue
        extension = str(file_record.get("extension") or "").lower()
        if extension not in {".pdf", ".docx"}:
            continue
        report_index += 1
        path = Path(str(file_record.get("file_path", "")))
        if extension == ".docx":
            pages, source_warnings = _extract_embedded_docx_text(path, source_label="docx final report")
            diagnostics.extend(
                build_anchor_to_field_diagnostics(
                    report_index,
                    pages,
                    source_tier="final_report_docx",
                    source_type="docx",
                )
            )
        else:
            pages, source_warnings = _extract_embedded_pdf_text(path)
            diagnostics.extend(
                build_anchor_to_field_diagnostics(
                    report_index,
                    pages,
                    source_tier="final_report_pdf",
                    source_type="pdf",
                )
            )
            companion_pages, companion_warnings = _extract_companion_docx_pages(companion_docx_by_report.get(str(file_record.get("file_id")), ()))
            diagnostics.extend(
                build_anchor_to_field_diagnostics(
                    report_index,
                    companion_pages,
                    source_tier="same_order_docx_companion",
                    source_type="docx",
                )
            )
            source_warnings = source_warnings + companion_warnings
        warnings.extend(_warning_type(item) for item in source_warnings)

    diagnostic_tuple = tuple(diagnostics)
    return AnchorToFieldDiagnosticsReport(
        diagnostics_version=ANCHOR_INVENTORY_VERSION,
        generated_at=datetime.now(UTC).isoformat(),
        source_intake_path=str(intake_path),
        analyzed_report_count=report_index,
        diagnostic_count=len(diagnostic_tuple),
        diagnostics=diagnostic_tuple,
        aggregate_counts=_anchor_to_field_aggregate_counts(diagnostic_tuple),
        warnings=tuple(sorted(set(warnings))),
    )


def build_anchor_inventory_rows(
    report_index: int,
    pages: Iterable[PageText],
    *,
    source_tier: str,
    source_type: str,
) -> tuple[AnchorInventoryRow, ...]:
    """Build anchor-family count rows from in-memory page text."""

    page_tuple = tuple(pages)
    total_pages = max((page.page_number for page in page_tuple), default=0)
    counters: Counter[tuple[str, str]] = Counter()
    for page in page_tuple:
        normalized = _normalize_text(page.text)
        if not normalized:
            continue
        bucket = _page_bucket(page.page_number, total_pages, source_type)
        for family, terms in ANCHOR_FAMILIES.items():
            count = sum(_term_count(normalized, term) for term in terms)
            if count:
                counters[(bucket, family)] += count
    return tuple(
        AnchorInventoryRow(
            report_index=report_index,
            source_tier=source_tier,
            source_type=source_type,
            page_bucket=bucket,
            anchor_family=family,
            count=count,
        )
        for (bucket, family), count in sorted(counters.items())
    )


def build_anchor_to_field_diagnostics(
    report_index: int,
    pages: Iterable[PageText],
    *,
    source_tier: str,
    source_type: str,
) -> tuple[AnchorToFieldDiagnostic, ...]:
    """Build redacted diagnostics for appraiser/title anchors near candidate lines."""

    page_tuple = tuple(pages)
    total_pages = max((page.page_number for page in page_tuple), default=0)
    diagnostics: list[AnchorToFieldDiagnostic] = []
    for page in page_tuple:
        lines = [_clean_line(line) for line in page.text.splitlines() if _clean_line(line)]
        page_bucket = _page_bucket(page.page_number, total_pages, source_type)
        for index, line in enumerate(lines):
            normalized = _normalize_text(line)
            if any(phrase in normalized for phrase in APPRAISER_CREDENTIAL_PHRASES) or "appraiser" in normalized:
                candidate = _nearby_appraiser_candidate(lines, index)
                reason = _appraiser_rejection_reason(candidate)
                diagnostics.append(
                    AnchorToFieldDiagnostic(
                        report_index=report_index,
                        field_name="appraiser_name",
                        anchor_family="appraiser_signature_certification",
                        source_tier=source_tier,
                        source_type=source_type,
                        page_bucket=page_bucket,
                        nearby_candidate_shape=_candidate_shape(candidate),
                        candidate_length_bucket=_length_bucket(len(candidate or "")),
                        rejection_reason=reason,
                        provenance_method="nearby appraiser anchor",
                    )
                )
            if any(phrase in normalized for phrase in REPORT_TITLE_PHRASES):
                candidate = _nearby_title_candidate(lines, index)
                reason = _title_rejection_reason(candidate)
                diagnostics.append(
                    AnchorToFieldDiagnostic(
                        report_index=report_index,
                        field_name="report_title",
                        anchor_family="report_title_title_block",
                        source_tier=source_tier,
                        source_type=source_type,
                        page_bucket=page_bucket,
                        nearby_candidate_shape=_candidate_shape(candidate),
                        candidate_length_bucket=_length_bucket(len(candidate or "")),
                        rejection_reason=reason,
                        provenance_method="nearby title anchor",
                    )
                )
    return tuple(diagnostics)


def render_anchor_inventory_markdown(report: AnchorInventoryReport) -> str:
    """Render anchor inventory without raw source text."""

    lines = [
        "# Privacy-Safe Anchor Inventory",
        "",
        "This local-only report inventories anchor-family counts in searchable text. It does not include report snippets, extracted values, file names, paths, client names, appraiser names, reviewer names, or source document text.",
        "",
        "## Totals",
        "",
        f"- Candidate final reports analyzed: {report.analyzed_report_count}",
        f"- Anchor count rows: {len(report.inventory_rows)}",
        "",
        "## Aggregate Counts",
        "",
    ]
    for label, counts in report.aggregate_counts.items():
        lines.append(f"### {label.replace('_', ' ').title()}")
        lines.extend(_markdown_count_lines(counts))
        lines.append("")
    lines.extend(["## Inventory Rows", ""])
    if not report.inventory_rows:
        lines.append("- None")
    for row in report.inventory_rows:
        lines.append(
            "- "
            f"report_index={row.report_index}; "
            f"tier={row.source_tier}; "
            f"type={row.source_type}; "
            f"bucket={row.page_bucket}; "
            f"family={row.anchor_family}; "
            f"count={row.count}"
        )
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in report.warnings) if report.warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def render_anchor_to_field_diagnostics_markdown(report: AnchorToFieldDiagnosticsReport) -> str:
    """Render anchor-to-field diagnostics without snippets or raw candidate values."""

    lines = [
        "# Privacy-Safe Anchor-to-Field Diagnostics",
        "",
        "This local-only report diagnoses appraiser_name and report_title anchors. It contains no snippets, raw names, titles, file names, paths, or source text.",
        "",
        "## Totals",
        "",
        f"- Candidate final reports analyzed: {report.analyzed_report_count}",
        f"- Diagnostic rows: {report.diagnostic_count}",
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
            f"field={item.field_name}; "
            f"family={item.anchor_family}; "
            f"tier={item.source_tier}; "
            f"type={item.source_type}; "
            f"bucket={item.page_bucket}; "
            f"shape={item.nearby_candidate_shape}; "
            f"length={item.candidate_length_bucket}; "
            f"reason={item.rejection_reason}; "
            f"method={item.provenance_method}"
        )
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in report.warnings) if report.warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_anchor_inventory_outputs(
    report: AnchorInventoryReport,
    output_directory: str | Path,
    *,
    basename: str = OUTPUT_BASENAME,
) -> dict[str, str]:
    """Save privacy-safe inventory outputs under an ignored local folder."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / f"{basename}.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_anchor_inventory_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def save_anchor_to_field_diagnostics_outputs(
    report: AnchorToFieldDiagnosticsReport,
    output_directory: str | Path,
    *,
    basename: str = ANCHOR_TO_FIELD_BASENAME,
) -> dict[str, str]:
    """Save privacy-safe anchor-to-field diagnostics under an ignored local folder."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / f"{basename}.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_anchor_to_field_diagnostics_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _aggregate_counts(rows: Iterable[AnchorInventoryRow]) -> dict[str, dict[str, int]]:
    row_tuple = tuple(rows)
    return {
        "anchor_family": _counter_to_dict(Counter(row.anchor_family for row in row_tuple for _ in range(row.count))),
        "source_tier": _counter_to_dict(Counter(row.source_tier for row in row_tuple for _ in range(row.count))),
        "source_type": _counter_to_dict(Counter(row.source_type for row in row_tuple for _ in range(row.count))),
        "page_bucket": _counter_to_dict(Counter(row.page_bucket for row in row_tuple for _ in range(row.count))),
        "report_index": _counter_to_dict(Counter(str(row.report_index) for row in row_tuple for _ in range(row.count))),
    }


def _anchor_to_field_aggregate_counts(items: Iterable[AnchorToFieldDiagnostic]) -> dict[str, dict[str, int]]:
    item_tuple = tuple(items)
    return {
        "field_name": _counter_to_dict(Counter(item.field_name for item in item_tuple)),
        "rejection_reason": _counter_to_dict(Counter(item.rejection_reason for item in item_tuple)),
        "anchor_family": _counter_to_dict(Counter(item.anchor_family for item in item_tuple)),
        "source_tier": _counter_to_dict(Counter(item.source_tier for item in item_tuple)),
        "source_type": _counter_to_dict(Counter(item.source_type for item in item_tuple)),
        "page_bucket": _counter_to_dict(Counter(item.page_bucket for item in item_tuple)),
        "candidate_shape": _counter_to_dict(Counter(item.nearby_candidate_shape for item in item_tuple)),
        "candidate_length_bucket": _counter_to_dict(Counter(item.candidate_length_bucket for item in item_tuple)),
        "provenance_method": _counter_to_dict(Counter(item.provenance_method for item in item_tuple)),
    }


def _nearby_appraiser_candidate(lines: tuple[str, ...] | list[str], index: int) -> str | None:
    for candidate in reversed(lines[max(0, index - 4) : index]):
        cleaned = _clean_line(candidate)
        if _line_is_structural(cleaned):
            continue
        return cleaned
    for candidate in lines[index + 1 : index + 3]:
        cleaned = _clean_line(candidate)
        if _line_is_structural(cleaned):
            continue
        return cleaned
    return None


def _nearby_title_candidate(lines: tuple[str, ...] | list[str], index: int) -> str | None:
    line = _clean_line(lines[index])
    if index > 0:
        previous = _clean_line(lines[index - 1])
        combined = _clean_line(f"{previous} {line}")
        if len(previous) <= 80 and not _line_is_structural(previous):
            return combined
    return line


def _appraiser_rejection_reason(candidate: str | None) -> str:
    if not candidate:
        return "no_nearby_candidate"
    if len(candidate) > 90:
        return "candidate_too_long"
    if _looks_like_company_or_title(candidate):
        return "company_or_title_not_person"
    if not _is_plausible_person_name(candidate):
        return "failed_person_name_validation"
    return "accepted_candidate_shape"


def _title_rejection_reason(candidate: str | None) -> str:
    if not candidate:
        return "no_nearby_candidate"
    if len(candidate) > 120:
        return "candidate_too_long"
    if _normalize_text(candidate) in GENERIC_TITLE_VALUES:
        return "title_candidate_too_generic"
    if not any(phrase in _normalize_text(candidate) for phrase in REPORT_TITLE_PHRASES):
        return "failed_title_phrase_validation"
    return "accepted_candidate_shape"


def _candidate_shape(candidate: str | None) -> str:
    if not candidate:
        return "missing"
    if len(candidate) > 120:
        return "long-text"
    if _is_plausible_person_name(candidate):
        return "person-like"
    if _looks_like_company_or_title(candidate):
        return "company-or-title"
    if any(phrase in _normalize_text(candidate) for phrase in REPORT_TITLE_PHRASES):
        return "title-like"
    return "short-text"


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


def _looks_like_company_or_title(value: str) -> bool:
    normalized = _normalize_text(value)
    tokens = set(re.findall(r"[a-z]+", normalized))
    return bool(tokens.intersection(COMPANY_OR_TITLE_TERMS))


def _line_is_structural(value: str) -> bool:
    normalized = _normalize_text(value)
    if not normalized:
        return True
    if normalized in {"signed", "signed by", "prepared by", "respectfully submitted", "submitted by", "sincerely"}:
        return True
    if any(phrase == normalized for phrase in APPRAISER_CREDENTIAL_PHRASES):
        return True
    return False


def _clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" :-\t")[:160]


def _page_bucket(page_number: int, total_pages: int, source_type: str) -> str:
    if source_type == "docx":
        return "document"
    if page_number <= 1:
        return "first_page"
    if page_number <= 3:
        return "early_pages"
    if total_pages and page_number > max(3, total_pages - 3):
        return "late_pages"
    return "middle_pages"


def _term_count(text: str, term: str) -> int:
    normalized_term = _normalize_text(term)
    return len(re.findall(rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])", text))


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _warning_type(value: str) -> str:
    normalized = _normalize_text(value)
    if "pypdf is not installed" in normalized:
        return "pdf_text_library_missing"
    if "python-docx is not installed" in normalized:
        return "docx_text_library_missing"
    if "no embedded" in normalized or "no searchable" in normalized:
        return "no_searchable_text"
    if "path does not exist" in normalized:
        return "source_path_missing"
    return "text_extraction_warning"


def _counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted((key, int(value)) for key, value in counter.items()))


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
