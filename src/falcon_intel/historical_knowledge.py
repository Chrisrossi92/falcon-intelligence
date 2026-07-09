"""Local-only deterministic metadata extraction for historical final reports.

This module is Phase 1 metadata extraction only. It reads likely final report
PDF/DOCX files and same-order DOCX companions identified by the historical
intake inventory, extracts embedded text only when locally available, and never
OCRs, uploads, modifies, or stores full report text.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any, Iterable


CONFIDENCE_LABELS = {"high", "medium", "low", "missing", "conflicting"}
OUTPUT_VERSION = "1"
PYPDF_MISSING_WARNING = (
    "pypdf is not installed; install optional local PDF support with "
    'python -m pip install -e ".[pdf]"; embedded PDF text extraction was skipped'
)
PYTHON_DOCX_MISSING_WARNING = (
    "python-docx is not installed; install optional local DOCX support with "
    'python -m pip install -e ".[docx]"; embedded DOCX text extraction was skipped'
)
DEFAULT_FIELDS = (
    "report_title",
    "report_type",
    "property_address",
    "property_type",
    "client",
    "intended_user",
    "intended_use",
    "effective_date",
    "report_date",
    "inspection_date",
    "appraiser_name",
    "reviewer_name",
)

LABEL_PATTERNS: dict[str, tuple[str, ...]] = {
    "property_address": (
        "Property Address",
        "Subject Property",
        "Subject Property Address",
        "Subject Address",
        "Property Identification",
        "Property Location",
        "Address of Property",
        "Location of Property",
    ),
    "property_type": (
        "Property Type",
        "Property Description",
        "Property Interest Appraised",
        "Property Classification",
        "Type of Property",
    ),
    "client": ("Client", "Client Name"),
    "intended_user": ("Intended User", "Intended Users"),
    "intended_use": ("Intended Use",),
    "effective_date": ("Effective Date", "Effective Date of Value", "Date of Value", "Valuation Date"),
    "report_date": ("Report Date", "Date of Report"),
    "inspection_date": (
        "Date of Inspection",
        "Inspection Date",
        "Inspection",
        "Date Inspected",
        "Inspected",
        "Property Inspection Date",
        "Date of Property Inspection",
        "Site Inspection Date",
        "Date of Site Inspection",
        "Site Visit Date",
        "Date of Site Visit",
        "Property Visit Date",
        "Date Viewed",
    ),
    "appraiser_name": (
        "Appraiser",
        "Appraiser Name",
        "Prepared By",
        "Report Prepared By",
        "Valuation Prepared By",
        "Signing Appraiser",
        "Principal Appraiser",
        "Appraiser of Record",
        "Signed By",
    ),
    "reviewer_name": (
        "Reviewer",
        "Reviewer Name",
        "Review Appraiser",
        "Reviewed By",
        "Reviewer Appraiser",
        "Review Completed By",
        "Appraisal Reviewed By",
        "Review Prepared By",
        "Review Signed By",
    ),
}

APPROACH_PHRASES: dict[str, tuple[str, ...]] = {
    "sales_comparison_approach": ("sales comparison approach",),
    "income_approach": ("income approach", "income capitalization approach"),
    "cost_approach": ("cost approach",),
}

SECTION_PHRASES: dict[str, tuple[str, ...]] = {
    "extraordinary_assumptions_present": ("extraordinary assumptions", "extraordinary assumption"),
    "hypothetical_conditions_present": ("hypothetical conditions", "hypothetical condition"),
    "certification_section_present": (
        "certification",
        "certifications",
        "certification statement",
        "certificate of appraisal",
        "certification of appraisal",
        "certification of value",
        "appraisal certification",
        "appraiser certification",
        "appraiser's certification",
        "appraisers certification",
        "appraiser s certification",
    ),
    "limiting_conditions_section_present": ("limiting conditions", "general assumptions and limiting conditions"),
}

REPORT_TYPE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("restricted use appraisal report", "restricted appraisal report"),
    ("restricted appraisal report", "restricted appraisal report"),
    ("appraisal report", "appraisal report"),
    ("evaluation report", "evaluation report"),
)
REPORT_TITLE_PHRASES = (
    "restricted use appraisal report",
    "restricted appraisal report",
    "market value appraisal report",
    "narrative appraisal report",
    "appraisal review report",
    "appraisal report",
    "valuation report",
    "evaluation report",
)
GENERIC_REPORT_TITLE_VALUES = {
    "appraisal report",
    "real estate appraisal report",
    "valuation report",
    "evaluation report",
}
DATE_RE = re.compile(
    r"\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+(?:19|20)\d{2}|"
    r"\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2}|(?:19|20)\d{2})\b",
    re.I,
)
ADDRESS_RE = re.compile(
    r"\b\d{2,6}\s+[a-z0-9][a-z0-9 .'-]*(?:street|st|avenue|ave|road|rd|drive|dr|"
    r"lane|ln|court|ct|boulevard|blvd|way|loop|parkway|pkwy|circle|cir|"
    r"highway|hwy|place|pl|terrace|ter|trail|square|sq)\b",
    re.I,
)
PERSON_RE = re.compile(r"^[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){1,4}(?:,?\s+[A-Z]{2,8})?$")
PERSON_SUFFIX_RE = re.compile(r"^[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){1,4}(?:,\s*(?:MAI|AI-GRS|SRA|ASA|CRE|MRICS)){1,3}$")
AMBIGUOUS_PERSON_TAILS = {
    "certification",
    "independence",
    "statement",
    "limiting",
    "conditions",
    "assumptions",
    "report",
    "certify",
}
SIGNATURE_NOISE_TERMS = {
    "address",
    "appraisal",
    "appraisals",
    "associates",
    "avenue",
    "boulevard",
    "certification",
    "company",
    "corp",
    "corporation",
    "drive",
    "email",
    "estate",
    "fax",
    "group",
    "inc",
    "license",
    "llc",
    "management",
    "partners",
    "phone",
    "realty",
    "road",
    "services",
    "street",
    "valuation",
}
SALIENT_FACTS_HEADINGS = (
    "summary of salient facts",
    "salient facts",
    "summary of important facts",
    "important facts and conclusions",
)
SECTION_STOP_HEADINGS = (
    "scope of work",
    "area data",
    "neighborhood",
    "market trend",
    "zoning",
    "site description",
    "building improvement",
    "analysis and conclusions",
    "highest and best use",
    "sales comparison approach",
    "income approach",
    "cost approach",
    "reconciliation",
    "certification",
    "assumptions and limiting conditions",
)
TRANSMITTAL_HEADINGS = (
    "letter of transmittal",
    "transmittal letter",
)
CERTIFICATION_SIGNATURE_HEADINGS = (
    "certification of appraisal",
    "appraiser certification",
    "appraiser's certification",
    "appraisal certification",
    "appraiser s certification",
    "certification",
)
REVIEW_SIGNATURE_HEADINGS = (
    "review certification",
    "appraisal review",
    "review appraiser",
)
SIGNATURE_SECTION_STOP_HEADINGS = (
    "assumptions and limiting conditions",
    "limiting conditions",
    "addenda",
    "exhibits",
    "qualifications",
    "sales comparison approach",
    "income approach",
    "cost approach",
)
INSPECTION_ANCHOR_TERMS = (
    "inspected",
    "inspection",
    "site visit",
    "site inspection",
    "property visit",
    "observed",
    "viewed",
)
APPRAISER_CREDENTIAL_PHRASES = (
    "certified general real estate appraiser",
    "state certified general appraiser",
    "state-certified general appraiser",
    "state certified general appraiser",
    "state certified general real estate appraiser",
    "state-certified general real estate appraiser",
    "certified residential real estate appraiser",
    "licensed real estate appraiser",
    "real estate appraiser",
    "state certified general appraiser",
    "certified general appraiser",
)
REVIEW_SECTION_PHRASES = (
    "appraisal review",
    "review appraiser",
    "reviewed by",
    "review certification",
)
SIGNATURE_SKIP_LINES = {
    "respectfully submitted",
    "submitted by",
    "sincerely",
    "certification of appraisal",
    "appraiser certification",
    "appraiser's certification",
    "appraisal certification",
}


@dataclass(frozen=True)
class PageText:
    """Embedded text from one local source page or document chunk."""

    page_number: int
    text: str
    source_label: str | None = None


@dataclass(frozen=True)
class MetadataCandidate:
    """One candidate metadata value with simple confidence and provenance."""

    value: str | None
    confidence: str
    extraction_method: str
    source_hint: str | None = None
    warning: str | None = None


@dataclass(frozen=True)
class HistoricalReportKnowledgeCandidate:
    """Phase 1 metadata candidates for one likely final report."""

    file_id: str
    file_path: str
    file_name: str
    extraction_status: str
    fields: dict[str, tuple[MetadataCandidate, ...]]
    approaches_referenced: dict[str, MetadataCandidate]
    sections_detected: dict[str, MetadataCandidate]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class HistoricalKnowledgeReport:
    """Complete local historical knowledge extraction output."""

    knowledge_version: str
    generated_at: str
    source_inventory_path: str
    report_candidates: tuple[HistoricalReportKnowledgeCandidate, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_version": self.knowledge_version,
            "generated_at": self.generated_at,
            "source_inventory_path": self.source_inventory_path,
            "report_candidates": [asdict(candidate) for candidate in self.report_candidates],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "summary": build_historical_knowledge_summary(self),
        }


def extract_report_metadata_from_pages(
    pages: Iterable[PageText],
    *,
    file_id: str = "synthetic-final-report",
    file_path: str = "synthetic/final-report.pdf",
    file_name: str = "final-report.pdf",
) -> HistoricalReportKnowledgeCandidate:
    """Extract deterministic metadata candidates from embedded/searchable text."""

    page_list = tuple(pages)
    warnings: list[str] = []
    if not any(page.text.strip() for page in page_list):
        warnings.append("No embedded/searchable text was available; OCR was not attempted.")
        return HistoricalReportKnowledgeCandidate(
            file_id=file_id,
            file_path=file_path,
            file_name=file_name,
            extraction_status="no_searchable_text",
            fields={field: (_missing_candidate("missing embedded searchable text"),) for field in DEFAULT_FIELDS},
            approaches_referenced=_detect_presence({}, APPROACH_PHRASES, {}),
            sections_detected=_detect_presence({}, SECTION_PHRASES, {}),
            warnings=tuple(warnings),
        )

    field_candidates: dict[str, tuple[MetadataCandidate, ...]] = {}
    field_candidates["report_title"] = _extract_report_title(page_list)
    field_candidates["report_type"] = _extract_report_type(page_list)

    for field, labels in LABEL_PATTERNS.items():
        field_candidates[field] = _extract_labeled_candidates(page_list, labels, field)

    section_candidates = _extract_section_level_candidates(page_list)
    for field, candidates in section_candidates.items():
        field_candidates[field] = _merge_candidates(field_candidates.get(field, ()), candidates)

    searchable_by_page = {page.page_number: _normalize_text(page.text) for page in page_list}
    source_hints_by_page = {page.page_number: _page_source_hint(page) for page in page_list}
    return HistoricalReportKnowledgeCandidate(
        file_id=file_id,
        file_path=file_path,
        file_name=file_name,
        extraction_status="extracted",
        fields=field_candidates,
        approaches_referenced=_detect_presence(searchable_by_page, APPROACH_PHRASES, source_hints_by_page),
        sections_detected=_detect_presence(searchable_by_page, SECTION_PHRASES, source_hints_by_page),
        warnings=tuple(warnings),
    )


def run_historical_knowledge_extraction(
    intake_inventory_path: str | Path,
) -> HistoricalKnowledgeReport:
    """Run Phase 1 extraction from an ignored historical intake inventory JSON."""

    inventory_path = Path(intake_inventory_path)
    payload = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    warnings: list[str] = []
    errors: list[str] = []
    candidates: list[HistoricalReportKnowledgeCandidate] = []

    files = tuple(dict(item) for item in payload.get("files", []))
    companion_docx_by_report = _companion_docx_by_report(files, payload.get("candidate_order_groups", []))

    for file_record in files:
        if file_record.get("candidate_role") != "final_report":
            continue
        extension = str(file_record.get("extension") or "").lower()
        if extension not in {".pdf", ".docx"}:
            warnings.append(f"Skipped unsupported likely final report: {file_record.get('file_id')}")
            continue

        file_path = Path(str(file_record.get("file_path", "")))
        pages: tuple[PageText, ...]
        source_warnings: tuple[str, ...]
        if extension == ".docx":
            pages, source_warnings = _extract_embedded_docx_text(file_path, source_label=f"docx final report: {file_record.get('file_id')}")
        else:
            pages, source_warnings = _extract_embedded_pdf_text(file_path)
            companion_pages, companion_warnings = _extract_companion_docx_pages(companion_docx_by_report.get(str(file_record.get("file_id")), ()))
            pages = pages + companion_pages
            source_warnings = source_warnings + companion_warnings

        warnings.extend(f"{file_record.get('file_id')}: {warning}" for warning in source_warnings)
        candidate = extract_report_metadata_from_pages(
                pages,
                file_id=str(file_record.get("file_id", "")),
                file_path=str(file_record.get("file_path", "")),
                file_name=str(file_record.get("file_name", "")),
            )
        candidates.append(_augment_from_intake_metadata(candidate, file_record))

    return HistoricalKnowledgeReport(
        knowledge_version=OUTPUT_VERSION,
        generated_at=datetime.now(UTC).isoformat(),
        source_inventory_path=str(inventory_path),
        report_candidates=tuple(candidates),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def build_historical_knowledge_summary(report: HistoricalKnowledgeReport) -> dict[str, Any]:
    """Build a compact summary without report text."""

    statuses = Counter(candidate.extraction_status for candidate in report.report_candidates)
    field_confidence = Counter()
    for candidate in report.report_candidates:
        for values in candidate.fields.values():
            for value in values:
                field_confidence[value.confidence] += 1

    return {
        "total_report_candidates": len(report.report_candidates),
        "extraction_status_breakdown": dict(sorted(statuses.items())),
        "field_confidence_breakdown": dict(sorted(field_confidence.items())),
        "warnings": list(report.warnings),
        "errors": list(report.errors),
    }


def render_historical_knowledge_summary(report: HistoricalKnowledgeReport) -> str:
    """Render a human-readable summary without copied report text."""

    summary = build_historical_knowledge_summary(report)
    lines = [
        "# Historical Knowledge Extraction Summary",
        "",
        "This local output contains deterministic metadata candidates only. It does not store full report text, OCR output, AI analysis, embeddings, uploads, or production records.",
        "",
        "## Totals",
        "",
        f"- Report candidates considered: {summary['total_report_candidates']}",
        "",
        "## Extraction Status",
        "",
    ]
    lines.extend(_markdown_count_lines(summary["extraction_status_breakdown"]))
    lines.extend(["", "## Field Confidence", ""])
    lines.extend(_markdown_count_lines(summary["field_confidence_breakdown"]))
    lines.extend(["", "## Candidate Reports", ""])
    if report.report_candidates:
        for candidate in report.report_candidates:
            lines.append(f"- {candidate.file_id}: {candidate.extraction_status}; warnings={len(candidate.warnings)}")
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings / Errors", ""])
    warnings = list(report.warnings) + list(report.errors)
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_historical_knowledge_outputs(
    report: HistoricalKnowledgeReport,
    output_directory: str | Path,
    *,
    basename: str = "historical-knowledge-report",
) -> dict[str, str]:
    """Save ignored JSON and Markdown output files."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / "historical-knowledge-summary.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_historical_knowledge_summary(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _extract_report_title(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    first_page_title = _extract_first_page_title_block(pages)
    if first_page_title:
        return first_page_title
    for page in pages:
        if page.page_number > 3 and not page.source_label:
            continue
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        for line in lines[:20]:
            normalized = _normalize_text(line)
            if any(phrase in normalized for phrase in REPORT_TITLE_PHRASES):
                return (
                    MetadataCandidate(
                        value=_clean_value(line),
                        confidence="medium",
                        extraction_method="deterministic title phrase",
                        source_hint=_page_source_hint(page),
                    ),
                )
    document_title = _extract_document_title_anchor(pages)
    if document_title:
        return document_title
    return (_missing_candidate("report title not found"),)


def _extract_first_page_title_block(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    if not pages:
        return ()
    page = pages[0]
    lines = [_clean_value(line) for line in page.text.splitlines() if _clean_value(line)]
    for index, line in enumerate(lines[:16]):
        normalized = _normalize_text(line)
        if "report" in normalized and index > 0:
            previous = _clean_value(lines[index - 1])
            combined = _clean_value(f"{previous} {line}")
            combined_normalized = _normalize_text(combined)
            if any(phrase in combined_normalized for phrase in REPORT_TITLE_PHRASES):
                return (
                    MetadataCandidate(
                        value=combined,
                        confidence="medium",
                        extraction_method="first page title block: split-line deterministic title phrase",
                        source_hint=_anchored_source_hint(page, "first page title block"),
                    ),
                )
        if any(phrase in normalized for phrase in REPORT_TITLE_PHRASES):
            return (
                MetadataCandidate(
                    value=line,
                    confidence="medium",
                    extraction_method="first page title block: deterministic title phrase",
                    source_hint=_anchored_source_hint(page, "first page title block"),
                ),
            )
    return ()


def _extract_document_title_anchor(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    for page in pages:
        lines = [_clean_value(line) for line in page.text.splitlines() if _clean_value(line)]
        for index, line in enumerate(lines[:40]):
            candidate = _report_title_candidate_from_lines(lines, index)
            if candidate and not _is_generic_report_title(candidate):
                return (
                    MetadataCandidate(
                        value=candidate,
                        confidence="medium",
                        extraction_method="document title anchor: non-generic title phrase",
                        source_hint=_anchored_source_hint(page, "document title anchor"),
                    ),
                )
    return ()


def _report_title_candidate_from_lines(lines: list[str], index: int) -> str | None:
    line = _clean_value(lines[index])
    normalized = _normalize_text(line)
    if index > 0:
        previous = _clean_value(lines[index - 1])
        combined = _clean_value(f"{previous} {line}")
        combined_normalized = _normalize_text(combined)
        if any(phrase in combined_normalized for phrase in REPORT_TITLE_PHRASES):
            return combined
    if any(phrase in normalized for phrase in REPORT_TITLE_PHRASES):
        return line
    return None


def _is_generic_report_title(value: str) -> bool:
    return _normalize_text(value) in GENERIC_REPORT_TITLE_VALUES


def _extract_report_type(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    first_pages = _normalize_text("\n".join(page.text for page in pages[:3]))
    for phrase, value in REPORT_TYPE_PATTERNS:
        if phrase in first_pages:
            return (
                    MetadataCandidate(
                        value=value,
                        confidence="high",
                        extraction_method="deterministic report type phrase",
                        source_hint=_multi_page_source_hint(pages[:3], "first three pages"),
                    ),
                )
    return (_missing_candidate("report type not found"),)


def _extract_labeled_candidates(
    pages: tuple[PageText, ...],
    labels: tuple[str, ...],
    field_name: str,
) -> tuple[MetadataCandidate, ...]:
    candidates: list[MetadataCandidate] = []
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines()]
        for index, line in enumerate(lines):
            for label in labels:
                value = _value_after_label(line, label, field_name)
                if value is None and _line_is_label(line, label):
                    value = _next_nonempty_line(lines, index + 1)
                value = _clean_labeled_field_value(field_name, value)
                if value:
                    candidates.append(
                        MetadataCandidate(
                            value=value,
                            confidence="high",
                            extraction_method=f"deterministic label match: {label}",
                            source_hint=_page_source_hint(page),
                        )
                    )

    if not candidates:
        return (_missing_candidate(f"{field_name} not found"),)
    return _mark_conflicts(candidates)


def _extract_section_level_candidates(pages: tuple[PageText, ...]) -> dict[str, tuple[MetadataCandidate, ...]]:
    candidates: dict[str, tuple[MetadataCandidate, ...]] = {}
    salient_lines = _extract_section_lines(pages, SALIENT_FACTS_HEADINGS, SECTION_STOP_HEADINGS, max_lines=80)
    if salient_lines:
        for field, labels in LABEL_PATTERNS.items():
            values = _extract_labeled_candidates_from_lines(
                salient_lines,
                labels,
                field,
                extraction_method_prefix="summary of salient facts table",
            )
            if values:
                candidates[field] = values

    inspection = _extract_inspection_anchor_candidates(pages)
    if inspection:
        candidates["inspection_date"] = _merge_candidates(candidates.get("inspection_date", ()), inspection)
    transmittal = _extract_transmittal_candidates(pages)
    for field, values in transmittal.items():
        if field == "appraiser_name" and not _field_is_missing(candidates.get("appraiser_name", ())):
            continue
        candidates[field] = _merge_candidates(candidates.get(field, ()), values)
    certification_appraiser = _extract_certification_signature_candidates(pages)
    if certification_appraiser and _field_is_missing(candidates.get("appraiser_name", ())):
        candidates["appraiser_name"] = _merge_candidates(candidates.get("appraiser_name", ()), certification_appraiser)
    review_signature = _extract_review_signature_candidates(pages)
    if review_signature:
        candidates["reviewer_name"] = _merge_candidates(candidates.get("reviewer_name", ()), review_signature)
    appraiser = _extract_appraiser_signature_candidates(pages)
    if appraiser and _field_is_missing(candidates.get("appraiser_name", ())):
        candidates["appraiser_name"] = _merge_candidates(candidates.get("appraiser_name", ()), appraiser)
    reviewer = _extract_reviewer_candidates(pages)
    if reviewer:
        candidates["reviewer_name"] = _merge_candidates(candidates.get("reviewer_name", ()), reviewer)
    return candidates


def _extract_inspection_anchor_candidates(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    candidates: list[MetadataCandidate] = []
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        for line in lines:
            normalized = _normalize_text(line)
            if not any(term in normalized for term in INSPECTION_ANCHOR_TERMS):
                continue
            value = _clean_field_value("inspection_date", line)
            if value:
                candidates.append(
                    MetadataCandidate(
                        value=value,
                        confidence="medium",
                        extraction_method="inspection anchor: sentence date match",
                        source_hint=_anchored_source_hint(page, "inspection anchor"),
                    )
                )
    return _mark_conflicts(candidates) if candidates else ()


def _extract_transmittal_candidates(pages: tuple[PageText, ...]) -> dict[str, tuple[MetadataCandidate, ...]]:
    lines = _extract_section_lines(pages, TRANSMITTAL_HEADINGS, SIGNATURE_SECTION_STOP_HEADINGS, max_lines=60)
    if not lines:
        return {}
    output: dict[str, tuple[MetadataCandidate, ...]] = {}
    inspection_candidates: list[MetadataCandidate] = []
    appraiser_candidates: list[MetadataCandidate] = []
    raw_lines = [line for _, line in lines]
    for index, (page_number, line) in enumerate(lines):
        normalized = _normalize_text(line)
        if any(term in normalized for term in INSPECTION_ANCHOR_TERMS):
            value = _clean_field_value("inspection_date", line)
            if value:
                inspection_candidates.append(
                    MetadataCandidate(
                        value=value,
                        confidence="medium",
                        extraction_method="transmittal section: inspection anchor",
                        source_hint=f"page {page_number}; transmittal section",
                    )
                )
        if any(phrase in normalized for phrase in APPRAISER_CREDENTIAL_PHRASES):
            names = _signature_person_candidates(raw_lines, index)
            for name in names:
                appraiser_candidates.append(
                    MetadataCandidate(
                        value=name,
                        confidence="medium",
                        extraction_method="transmittal section: segmented appraiser signature anchor",
                        source_hint=f"page {page_number}; transmittal section",
                    )
                )
    if inspection_candidates:
        output["inspection_date"] = _mark_conflicts(inspection_candidates)
    if appraiser_candidates:
        output["appraiser_name"] = _safe_signature_candidates(appraiser_candidates)
    return output


def _extract_certification_signature_candidates(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    lines = _extract_section_lines(pages, CERTIFICATION_SIGNATURE_HEADINGS, SIGNATURE_SECTION_STOP_HEADINGS, max_lines=80)
    if not lines:
        return ()
    candidates: list[MetadataCandidate] = []
    raw_lines = [line for _, line in lines]
    for index, (page_number, line) in enumerate(lines):
        normalized = _normalize_text(line)
        if not any(phrase in normalized for phrase in APPRAISER_CREDENTIAL_PHRASES):
            continue
        names = _signature_person_candidates(raw_lines, index)
        method = "certification signature section: segmented appraiser credential anchor"
        for name in names:
            candidates.append(
                MetadataCandidate(
                    value=name,
                    confidence="medium",
                    extraction_method=method,
                    source_hint=f"page {page_number}; certification signature section",
                )
            )
    return _safe_signature_candidates(candidates)


def _extract_review_signature_candidates(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    lines = _extract_section_lines(pages, REVIEW_SIGNATURE_HEADINGS, SIGNATURE_SECTION_STOP_HEADINGS, max_lines=60)
    if not lines:
        return ()
    candidates: list[MetadataCandidate] = []
    raw_lines = [line for _, line in lines]
    for index, (page_number, line) in enumerate(lines):
        normalized = _normalize_text(line)
        if "review appraiser" in normalized:
            name = _clean_field_value("reviewer_name", _nearest_neighbor_person_name(raw_lines, index))
            if name:
                candidates.append(
                    MetadataCandidate(
                        value=name,
                        confidence="medium",
                        extraction_method="review signature section: review appraiser anchor",
                        source_hint=f"page {page_number}; review signature section",
                    )
                )
                continue
        if normalized.startswith("review signed") or normalized.startswith("reviewed by"):
            value = _clean_field_value("reviewer_name", _next_nonempty_line(raw_lines, index + 1))
            if value:
                candidates.append(
                    MetadataCandidate(
                        value=value,
                        confidence="medium",
                        extraction_method="review signature section: reviewed-by anchor",
                        source_hint=f"page {page_number}; review signature section",
                    )
                )
    return _safe_signature_candidates(candidates)


def _safe_signature_candidates(candidates: list[MetadataCandidate]) -> tuple[MetadataCandidate, ...]:
    if not candidates:
        return ()
    unique_values = {_normalize_text(candidate.value or "") for candidate in candidates if candidate.value}
    if len(unique_values) > 1:
        return ()
    return tuple(candidates[:3])


def _extract_labeled_candidates_from_lines(
    lines: tuple[tuple[int, str], ...],
    labels: tuple[str, ...],
    field_name: str,
    *,
    extraction_method_prefix: str,
) -> tuple[MetadataCandidate, ...]:
    candidates: list[MetadataCandidate] = []
    raw_lines = [line for _, line in lines]
    for index, (page_number, line) in enumerate(lines):
        for label in labels:
            value = _value_after_label(line, label, field_name)
            if value is None and _line_is_label(line, label):
                value = _next_nonempty_line(raw_lines, index + 1)
            value = _clean_labeled_field_value(field_name, value)
            if value:
                candidates.append(
                    MetadataCandidate(
                        value=value,
                        confidence="high",
                        extraction_method=f"{extraction_method_prefix}: {label}",
                        source_hint=f"page {page_number}",
                    )
                )
    return _mark_conflicts(candidates) if candidates else ()


def _extract_section_lines(
    pages: tuple[PageText, ...],
    headings: tuple[str, ...],
    stop_headings: tuple[str, ...],
    *,
    max_lines: int,
) -> tuple[tuple[int, str], ...]:
    collected: list[tuple[int, str]] = []
    in_section = False
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        for line in lines:
            normalized = _normalize_text(line)
            if not in_section and any(heading in normalized for heading in headings):
                in_section = True
                continue
            if not in_section:
                continue
            if collected and any(heading in normalized for heading in stop_headings):
                return tuple(collected[:max_lines])
            collected.append((page.page_number, line))
            if len(collected) >= max_lines:
                return tuple(collected)
    return tuple(collected)


def _extract_appraiser_signature_candidates(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    candidates: list[MetadataCandidate] = []
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        for index, line in enumerate(lines):
            normalized = _normalize_text(line)
            if not any(phrase in normalized for phrase in APPRAISER_CREDENTIAL_PHRASES):
                continue
            if "review appraiser" in normalized:
                continue
            names = _signature_person_candidates(lines, index)
            method = "signature block: segmented appraiser credential anchor"
            for name in names:
                candidates.append(
                    MetadataCandidate(
                        value=name,
                        confidence="medium",
                        extraction_method=method,
                        source_hint=_page_source_hint(page),
                    )
                )
    return _mark_conflicts(candidates) if candidates else ()


def _extract_reviewer_candidates(pages: tuple[PageText, ...]) -> tuple[MetadataCandidate, ...]:
    candidates: list[MetadataCandidate] = []
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        for index, line in enumerate(lines):
            normalized = _normalize_text(line)
            if normalized == "reviewed by" or normalized.startswith("reviewed by "):
                value = _value_after_label(line, "Reviewed By", "reviewer_name")
                value = _clean_field_value("reviewer_name", value or _next_nonempty_line(lines, index + 1))
                if value:
                    candidates.append(
                        MetadataCandidate(
                            value=value,
                            confidence="high",
                            extraction_method="review section: reviewed by anchor",
                            source_hint=_page_source_hint(page),
                        )
                    )
                continue
            if "review appraiser" in normalized:
                value = _value_after_label(line, "Review Appraiser", "reviewer_name")
                value = _clean_field_value("reviewer_name", value or _nearest_neighbor_person_name(lines, index))
                if value:
                    candidates.append(
                        MetadataCandidate(
                            value=value,
                            confidence="medium",
                            extraction_method="review section: review appraiser anchor",
                            source_hint=_page_source_hint(page),
                        )
                    )
    return _mark_conflicts(candidates) if candidates else ()


def _detect_presence(
    searchable_by_page: dict[int, str],
    phrase_map: dict[str, tuple[str, ...]],
    source_hints_by_page: dict[int, str],
) -> dict[str, MetadataCandidate]:
    results: dict[str, MetadataCandidate] = {}
    for field, phrases in phrase_map.items():
        found_page = None
        for page_number, text in searchable_by_page.items():
            if any(phrase in text for phrase in phrases):
                found_page = page_number
                break
        if found_page is None:
            results[field] = MetadataCandidate(
                value="missing",
                confidence="missing",
                extraction_method="deterministic phrase presence",
                warning=f"{field} not detected",
            )
        else:
            results[field] = MetadataCandidate(
                value="present",
                confidence="medium",
                extraction_method="deterministic phrase presence",
                source_hint=source_hints_by_page.get(found_page, f"page {found_page}"),
            )
    return results


def _augment_from_intake_metadata(
    candidate: HistoricalReportKnowledgeCandidate,
    file_record: dict[str, Any],
) -> HistoricalReportKnowledgeCandidate:
    """Carry conservative filename/folder metadata candidates into extraction output."""

    fields = dict(candidate.fields)
    metadata_sources = {
        "property_address": ("likely_property_address", "historical intake property-address metadata"),
        "report_type": ("likely_report_type", "historical intake report-type metadata"),
        "report_date": ("likely_report_date", "historical intake report-date metadata"),
    }
    for field_name, (source_key, method) in metadata_sources.items():
        value = file_record.get(source_key)
        if not value or not _field_is_missing(fields.get(field_name, ())):
            continue
        fields[field_name] = (
            MetadataCandidate(
                value=_clean_value(str(value)),
                confidence="medium",
                extraction_method=method,
                source_hint="intake filename/folder metadata",
            ),
        )

    return HistoricalReportKnowledgeCandidate(
        file_id=candidate.file_id,
        file_path=candidate.file_path,
        file_name=candidate.file_name,
        extraction_status=candidate.extraction_status,
        fields=fields,
        approaches_referenced=candidate.approaches_referenced,
        sections_detected=candidate.sections_detected,
        warnings=candidate.warnings,
    )


def _field_is_missing(values: tuple[MetadataCandidate, ...]) -> bool:
    return not values or all(value.confidence == "missing" or value.value is None for value in values)


def _merge_candidates(
    existing: tuple[MetadataCandidate, ...],
    additional: tuple[MetadataCandidate, ...],
) -> tuple[MetadataCandidate, ...]:
    existing_values = tuple(candidate for candidate in existing if candidate.value and candidate.confidence != "missing")
    additional_values = tuple(candidate for candidate in additional if candidate.value and candidate.confidence != "missing")
    if not existing_values:
        return additional_values or existing
    if not additional_values:
        return existing
    return _mark_conflicts(list(existing_values + additional_values))


def _clean_field_value(field_name: str, value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = _clean_value(value)
    if not cleaned:
        return None
    if field_name in {"effective_date", "report_date", "inspection_date"}:
        match = DATE_RE.search(cleaned)
        return match.group(0) if match else None
    if field_name in {"appraiser_name", "reviewer_name"}:
        return cleaned if _is_plausible_person_name(cleaned) else None
    return cleaned


def _clean_labeled_field_value(field_name: str, value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = _clean_value(value)
    if not cleaned:
        return None
    if field_name in {"effective_date", "report_date", "inspection_date"}:
        match = DATE_RE.search(cleaned)
        return match.group(0) if match else None
    if field_name in {"appraiser_name", "reviewer_name"}:
        return cleaned if _is_plausible_person_name(cleaned) else None
    return cleaned


def _nearest_previous_person_name(lines: list[str], index: int) -> str | None:
    for candidate in reversed(lines[max(0, index - 4) : index]):
        cleaned = _clean_value(candidate)
        if _normalize_text(cleaned) in SIGNATURE_SKIP_LINES:
            continue
        if _is_plausible_person_name(cleaned):
            return cleaned
    return None


def _signature_person_candidates(lines: list[str], index: int) -> tuple[str, ...]:
    """Return clean person-like lines around a signature credential anchor."""

    candidates: list[str] = []
    window: list[str] = []
    window.extend(reversed(lines[max(0, index - 8) : index]))
    window.extend(lines[index + 1 : index + 5])
    for candidate in window:
        cleaned = _clean_signature_candidate(candidate)
        if not cleaned:
            continue
        if cleaned in candidates:
            continue
        candidates.append(cleaned)
        if len(candidates) >= 2:
            break
    return tuple(candidates)


def _nearest_following_person_name(lines: list[str], index: int) -> str | None:
    for candidate in lines[index + 1 : index + 4]:
        cleaned = _clean_value(candidate)
        if _normalize_text(cleaned) in SIGNATURE_SKIP_LINES:
            continue
        if _is_plausible_person_name(cleaned):
            return cleaned
    return None


def _nearest_neighbor_person_name(lines: list[str], index: int) -> str | None:
    candidates = []
    candidates.extend(reversed(lines[max(0, index - 3) : index]))
    candidates.extend(lines[index + 1 : index + 4])
    for candidate in candidates:
        cleaned = _clean_value(candidate)
        if _normalize_text(cleaned) in SIGNATURE_SKIP_LINES:
            continue
        if _is_plausible_person_name(cleaned):
            return cleaned
    return None


def _extract_embedded_pdf_text(path: Path) -> tuple[tuple[PageText, ...], tuple[str, ...]]:
    if not path.exists():
        return (), ("source PDF path does not exist",)
    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError:
        return (), (PYPDF_MISSING_WARNING,)

    warnings: list[str] = []
    pages: list[PageText] = []
    try:
        reader = PdfReader(str(path))
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(PageText(page_number=index, text=text))
    except Exception as exc:  # pragma: no cover - library-specific failures
        return (), (f"embedded PDF text extraction failed: {type(exc).__name__}",)

    if not pages:
        warnings.append("no embedded/searchable PDF text found; OCR was not attempted")
    return tuple(pages), tuple(warnings)


def _extract_embedded_docx_text(path: Path, *, source_label: str) -> tuple[tuple[PageText, ...], tuple[str, ...]]:
    if not path.exists():
        return (), ("source DOCX path does not exist",)
    try:
        from docx import Document  # type: ignore[import-not-found]
    except ImportError:
        return (), (PYTHON_DOCX_MISSING_WARNING,)

    try:
        document = Document(str(path))
        paragraphs = [_clean_value(paragraph.text) for paragraph in document.paragraphs if paragraph.text.strip()]
    except Exception as exc:  # pragma: no cover - library-specific failures
        return (), (f"embedded DOCX text extraction failed: {type(exc).__name__}",)

    if not paragraphs:
        return (), ("no embedded DOCX text found",)
    text = "\n".join(paragraphs)
    return (PageText(page_number=1, text=text, source_label=source_label),), ()


def _extract_companion_docx_pages(file_records: Iterable[dict[str, Any]]) -> tuple[tuple[PageText, ...], tuple[str, ...]]:
    pages: list[PageText] = []
    warnings: list[str] = []
    for file_record in file_records:
        file_id = str(file_record.get("file_id") or "unknown-docx")
        docx_pages, docx_warnings = _extract_embedded_docx_text(
            Path(str(file_record.get("file_path", ""))),
            source_label=f"docx companion source: {file_id}",
        )
        pages.extend(docx_pages)
        warnings.extend(f"{file_id}: {warning}" for warning in docx_warnings)
    return tuple(pages), tuple(warnings)


def _companion_docx_by_report(
    files: tuple[dict[str, Any], ...],
    candidate_order_groups: Iterable[dict[str, Any]],
) -> dict[str, tuple[dict[str, Any], ...]]:
    files_by_id = {str(item.get("file_id")): item for item in files if item.get("file_id")}
    output: dict[str, list[dict[str, Any]]] = {}

    for group in candidate_order_groups:
        group_file_ids = tuple(str(file_id) for file_id in group.get("file_ids", ()) if file_id)
        group_files = tuple(files_by_id[file_id] for file_id in group_file_ids if file_id in files_by_id)
        final_reports = tuple(item for item in group_files if item.get("candidate_role") == "final_report")
        companion_docx = tuple(
            item
            for item in group_files
            if str(item.get("extension") or "").lower() == ".docx"
            and item.get("candidate_role") in {"source_document", "draft_report", "final_report", "unknown"}
        )
        for report in final_reports:
            report_id = str(report.get("file_id"))
            output.setdefault(report_id, [])
            output[report_id].extend(item for item in companion_docx if str(item.get("file_id")) != report_id)

    for report in files:
        if report.get("candidate_role") != "final_report":
            continue
        report_id = str(report.get("file_id"))
        if report_id in output:
            continue
        report_parent = str(report.get("parent_folder") or Path(str(report.get("file_path", ""))).parent)
        output[report_id] = [
            item
            for item in files
            if str(item.get("file_id")) != report_id
            and str(item.get("extension") or "").lower() == ".docx"
            and str(item.get("parent_folder") or Path(str(item.get("file_path", ""))).parent) == report_parent
        ]

    return {report_id: tuple(_dedupe_file_records(records)) for report_id, records in output.items()}


def _dedupe_file_records(records: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for record in records:
        file_id = str(record.get("file_id") or "")
        if not file_id or file_id in seen:
            continue
        seen.add(file_id)
        deduped.append(record)
    return tuple(deduped)


def _page_source_hint(page: PageText) -> str:
    return page.source_label or f"page {page.page_number}"


def _anchored_source_hint(page: PageText, anchor: str) -> str:
    return f"{_page_source_hint(page)}; {anchor}"


def _multi_page_source_hint(pages: tuple[PageText, ...], fallback: str) -> str:
    source_labels = tuple(dict.fromkeys(page.source_label for page in pages if page.source_label))
    if source_labels:
        return ", ".join(source_labels)
    return fallback


def _value_after_label(line: str, label: str, field_name: str | None = None) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(label)}\s*(?::|\-| {{2,}}|\t+)\s*(.+?)\s*$", re.I)
    match = pattern.match(line)
    if match:
        return match.group(1)
    if not field_name:
        return None
    if field_name == "appraiser_name" and label.lower() == "appraiser":
        return None
    fallback = re.match(rf"^\s*{re.escape(label)}\s+(.+?)\s*$", line, re.I)
    if not fallback:
        return None
    value = fallback.group(1).strip()
    return value if _is_plausible_single_space_value(field_name, value) else None


def _line_is_label(line: str, label: str) -> bool:
    return bool(re.match(rf"^\s*{re.escape(label)}\s*[:\-]?\s*$", line, re.I))


def _next_nonempty_line(lines: list[str], start_index: int) -> str | None:
    for line in lines[start_index : start_index + 3]:
        if line.strip():
            return line.strip()
    return None


def _mark_conflicts(candidates: list[MetadataCandidate]) -> tuple[MetadataCandidate, ...]:
    unique_values = {_normalize_text(candidate.value or "") for candidate in candidates if candidate.value}
    if len(unique_values) <= 1:
        return tuple(candidates[:3])
    return tuple(
        MetadataCandidate(
            value=candidate.value,
            confidence="conflicting",
            extraction_method=candidate.extraction_method,
            source_hint=candidate.source_hint,
            warning="multiple conflicting candidate values detected",
        )
        for candidate in candidates[:5]
    )


def _missing_candidate(warning: str) -> MetadataCandidate:
    return MetadataCandidate(
        value=None,
        confidence="missing",
        extraction_method="deterministic pattern matching",
        warning=warning,
    )


def _clean_value(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" :-\t")
    return value[:160]


def _clean_signature_candidate(value: str) -> str | None:
    cleaned = _clean_value(value)
    if not cleaned or len(cleaned) > 90:
        return None
    normalized = _normalize_text(cleaned)
    if normalized in SIGNATURE_SKIP_LINES:
        return None
    if _looks_like_contact_or_license_line(cleaned):
        return None
    if _looks_like_company_or_address_line(cleaned):
        return None
    return cleaned if _is_plausible_person_name(cleaned) else None


def _looks_like_contact_or_license_line(value: str) -> bool:
    normalized = _normalize_text(value)
    if normalized.startswith("review signed") or normalized.startswith("reviewed by"):
        return True
    if "@" in value or re.search(r"\b(?:phone|fax|email|tel|cell|license|lic(?:ense)? no)\b", normalized):
        return True
    if re.search(r"\b\d{3}[-.)\s]\d{3}[-.\s]\d{4}\b", value):
        return True
    if re.search(r"\b(?:cg|cert|lic)[- ]?\d{3,}\b", normalized):
        return True
    return False


def _looks_like_company_or_address_line(value: str) -> bool:
    normalized = _normalize_text(value)
    tokens = set(re.findall(r"[a-z]+", normalized))
    if tokens.intersection(SIGNATURE_NOISE_TERMS):
        return True
    if ADDRESS_RE.search(value):
        return True
    return False


def _is_plausible_single_space_value(field_name: str, value: str) -> bool:
    cleaned = _clean_value(value)
    if not cleaned or len(cleaned) > 90:
        return False
    normalized = _normalize_text(cleaned)
    if field_name == "property_address":
        return bool(ADDRESS_RE.search(cleaned))
    if field_name == "inspection_date":
        return bool(DATE_RE.search(cleaned)) and "not provided" not in normalized
    if field_name in {"appraiser_name", "reviewer_name"}:
        return _is_plausible_person_name(cleaned)
    return False


def _is_plausible_person_name(value: str) -> bool:
    cleaned = _clean_value(value)
    normalized = _normalize_text(cleaned)
    tokens = set(re.findall(r"[a-z]+", normalized))
    if tokens.intersection(AMBIGUOUS_PERSON_TAILS) or tokens.intersection(SIGNATURE_NOISE_TERMS):
        return False
    return bool(PERSON_RE.match(cleaned) or PERSON_SUFFIX_RE.match(cleaned))


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
