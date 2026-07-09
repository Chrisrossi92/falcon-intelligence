"""Privacy-safe OCR/layout feasibility planning for unresolved fields.

This module does not perform OCR. It summarizes coarse extraction state so a
future OCR/layout slice can be scoped without storing report text, OCR text, or
page images.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any, Iterable

from falcon_intel.anchor_inventory import (
    ANCHOR_FAMILIES,
    AnchorInventoryReport,
    run_local_anchor_inventory,
)
from falcon_intel.historical_knowledge import (
    HistoricalKnowledgeReport,
    PageText,
    _companion_docx_by_report,
    _extract_companion_docx_pages,
    _extract_embedded_docx_text,
    _extract_embedded_pdf_text,
    run_historical_knowledge_extraction,
)
from falcon_intel.verification_engine import VerificationReport, verify_report_candidate


OCR_FEASIBILITY_VERSION = "1"
OUTPUT_BASENAME = "ocr-feasibility-report"
TARGET_FIELDS = ("inspection_date", "reviewer_name", "appraiser_name", "report_title")
FIELD_ANCHOR_FAMILIES = {
    "inspection_date": "inspection_site_visit",
    "reviewer_name": "reviewer_review",
    "appraiser_name": "appraiser_signature_certification",
    "report_title": "report_title_title_block",
}
DEFAULT_PAGE_BUCKETS = {
    "inspection_date": ("first_page", "early_pages"),
    "reviewer_name": ("late_pages", "document"),
    "appraiser_name": ("late_pages", "middle_pages", "document"),
    "report_title": ("first_page", "document"),
}


@dataclass(frozen=True)
class OCRFeasibilityRow:
    """One anonymous report-level OCR/layout feasibility row."""

    report_index: int
    candidate_final_report_count: int
    source_file_type: str
    final_report_searchable_text: str
    companion_docx_searchable_text: str
    missing_target_fields: tuple[str, ...]
    companion_docx_helped_fields: tuple[str, ...]
    field_recommendations: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class OCRFeasibilityReport:
    """Privacy-safe feasibility report for future opt-in OCR/layout work."""

    feasibility_version: str
    generated_at: str
    source_intake_path: str
    candidate_final_report_count: int
    analyzed_report_count: int
    target_fields: tuple[str, ...]
    rows: tuple[OCRFeasibilityRow, ...]
    aggregate_counts: dict[str, dict[str, int]]
    field_recommendations: dict[str, dict[str, Any]]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_local_ocr_feasibility(intake_path: str | Path) -> OCRFeasibilityReport:
    """Run local deterministic stages and return a redacted OCR feasibility report."""

    intake = _load_json(intake_path)
    knowledge_report = run_historical_knowledge_extraction(intake_path)
    verification_report = _build_verification_report(knowledge_report)
    anchor_report = run_local_anchor_inventory(intake_path)
    return build_ocr_feasibility_report(
        intake=intake,
        knowledge_report=knowledge_report.to_dict(),
        verification_report=verification_report.to_dict(),
        anchor_inventory_report=anchor_report.to_dict(),
        source_intake_path=str(intake_path),
    )


def build_ocr_feasibility_report(
    *,
    intake: dict[str, Any],
    knowledge_report: dict[str, Any],
    verification_report: dict[str, Any],
    anchor_inventory_report: dict[str, Any],
    source_intake_path: str = "",
    generated_at: str | None = None,
) -> OCRFeasibilityReport:
    """Build feasibility rows from existing privacy-safe extraction outputs."""

    generated_at = generated_at or datetime.now(UTC).isoformat()
    files = tuple(dict(item) for item in intake.get("files", []))
    final_reports = tuple(item for item in files if item.get("candidate_role") == "final_report")
    companion_docx_by_report = _companion_docx_by_report(files, intake.get("candidate_order_groups", ()))
    report_candidates = tuple(dict(item) for item in knowledge_report.get("report_candidates", []))
    facts_by_file_id = {
        str(package.get("file_id") or ""): tuple(dict(fact) for fact in package.get("facts", ()))
        for package in verification_report.get("report_facts", ())
    }
    anchor_buckets = _anchor_buckets_by_report(anchor_inventory_report.get("inventory_rows", ()))

    rows: list[OCRFeasibilityRow] = []
    for report_index, candidate in enumerate(report_candidates, start=1):
        file_id = str(candidate.get("file_id") or "")
        file_record = _file_record_for_candidate(files, candidate)
        facts = facts_by_file_id.get(file_id, ())
        rows.append(
            _build_row(
                report_index=report_index,
                candidate_final_report_count=len(final_reports),
                file_record=file_record,
                companion_records=companion_docx_by_report.get(str(candidate.get("file_id") or ""), ()),
                candidate=candidate,
                facts=facts,
                anchor_buckets=anchor_buckets.get(report_index, {}),
            )
        )

    row_tuple = tuple(rows)
    aggregate_counts = _aggregate_counts(row_tuple)
    return OCRFeasibilityReport(
        feasibility_version=OCR_FEASIBILITY_VERSION,
        generated_at=generated_at,
        source_intake_path=str(source_intake_path),
        candidate_final_report_count=len(final_reports),
        analyzed_report_count=len(row_tuple),
        target_fields=TARGET_FIELDS,
        rows=row_tuple,
        aggregate_counts=aggregate_counts,
        field_recommendations=_aggregate_field_recommendations(row_tuple),
        warnings=_privacy_warnings(knowledge_report, anchor_inventory_report),
    )


def render_ocr_feasibility_markdown(report: OCRFeasibilityReport) -> str:
    """Render feasibility output without raw report text, values, snippets, or paths."""

    lines = [
        "# Privacy-Safe OCR/Layout Feasibility",
        "",
        "This local-only report does not run OCR and does not include report text, OCR text, snippets, raw extracted values, file names, paths, or page images.",
        "",
        "## Totals",
        "",
        f"- Candidate final reports in intake: {report.candidate_final_report_count}",
        f"- Candidate final reports analyzed: {report.analyzed_report_count}",
        f"- Target fields: {', '.join(report.target_fields)}",
        "",
        "## Aggregate Counts",
        "",
    ]
    for label, counts in report.aggregate_counts.items():
        lines.append(f"### {label.replace('_', ' ').title()}")
        lines.extend(_markdown_count_lines(counts))
        lines.append("")

    lines.extend(["## Field Recommendations", ""])
    for field, payload in report.field_recommendations.items():
        buckets = ",".join(payload.get("recommended_page_buckets", ())) or "unknown"
        lines.append(
            "- "
            f"field={field}; "
            f"ocr_recommended={payload.get('ocr_recommended')}; "
            f"reason={payload.get('reason')}; "
            f"page_buckets={buckets}; "
            f"missing_reports={payload.get('missing_report_count', 0)}"
        )

    lines.extend(["", "## Report Rows", ""])
    if not report.rows:
        lines.append("- None")
    for row in report.rows:
        lines.append(
            "- "
            f"report_index={row.report_index}; "
            f"candidate_final_reports={row.candidate_final_report_count}; "
            f"source_type={row.source_file_type}; "
            f"final_searchable={row.final_report_searchable_text}; "
            f"companion_docx_searchable={row.companion_docx_searchable_text}; "
            f"missing={','.join(row.missing_target_fields) or 'none'}; "
            f"companion_helped={','.join(row.companion_docx_helped_fields) or 'none'}"
        )
        for field, payload in row.field_recommendations.items():
            buckets = ",".join(payload.get("recommended_page_buckets", ())) or "unknown"
            lines.append(
                "  - "
                f"field={field}; "
                f"ocr_recommended={payload.get('ocr_recommended')}; "
                f"reason={payload.get('reason')}; "
                f"page_buckets={buckets}"
            )

    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in report.warnings) if report.warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_ocr_feasibility_outputs(
    report: OCRFeasibilityReport,
    output_directory: str | Path,
    *,
    basename: str = OUTPUT_BASENAME,
) -> dict[str, str]:
    """Save privacy-safe feasibility JSON and Markdown under an ignored local folder."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / f"{basename}.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_ocr_feasibility_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _build_verification_report(knowledge_report: HistoricalKnowledgeReport) -> VerificationReport:
    timestamp = datetime.now(UTC).isoformat()
    payload = knowledge_report.to_dict()
    return VerificationReport(
        verification_version="1",
        generated_at=timestamp,
        source_knowledge_path="in-memory historical knowledge report",
        report_facts=tuple(verify_report_candidate(candidate, timestamp=timestamp) for candidate in payload.get("report_candidates", ())),
        warnings=tuple(str(item) for item in payload.get("warnings", ()) if item),
        errors=tuple(str(item) for item in payload.get("errors", ()) if item),
    )


def _build_row(
    *,
    report_index: int,
    candidate_final_report_count: int,
    file_record: dict[str, Any],
    companion_records: tuple[dict[str, Any], ...],
    candidate: dict[str, Any],
    facts: tuple[dict[str, Any], ...],
    anchor_buckets: dict[str, tuple[str, ...]],
) -> OCRFeasibilityRow:
    source_file_type = str(file_record.get("extension") or "").strip(".").lower() or "unknown"
    final_text_status, companion_status = _searchable_text_status(file_record, companion_records)
    facts_by_field = {str(fact.get("field_name") or ""): fact for fact in facts}
    missing_fields = tuple(field for field in TARGET_FIELDS if _fact_status(facts_by_field.get(field)) == "missing")
    companion_helped = tuple(field for field in TARGET_FIELDS if _companion_helped(candidate, facts_by_field.get(field)))
    recommendations = {
        field: _field_recommendation(
            field=field,
            fact=facts_by_field.get(field),
            anchor_buckets=anchor_buckets,
            companion_helped=field in companion_helped,
        )
        for field in TARGET_FIELDS
    }
    return OCRFeasibilityRow(
        report_index=report_index,
        candidate_final_report_count=candidate_final_report_count,
        source_file_type=source_file_type,
        final_report_searchable_text=final_text_status,
        companion_docx_searchable_text=companion_status,
        missing_target_fields=missing_fields,
        companion_docx_helped_fields=companion_helped,
        field_recommendations=recommendations,
    )


def _searchable_text_status(file_record: dict[str, Any], companion_records: tuple[dict[str, Any], ...]) -> tuple[str, str]:
    extension = str(file_record.get("extension") or "").lower()
    path = Path(str(file_record.get("file_path") or ""))
    if extension == ".docx":
        final_pages, final_warnings = _extract_embedded_docx_text(path, source_label="docx final report")
        return _text_status(final_pages, final_warnings), "not_applicable"
    if extension == ".pdf":
        final_pages, final_warnings = _extract_embedded_pdf_text(path)
        companion_pages, companion_warnings = _extract_companion_docx_pages(companion_records)
        return _text_status(final_pages, final_warnings), _text_status(companion_pages, companion_warnings, none_label="not_detected")
    return "unsupported_source_type", "not_applicable"


def _text_status(pages: Iterable[PageText], warnings: Iterable[str], *, none_label: str = "unavailable") -> str:
    page_tuple = tuple(pages)
    if any(page.text.strip() for page in page_tuple):
        return "available"
    warning_text = " ".join(str(item).lower() for item in warnings)
    if "not installed" in warning_text:
        return "dependency_missing"
    if "path does not exist" in warning_text:
        return "source_missing"
    if "no embedded" in warning_text or "no searchable" in warning_text:
        return "not_searchable"
    return none_label


def _field_recommendation(
    *,
    field: str,
    fact: dict[str, Any] | None,
    anchor_buckets: dict[str, tuple[str, ...]],
    companion_helped: bool,
) -> dict[str, Any]:
    status = _fact_status(fact)
    anchor_family = FIELD_ANCHOR_FAMILIES[field]
    buckets = anchor_buckets.get(anchor_family, ())
    if status == "missing":
        if buckets:
            return {
                "ocr_recommended": False,
                "reason": "searchable_anchor_exists_parser_or_layout_tuning_first",
                "recommended_page_buckets": buckets,
            }
        return {
            "ocr_recommended": True,
            "reason": "target_field_missing_and_anchor_absent_from_searchable_text",
            "recommended_page_buckets": DEFAULT_PAGE_BUCKETS[field],
        }
    if status == "conflicting":
        return {
            "ocr_recommended": False,
            "reason": "verification_conflict_requires_review_before_ocr",
            "recommended_page_buckets": buckets or DEFAULT_PAGE_BUCKETS[field],
        }
    if status == "needs_review":
        return {
            "ocr_recommended": False,
            "reason": "field_found_but_needs_review",
            "recommended_page_buckets": buckets or DEFAULT_PAGE_BUCKETS[field],
        }
    if companion_helped:
        return {
            "ocr_recommended": False,
            "reason": "companion_docx_supported_current_extraction",
            "recommended_page_buckets": buckets or DEFAULT_PAGE_BUCKETS[field],
        }
    return {
        "ocr_recommended": False,
        "reason": "field_already_found",
        "recommended_page_buckets": buckets or DEFAULT_PAGE_BUCKETS[field],
    }


def _fact_status(fact: dict[str, Any] | None) -> str:
    if not fact:
        return "missing"
    return str(fact.get("verification_status") or "missing")


def _companion_helped(candidate: dict[str, Any], fact: dict[str, Any] | None) -> bool:
    if fact:
        evidence = tuple(fact.get("supporting_evidence") or ()) + tuple(fact.get("conflicting_evidence") or ())
        if any(str(item.get("source_type") or "") == "same_order_docx_companion" for item in evidence):
            return True
    field_name = str(fact.get("field_name") or "") if fact else ""
    for item in dict(candidate.get("fields", {})).get(field_name, ()):
        if "docx companion source" in str(dict(item).get("source_hint") or ""):
            return True
    return False


def _file_record_for_candidate(files: tuple[dict[str, Any], ...], candidate: dict[str, Any]) -> dict[str, Any]:
    file_id = str(candidate.get("file_id") or "")
    for item in files:
        if str(item.get("file_id") or "") == file_id:
            return item
    return {}


def _anchor_buckets_by_report(rows: Iterable[dict[str, Any]]) -> dict[int, dict[str, tuple[str, ...]]]:
    buckets: dict[int, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in rows:
        report_index = int(row.get("report_index") or 0)
        family = str(row.get("anchor_family") or "")
        bucket = str(row.get("page_bucket") or "")
        if report_index and family and bucket:
            buckets[report_index][family].add(bucket)
    return {
        report_index: {family: tuple(sorted(values)) for family, values in family_map.items()}
        for report_index, family_map in buckets.items()
    }


def _aggregate_counts(rows: Iterable[OCRFeasibilityRow]) -> dict[str, dict[str, int]]:
    row_tuple = tuple(rows)
    return {
        "source_file_type": _counter_to_dict(Counter(row.source_file_type for row in row_tuple)),
        "final_report_searchable_text": _counter_to_dict(Counter(row.final_report_searchable_text for row in row_tuple)),
        "companion_docx_searchable_text": _counter_to_dict(Counter(row.companion_docx_searchable_text for row in row_tuple)),
        "missing_target_fields": _counter_to_dict(Counter(field for row in row_tuple for field in row.missing_target_fields)),
        "companion_docx_helped_fields": _counter_to_dict(Counter(field for row in row_tuple for field in row.companion_docx_helped_fields)),
        "ocr_recommended_fields": _counter_to_dict(
            Counter(field for row in row_tuple for field, payload in row.field_recommendations.items() if payload.get("ocr_recommended"))
        ),
        "recommendation_reasons": _counter_to_dict(
            Counter(str(payload.get("reason") or "unknown") for row in row_tuple for payload in row.field_recommendations.values())
        ),
    }


def _aggregate_field_recommendations(rows: Iterable[OCRFeasibilityRow]) -> dict[str, dict[str, Any]]:
    row_tuple = tuple(rows)
    output: dict[str, dict[str, Any]] = {}
    for field in TARGET_FIELDS:
        field_payloads = tuple(row.field_recommendations[field] for row in row_tuple if field in row.field_recommendations)
        reason_counts = Counter(str(item.get("reason") or "unknown") for item in field_payloads)
        bucket_counts = Counter(
            bucket
            for item in field_payloads
            for bucket in tuple(item.get("recommended_page_buckets") or ())
        )
        output[field] = {
            "ocr_recommended": any(bool(item.get("ocr_recommended")) for item in field_payloads),
            "missing_report_count": sum(1 for row in row_tuple if field in row.missing_target_fields),
            "companion_docx_helped_report_count": sum(1 for row in row_tuple if field in row.companion_docx_helped_fields),
            "reasons": _counter_to_dict(reason_counts),
            "recommended_page_buckets": tuple(bucket for bucket, _count in bucket_counts.most_common()),
        }
    return output


def _privacy_warnings(knowledge_report: dict[str, Any], anchor_inventory_report: dict[str, Any]) -> tuple[str, ...]:
    warnings: list[str] = []
    if any(field not in FIELD_ANCHOR_FAMILIES for field in TARGET_FIELDS):
        warnings.append("target_field_without_anchor_family")
    warning_text = " ".join(str(item).lower() for item in knowledge_report.get("warnings", ()))
    if "no embedded" in warning_text or "no searchable" in warning_text:
        warnings.append("some_sources_lack_searchable_text")
    for family in set(FIELD_ANCHOR_FAMILIES.values()) - set(ANCHOR_FAMILIES):
        warnings.append(f"anchor_family_not_inventory_supported:{family}")
    if anchor_inventory_report.get("warnings"):
        warnings.extend(str(item) for item in anchor_inventory_report.get("warnings", ()))
    return tuple(sorted(set(warnings)))


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted((key, int(value)) for key, value in counter.items()))


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
