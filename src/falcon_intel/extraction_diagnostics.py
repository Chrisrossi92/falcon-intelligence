"""Privacy-safe unresolved-field diagnostics for local extraction runs.

The diagnostics output is intentionally value-free: it records only field names,
anonymous report indexes, source tiers, source labels, coarse value shapes, length
buckets, fingerprints, and deterministic status reasons.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from falcon_intel.historical_knowledge import run_historical_knowledge_extraction
from falcon_intel.verification_engine import VerificationReport, verify_report_candidate


DIAGNOSTICS_VERSION = "1"
OUTPUT_BASENAME = "extraction-diagnostics-report"
UNRESOLVED_STATUSES = {"missing", "conflicting"}
PERSON_RE = re.compile(r"^[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){1,4}(?:,?\s+[A-Z]{2,8})?$")
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


@dataclass(frozen=True)
class UnresolvedFieldDiagnostic:
    """One redacted unresolved-field diagnostic row."""

    report_index: int
    field_name: str
    verification_status: str
    source_tier: str
    source_file_type: str
    source_label: str | None
    matched_anchor_type: str
    candidate_shape: str
    length_bucket: str
    fingerprint: str | None
    status_reason: str


@dataclass(frozen=True)
class ExtractionDiagnosticsReport:
    """Privacy-safe diagnostics for unresolved fields."""

    diagnostics_version: str
    generated_at: str
    source_intake_path: str
    analyzed_report_count: int
    unresolved_count: int
    diagnostics: tuple[UnresolvedFieldDiagnostic, ...]
    aggregate_categories: dict[str, dict[str, int]]
    recommendations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_local_extraction_diagnostics(intake_path: str | Path) -> ExtractionDiagnosticsReport:
    """Run the local extraction pipeline and return redacted unresolved diagnostics."""

    intake = _load_json(intake_path)
    knowledge_report = run_historical_knowledge_extraction(intake_path)
    verification_report = _build_verification_report(knowledge_report.to_dict())
    return build_extraction_diagnostics_report(
        intake=intake,
        knowledge_report=knowledge_report.to_dict(),
        verification_report=verification_report.to_dict(),
        source_intake_path=str(intake_path),
    )


def build_extraction_diagnostics_report(
    *,
    intake: dict[str, Any],
    knowledge_report: dict[str, Any],
    verification_report: dict[str, Any],
    source_intake_path: str = "",
    generated_at: str | None = None,
) -> ExtractionDiagnosticsReport:
    """Build redacted diagnostics from in-memory extraction and verification payloads."""

    generated_at = generated_at or datetime.now(UTC).isoformat()
    files_by_id = {str(item.get("file_id") or ""): dict(item) for item in intake.get("files", [])}
    candidates_by_id = {str(item.get("file_id") or ""): dict(item) for item in knowledge_report.get("report_candidates", [])}
    diagnostics: list[UnresolvedFieldDiagnostic] = []

    for report_index, package in enumerate(verification_report.get("report_facts", []), start=1):
        file_id = str(package.get("file_id") or "")
        file_record = files_by_id.get(file_id, {})
        candidate = candidates_by_id.get(file_id, {})
        for fact in package.get("facts", []):
            status = str(fact.get("verification_status") or "missing")
            diagnostics_payload = dict(fact.get("diagnostics") or {})
            reason = str(diagnostics_payload.get("status_reason") or status)
            if status not in UNRESOLVED_STATUSES and "disagrees" not in reason:
                continue
            diagnostics.extend(
                _diagnostics_for_fact(
                    report_index=report_index,
                    fact=dict(fact),
                    candidate=candidate,
                    file_record=file_record,
                    status_reason=reason,
                )
            )

    diagnostic_tuple = tuple(diagnostics)
    return ExtractionDiagnosticsReport(
        diagnostics_version=DIAGNOSTICS_VERSION,
        generated_at=generated_at,
        source_intake_path=str(source_intake_path),
        analyzed_report_count=len(tuple(verification_report.get("report_facts", ()))),
        unresolved_count=len(diagnostic_tuple),
        diagnostics=diagnostic_tuple,
        aggregate_categories=_build_aggregate_categories(diagnostic_tuple),
        recommendations=_recommend_next_steps(diagnostic_tuple, knowledge_report),
    )


def render_extraction_diagnostics_markdown(report: ExtractionDiagnosticsReport) -> str:
    """Render diagnostics without raw extracted values or report snippets."""

    lines = [
        "# Privacy-Safe Extraction Diagnostics",
        "",
        "This local-only report contains no raw extracted values and no report text snippets. Candidate values are represented only as coarse shapes, length buckets, and fingerprints.",
        "",
        "## Totals",
        "",
        f"- Candidate final reports analyzed: {report.analyzed_report_count}",
        f"- Unresolved diagnostic rows: {report.unresolved_count}",
        "",
        "## Aggregate Categories",
        "",
    ]
    for category, counts in report.aggregate_categories.items():
        lines.append(f"### {category.replace('_', ' ').title()}")
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
            f"status={item.verification_status}; "
            f"reason={item.status_reason}; "
            f"tier={item.source_tier}; "
            f"file_type={item.source_file_type}; "
            f"source_label={item.source_label or 'none'}; "
            f"anchor={item.matched_anchor_type}; "
            f"shape={item.candidate_shape}; "
            f"length={item.length_bucket}; "
            f"fingerprint={item.fingerprint or 'none'}"
        )

    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report.recommendations) if report.recommendations else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_extraction_diagnostics_outputs(
    report: ExtractionDiagnosticsReport,
    output_directory: str | Path,
    *,
    basename: str = OUTPUT_BASENAME,
) -> dict[str, str]:
    """Save redacted diagnostics JSON and Markdown under an ignored local folder."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / f"{basename}.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_extraction_diagnostics_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _build_verification_report(knowledge_report: dict[str, Any]) -> VerificationReport:
    timestamp = datetime.now(UTC).isoformat()
    report_facts = tuple(verify_report_candidate(candidate, timestamp=timestamp) for candidate in knowledge_report.get("report_candidates", []))
    return VerificationReport(
        verification_version="1",
        generated_at=timestamp,
        source_knowledge_path="in-memory historical knowledge report",
        report_facts=report_facts,
        warnings=tuple(str(item) for item in knowledge_report.get("warnings", []) if item),
        errors=tuple(str(item) for item in knowledge_report.get("errors", []) if item),
    )


def _diagnostics_for_fact(
    *,
    report_index: int,
    fact: dict[str, Any],
    candidate: dict[str, Any],
    file_record: dict[str, Any],
    status_reason: str,
) -> tuple[UnresolvedFieldDiagnostic, ...]:
    field_name = str(fact.get("field_name") or "unknown")
    status = str(fact.get("verification_status") or "missing")
    evidence = tuple(fact.get("supporting_evidence") or ()) + tuple(fact.get("conflicting_evidence") or ())
    if evidence:
        return tuple(
            _diagnostic_from_evidence(
                report_index=report_index,
                field_name=field_name,
                verification_status=status,
                evidence=dict(item),
                status_reason=status_reason,
            )
            for item in evidence
        )

    candidate_items = tuple(dict(item) for item in dict(candidate.get("fields", {})).get(field_name, ()) if isinstance(item, dict))
    if not candidate_items:
        candidate_items = ({"confidence": "missing", "extraction_method": "deterministic pattern matching", "warning": "field not found"},)
    return tuple(
        _diagnostic_from_missing_candidate(
            report_index=report_index,
            field_name=field_name,
            verification_status=status,
            candidate=item,
            file_record=file_record,
            status_reason=status_reason,
        )
        for item in candidate_items[:3]
    )


def _diagnostic_from_evidence(
    *,
    report_index: int,
    field_name: str,
    verification_status: str,
    evidence: dict[str, Any],
    status_reason: str,
) -> UnresolvedFieldDiagnostic:
    value = evidence.get("normalized_value") or evidence.get("value")
    source_tier = str(evidence.get("source_type") or "unknown")
    return UnresolvedFieldDiagnostic(
        report_index=report_index,
        field_name=field_name,
        verification_status=verification_status,
        source_tier=source_tier,
        source_file_type=_source_file_type(source_tier, evidence.get("source_label")),
        source_label=_redacted_source_label(evidence.get("source_label")),
        matched_anchor_type=_anchor_type(evidence.get("method")),
        candidate_shape=_candidate_shape(field_name, evidence.get("value")),
        length_bucket=_length_bucket(len(str(evidence.get("value") or ""))),
        fingerprint=_fingerprint(field_name, value),
        status_reason=status_reason,
    )


def _diagnostic_from_missing_candidate(
    *,
    report_index: int,
    field_name: str,
    verification_status: str,
    candidate: dict[str, Any],
    file_record: dict[str, Any],
    status_reason: str,
) -> UnresolvedFieldDiagnostic:
    source_tier = _source_tier_from_hint(candidate.get("source_hint"))
    value = candidate.get("value")
    return UnresolvedFieldDiagnostic(
        report_index=report_index,
        field_name=field_name,
        verification_status=verification_status,
        source_tier=source_tier,
        source_file_type=_source_file_type(source_tier, candidate.get("source_hint"), file_record=file_record),
        source_label=_redacted_source_label(candidate.get("source_hint")),
        matched_anchor_type=_anchor_type(candidate.get("extraction_method") or candidate.get("warning")),
        candidate_shape=_candidate_shape(field_name, value),
        length_bucket=_length_bucket(len(str(value or ""))),
        fingerprint=_fingerprint(field_name, value),
        status_reason=status_reason,
    )


def _source_tier_from_hint(source_hint: Any) -> str:
    hint = str(source_hint or "").lower()
    if hint.startswith("docx final report"):
        return "final_report_docx"
    if hint.startswith("docx companion source"):
        return "same_order_docx_companion"
    if hint.startswith("page "):
        return "final_report_pdf"
    if hint == "intake filename/folder metadata":
        return "folder_intake_metadata"
    if not hint:
        return "not_detected"
    return "extracted_metadata"


def _source_file_type(source_tier: str, source_label: Any, *, file_record: dict[str, Any] | None = None) -> str:
    if source_tier in {"final_report_docx", "same_order_docx_companion"}:
        return "docx"
    if source_tier == "final_report_pdf":
        return "pdf"
    if source_tier in {"folder_intake_metadata", "filename"}:
        return "metadata"
    if file_record:
        extension = str(file_record.get("extension") or "").strip(".").lower()
        if extension:
            return extension
    label = str(source_label or "").lower()
    if "docx" in label:
        return "docx"
    if label.startswith("page "):
        return "pdf"
    return "unknown"


def _redacted_source_label(value: Any) -> str | None:
    if not value:
        return None
    label = str(value)
    if label.startswith("page "):
        return label
    if label == "first three pages":
        return label
    if label.startswith("docx companion source:"):
        return "docx companion source"
    if label.startswith("docx final report:"):
        return "docx final report"
    if label == "intake filename/folder metadata":
        return label
    return "source label"


def _anchor_type(value: Any) -> str:
    text = str(value or "").lower()
    if "label match" in text:
        return "label_match"
    if "title phrase" in text:
        return "title_phrase"
    if "report type phrase" in text:
        return "report_type_phrase"
    if "signature block" in text:
        return "signature_anchor"
    if "review section" in text:
        return "review_anchor"
    if "summary of salient facts" in text:
        return "section_table"
    if "phrase presence" in text:
        return "presence_phrase"
    if "historical intake" in text:
        return "intake_metadata"
    if "filename" in text:
        return "filename_metadata"
    if "not found" in text or "not detected" in text or "missing" in text:
        return "not_detected"
    return "unknown"


def _candidate_shape(field_name: str, value: Any) -> str:
    if value in (None, ""):
        return "missing"
    text = str(value)
    if DATE_RE.search(text):
        return "date-like"
    if ADDRESS_RE.search(text):
        return "address-like"
    if field_name in {"appraiser_name", "reviewer_name"} and PERSON_RE.match(text.strip()):
        return "person-like"
    if text.lower().strip() == "present":
        return "presence-indicator"
    if len(text) > 80:
        return "long-text"
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


def _fingerprint(field_name: str, value: Any) -> str | None:
    if value in (None, ""):
        return None
    normalized = re.sub(r"\s+", " ", str(value)).strip().lower()
    return hashlib.sha256(f"falcon-diagnostics-v1|{field_name}|{normalized}".encode("utf-8")).hexdigest()[:10]


def _build_aggregate_categories(items: Iterable[UnresolvedFieldDiagnostic]) -> dict[str, dict[str, int]]:
    diagnostics = tuple(items)
    return {
        "fields_by_status": _counter_to_dict(Counter(f"{item.field_name}:{item.verification_status}" for item in diagnostics)),
        "field_counts": _counter_to_dict(Counter(item.field_name for item in diagnostics)),
        "status_reasons": _counter_to_dict(Counter(item.status_reason for item in diagnostics)),
        "source_tiers": _counter_to_dict(Counter(item.source_tier for item in diagnostics)),
        "source_file_types": _counter_to_dict(Counter(item.source_file_type for item in diagnostics)),
        "anchor_types": _counter_to_dict(Counter(item.matched_anchor_type for item in diagnostics)),
        "candidate_shapes": _counter_to_dict(Counter(item.candidate_shape for item in diagnostics)),
        "length_buckets": _counter_to_dict(Counter(item.length_bucket for item in diagnostics)),
    }


def _recommend_next_steps(items: Iterable[UnresolvedFieldDiagnostic], knowledge_report: dict[str, Any]) -> tuple[str, ...]:
    diagnostics = tuple(items)
    recommendations: list[str] = []
    missing_not_detected = sorted({item.field_name for item in diagnostics if item.verification_status == "missing" and item.source_tier == "not_detected"})
    if missing_not_detected:
        recommendations.append(f"Add deterministic labels or anchor patterns for missing fields: {', '.join(missing_not_detected)}.")
    if any(item.verification_status == "missing" and item.source_file_type in {"pdf", "unknown"} for item in diagnostics):
        recommendations.append("Improve first-page and section scanning before OCR for fields that are present as embedded text but not anchored.")
    if any(item.source_tier == "same_order_docx_companion" and item.verification_status != "missing" for item in diagnostics):
        recommendations.append("Keep DOCX companion evidence supportive only; review same-order companion disagreements before promotion.")
    if any(item.verification_status == "conflicting" for item in diagnostics):
        recommendations.append("Resolve true final-report conflicts with field-specific review rules before promotion.")
    warnings = " ".join(str(item) for item in knowledge_report.get("warnings", ())).lower()
    if "no embedded/searchable pdf text" in warnings or "no searchable" in warnings:
        recommendations.append("Plan OCR feasibility for files without embedded searchable text, keeping OCR output ignored under data/.")
    return tuple(dict.fromkeys(recommendations))


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted((key, int(value)) for key, value in counter.items()))


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
