"""Local deterministic verification engine for Falcon Intelligence facts.

The verification engine promotes candidate metadata into explainable verified
facts only when deterministic evidence supports that promotion. It does not
extract new report content, OCR, call AI, upload, write schemas, or create a
Memory Graph.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable


VERIFICATION_VERSION = "1"
VERIFICATION_STATUSES = {"verified", "probable", "conflicting", "missing", "rejected", "needs_review"}
CONFIDENCE_LABELS = {"high", "medium", "low", "missing", "conflicting"}

VERIFY_FIELDS = (
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
    "sales_comparison_approach",
    "income_approach",
    "cost_approach",
    "extraordinary_assumptions_present",
    "hypothetical_conditions_present",
    "certification_section_present",
    "limiting_conditions_section_present",
)

STREET_SUFFIXES = {
    "st": "street",
    "street": "street",
    "ave": "avenue",
    "avenue": "avenue",
    "rd": "road",
    "road": "road",
    "dr": "drive",
    "drive": "drive",
    "ln": "lane",
    "lane": "lane",
    "ct": "court",
    "court": "court",
    "blvd": "boulevard",
    "boulevard": "boulevard",
    "hwy": "highway",
    "highway": "highway",
    "pkwy": "parkway",
    "parkway": "parkway",
}

PROVENANCE_TIER_ORDER = {
    "final_report_pdf": 10,
    "final_report_docx": 10,
    "same_order_docx_companion": 30,
    "folder_intake_metadata": 40,
    "filename": 50,
    "derived_report_title": 50,
    "extracted_metadata": 60,
}
AUTHORITATIVE_TIERS = {"final_report_pdf", "final_report_docx"}
MONTH_NUMBERS = {
    "jan": "01",
    "january": "01",
    "feb": "02",
    "february": "02",
    "mar": "03",
    "march": "03",
    "apr": "04",
    "april": "04",
    "may": "05",
    "jun": "06",
    "june": "06",
    "jul": "07",
    "july": "07",
    "aug": "08",
    "august": "08",
    "sep": "09",
    "sept": "09",
    "september": "09",
    "oct": "10",
    "october": "10",
    "nov": "11",
    "november": "11",
    "dec": "12",
    "december": "12",
}


@dataclass(frozen=True)
class VerificationEvidence:
    """One short evidence reference supporting or conflicting with a value."""

    field_name: str
    value: str | None
    normalized_value: str | None
    source_type: str
    source_label: str
    source_reference: str
    confidence: str
    method: str
    warning: str | None = None


@dataclass(frozen=True)
class VerifiedFact:
    """A local verified fact ledger entry."""

    field_name: str
    verified_value: str | None
    verification_status: str
    confidence: str
    supporting_evidence: tuple[VerificationEvidence, ...]
    conflicting_evidence: tuple[VerificationEvidence, ...]
    verification_method: str
    verification_timestamp: str
    notes: tuple[str, ...]
    source_references: tuple[str, ...]
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VerifiedReportFacts:
    """All verified-fact ledgers for one historical report candidate."""

    file_id: str
    file_name: str
    file_path: str
    facts: tuple[VerifiedFact, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerificationReport:
    """Complete local verification output."""

    verification_version: str
    generated_at: str
    source_knowledge_path: str
    report_facts: tuple[VerifiedReportFacts, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_version": self.verification_version,
            "generated_at": self.generated_at,
            "source_knowledge_path": self.source_knowledge_path,
            "report_facts": [asdict(item) for item in self.report_facts],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "summary": build_verification_summary(self),
        }


def verify_report_candidate(candidate: dict[str, Any], *, timestamp: str | None = None) -> VerifiedReportFacts:
    """Verify one historical knowledge candidate dictionary."""

    timestamp = timestamp or datetime.now(UTC).isoformat()
    evidence_by_field = collect_candidate_evidence(candidate)
    facts = tuple(_verify_field(field, evidence_by_field.get(field, ()), timestamp) for field in VERIFY_FIELDS)
    return VerifiedReportFacts(
        file_id=str(candidate.get("file_id", "")),
        file_name=str(candidate.get("file_name", "")),
        file_path=str(candidate.get("file_path", "")),
        facts=facts,
        warnings=tuple(str(item) for item in candidate.get("warnings", []) if item),
    )


def collect_candidate_evidence(candidate: dict[str, Any]) -> dict[str, tuple[VerificationEvidence, ...]]:
    """Collect short evidence references from metadata candidates only."""

    evidence: dict[str, list[VerificationEvidence]] = defaultdict(list)
    file_id = str(candidate.get("file_id", "unknown-file"))
    file_name = str(candidate.get("file_name", ""))

    for field, values in dict(candidate.get("fields", {})).items():
        for index, item in enumerate(values or (), start=1):
            value = item.get("value") if isinstance(item, dict) else None
            confidence = str(item.get("confidence", "low")) if isinstance(item, dict) else "low"
            if not value or confidence == "missing":
                continue
            evidence[field].append(
                VerificationEvidence(
                    field_name=field,
                    value=str(value),
                    normalized_value=normalize_fact_value(field, str(value)),
                    source_type=_source_type_from_candidate(item),
                    source_label=str(item.get("source_hint") or "metadata candidate"),
                    source_reference=f"{file_id}:{field}:{index}",
                    confidence=confidence if confidence in CONFIDENCE_LABELS else "low",
                    method=str(item.get("extraction_method") or "historical knowledge extraction"),
                    warning=item.get("warning"),
                )
            )

    for field, values in dict(candidate.get("approaches_referenced", {})).items():
        _append_presence_evidence(evidence, field, values, file_id)
    for field, values in dict(candidate.get("sections_detected", {})).items():
        _append_presence_evidence(evidence, field, values, file_id)

    derived = _derived_filename_evidence(file_id, file_name)
    for field, items in derived.items():
        evidence[field].extend(items)

    title_evidence = evidence.get("report_title", ())
    for item in title_evidence:
        if item.source_type not in AUTHORITATIVE_TIERS:
            continue
        if item.method.startswith("document title anchor"):
            continue
        report_type = _report_type_from_text(item.value or "")
        if report_type:
            evidence["report_type"].append(
                VerificationEvidence(
                    field_name="report_type",
                    value=report_type,
                    normalized_value=normalize_fact_value("report_type", report_type),
                    source_type="derived_report_title",
                    source_label=item.source_label,
                    source_reference=f"{item.source_reference}:report_type",
                    confidence="medium",
                    method="deterministic title agreement",
                )
            )

    return {field: tuple(items) for field, items in evidence.items()}


def run_verification(knowledge_report_path: str | Path) -> VerificationReport:
    """Run deterministic verification from an ignored historical knowledge output."""

    path = Path(knowledge_report_path)
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    timestamp = datetime.now(UTC).isoformat()
    report_facts = tuple(verify_report_candidate(candidate, timestamp=timestamp) for candidate in payload.get("report_candidates", []))
    return VerificationReport(
        verification_version=VERIFICATION_VERSION,
        generated_at=timestamp,
        source_knowledge_path=str(path),
        report_facts=report_facts,
        warnings=tuple(str(item) for item in payload.get("warnings", []) if item),
        errors=tuple(str(item) for item in payload.get("errors", []) if item),
    )


def build_verification_summary(report: VerificationReport) -> dict[str, Any]:
    """Build compact verification counts without sensitive report text."""

    statuses = Counter()
    confidence = Counter()
    candidate_facts = 0
    for item in report.report_facts:
        for fact in item.facts:
            statuses[fact.verification_status] += 1
            confidence[fact.confidence] += 1
            candidate_facts += len(fact.supporting_evidence) + len(fact.conflicting_evidence)

    return {
        "report_count": len(report.report_facts),
        "candidate_facts": candidate_facts,
        "verified_facts": statuses["verified"],
        "probable_facts": statuses["probable"],
        "conflicting_facts": statuses["conflicting"],
        "rejected_candidates": statuses["rejected"],
        "missing_values": statuses["missing"],
        "needs_review": statuses["needs_review"],
        "verification_status_breakdown": dict(sorted(statuses.items())),
        "confidence_breakdown": dict(sorted(confidence.items())),
        "warnings": list(report.warnings),
        "errors": list(report.errors),
    }


def render_verification_summary(report: VerificationReport) -> str:
    """Render a local Markdown verification summary without long source text."""

    summary = build_verification_summary(report)
    lines = [
        "# Verification Summary",
        "",
        "This local output contains deterministic verified-fact ledgers only. It does not store full report text, OCR output, AI analysis, embeddings, uploads, production records, or Memory Graph nodes.",
        "",
        "## Totals",
        "",
        f"- Reports verified: {summary['report_count']}",
        f"- Candidate facts considered: {summary['candidate_facts']}",
        f"- Verified facts: {summary['verified_facts']}",
        f"- Probable facts: {summary['probable_facts']}",
        f"- Conflicting facts: {summary['conflicting_facts']}",
        f"- Missing values: {summary['missing_values']}",
        f"- Rejected candidates: {summary['rejected_candidates']}",
        "",
        "## Verification Status",
        "",
    ]
    lines.extend(_markdown_count_lines(summary["verification_status_breakdown"]))
    lines.extend(["", "## Confidence", ""])
    lines.extend(_markdown_count_lines(summary["confidence_breakdown"]))
    lines.extend(["", "## Report Ledgers", ""])
    if report.report_facts:
        for item in report.report_facts:
            status_counts = Counter(fact.verification_status for fact in item.facts)
            lines.append(f"- {item.file_id}: {dict(sorted(status_counts.items()))}")
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings / Errors", ""])
    warnings = list(report.warnings) + list(report.errors)
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_verification_outputs(
    report: VerificationReport,
    output_directory: str | Path,
    *,
    basename: str = "verification-report",
) -> dict[str, str]:
    """Save ignored JSON and Markdown verification outputs."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / "verification-summary.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_verification_summary(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def normalize_fact_value(field_name: str, value: str) -> str:
    """Normalize obvious deterministic differences for comparison."""

    normalized = value.lower().replace("&", " and ")
    normalized = re.sub(r"[.,;:]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if field_name.endswith("_date"):
        date_value = _normalize_date_value(normalized)
        if date_value:
            return date_value
    if field_name == "intended_use":
        return _normalize_intended_use(normalized)
    if field_name == "property_type":
        return _normalize_property_type(normalized)
    if field_name == "property_address":
        tokens = normalized.split()
        tokens = [STREET_SUFFIXES.get(token, token) for token in tokens]
        normalized = " ".join(tokens)
    return normalized


def _verify_field(field_name: str, evidence: tuple[VerificationEvidence, ...], timestamp: str) -> VerifiedFact:
    if not evidence:
        return VerifiedFact(
            field_name=field_name,
            verified_value=None,
            verification_status="missing",
            confidence="missing",
            supporting_evidence=(),
            conflicting_evidence=(),
            verification_method="missing rule",
            verification_timestamp=timestamp,
            notes=("No candidate value was available; Falcon did not fabricate a value.",),
            source_references=(),
            diagnostics={"status_reason": "missing_candidate", "field_name": field_name, "candidate_count": 0},
        )

    by_value: dict[str, list[VerificationEvidence]] = defaultdict(list)
    for item in evidence:
        if item.normalized_value:
            by_value[item.normalized_value].append(item)

    if not by_value:
        return _needs_review_fact(field_name, evidence, timestamp, "Candidate evidence had no comparable value.")

    if len(by_value) > 1:
        tiered_fact = _tiered_conflict_fact(field_name, by_value, timestamp)
        if tiered_fact:
            return tiered_fact
        conflicting = tuple(item for group in by_value.values() for item in group)
        return VerifiedFact(
            field_name=field_name,
            verified_value=None,
            verification_status="conflicting",
            confidence="conflicting",
            supporting_evidence=(),
            conflicting_evidence=conflicting,
            verification_method="conflict rule",
            verification_timestamp=timestamp,
            notes=(
                "Multiple candidate values disagreed after deterministic normalization.",
                "Conflict details use normalized fingerprints only; raw candidate values are kept out of summaries.",
            ),
            source_references=tuple(item.source_reference for item in conflicting),
            diagnostics=_conflict_diagnostics(field_name, by_value),
        )

    supporting = tuple(next(iter(by_value.values())))
    verified_value = _preferred_value(supporting)
    independent_sources = {_provenance_key(item) for item in supporting}
    if len(supporting) >= 2 and len(independent_sources) >= 2:
        return VerifiedFact(
            field_name=field_name,
            verified_value=verified_value,
            verification_status="verified",
            confidence="high",
            supporting_evidence=supporting,
            conflicting_evidence=(),
            verification_method="agreement rule",
            verification_timestamp=timestamp,
            notes=("Multiple independent evidence references agreed after deterministic normalization.",),
            source_references=tuple(item.source_reference for item in supporting),
            diagnostics={
                "status_reason": "independent_agreement",
                "field_name": field_name,
                "candidate_count": len(supporting),
                "source_labels": tuple(sorted({item.source_label for item in supporting})),
                "source_references": tuple(sorted({item.source_reference for item in supporting})),
                "provenance_tiers": tuple(sorted({_provenance_tier(item) for item in supporting})),
            },
        )

    if any(item.confidence in {"high", "medium"} for item in supporting):
        return VerifiedFact(
            field_name=field_name,
            verified_value=verified_value,
            verification_status="probable",
            confidence="medium",
            supporting_evidence=supporting,
            conflicting_evidence=(),
            verification_method="single-source rule",
            verification_timestamp=timestamp,
            notes=("A candidate value exists, but independent agreement is not yet available.",),
            source_references=tuple(item.source_reference for item in supporting),
            diagnostics={
                "status_reason": "single_source_probable",
                "field_name": field_name,
                "candidate_count": len(supporting),
                "source_labels": tuple(sorted({item.source_label for item in supporting})),
                "provenance_tiers": tuple(sorted({_provenance_tier(item) for item in supporting})),
            },
        )

    return _needs_review_fact(field_name, supporting, timestamp, "Candidate value exists with low confidence only.")


def _append_presence_evidence(
    evidence: dict[str, list[VerificationEvidence]],
    field: str,
    item: Any,
    file_id: str,
) -> None:
    if not isinstance(item, dict) or item.get("value") != "present":
        return
    evidence[field].append(
        VerificationEvidence(
            field_name=field,
            value="present",
            normalized_value="present",
            source_type=_source_type_from_candidate(item),
            source_label=str(item.get("source_hint") or "phrase presence"),
            source_reference=f"{file_id}:{field}:presence",
            confidence=str(item.get("confidence") or "medium"),
            method=str(item.get("extraction_method") or "deterministic phrase presence"),
            warning=item.get("warning"),
        )
    )


def _derived_filename_evidence(file_id: str, file_name: str) -> dict[str, tuple[VerificationEvidence, ...]]:
    evidence: dict[str, list[VerificationEvidence]] = defaultdict(list)
    report_type = _report_type_from_text(file_name)
    if report_type:
        evidence["report_type"].append(
            VerificationEvidence(
                field_name="report_type",
                value=report_type,
                normalized_value=normalize_fact_value("report_type", report_type),
                source_type="filename",
                source_label="filename",
                source_reference=f"{file_id}:filename:report_type",
                confidence="medium",
                method="deterministic filename phrase",
            )
        )
    return {field: tuple(items) for field, items in evidence.items()}


def _report_type_from_text(text: str) -> str | None:
    normalized = normalize_fact_value("report_type", text)
    if "restricted appraisal report" in normalized:
        return "restricted appraisal report"
    if "appraisal report" in normalized:
        return "appraisal report"
    return None


def _preferred_value(evidence: tuple[VerificationEvidence, ...]) -> str | None:
    for item in evidence:
        if item.value:
            return item.value
    return None


def _needs_review_fact(
    field_name: str,
    evidence: Iterable[VerificationEvidence],
    timestamp: str,
    note: str,
) -> VerifiedFact:
    evidence_tuple = tuple(evidence)
    return VerifiedFact(
        field_name=field_name,
        verified_value=_preferred_value(evidence_tuple),
        verification_status="needs_review",
        confidence="low",
        supporting_evidence=evidence_tuple,
        conflicting_evidence=(),
        verification_method="needs-review rule",
        verification_timestamp=timestamp,
        notes=(note,),
        source_references=tuple(item.source_reference for item in evidence_tuple),
        diagnostics={
            "status_reason": "low_confidence_needs_review",
            "field_name": field_name,
            "candidate_count": len(evidence_tuple),
            "source_labels": tuple(sorted({item.source_label for item in evidence_tuple})),
            "provenance_tiers": tuple(sorted({_provenance_tier(item) for item in evidence_tuple})),
        },
    )


def _conflict_diagnostics(field_name: str, by_value: dict[str, list[VerificationEvidence]]) -> dict[str, Any]:
    evidence = tuple(item for group in by_value.values() for item in group)
    groups = tuple(
        {
            "fingerprint": _fingerprint(value),
            "candidate_count": len(items),
            "provenance_tier": _highest_group_tier(items),
            "source_labels": tuple(sorted({item.source_label for item in items})),
            "source_references": tuple(sorted({item.source_reference for item in items})),
        }
        for value, items in sorted(by_value.items(), key=lambda pair: _fingerprint(pair[0]))
    )
    return {
        "status_reason": "conflicting_normalized_values",
        "field_name": field_name,
        "candidate_count": len(evidence),
        "normalized_candidate_fingerprints": tuple(sorted(_fingerprint(value) for value in by_value)),
        "normalized_candidate_groups": groups,
        "source_labels": tuple(sorted({item.source_label for item in evidence})),
        "source_references": tuple(sorted({item.source_reference for item in evidence})),
        "provenance_tier_counts": dict(sorted(Counter(_provenance_tier(item) for item in evidence).items())),
    }


def _tiered_conflict_fact(
    field_name: str,
    by_value: dict[str, list[VerificationEvidence]],
    timestamp: str,
) -> VerifiedFact | None:
    authoritative_values = {
        value: items
        for value, items in by_value.items()
        if any(_provenance_tier(item) in AUTHORITATIVE_TIERS for item in items)
    }
    if len(authoritative_values) != 1 or len(authoritative_values) == len(by_value):
        return None

    authoritative_value, authoritative_items = next(iter(authoritative_values.items()))
    supporting = tuple(authoritative_items)
    conflicting = tuple(item for value, items in by_value.items() if value != authoritative_value for item in items)
    return VerifiedFact(
        field_name=field_name,
        verified_value=_preferred_value(supporting),
        verification_status="needs_review",
        confidence="low",
        supporting_evidence=supporting,
        conflicting_evidence=conflicting,
        verification_method="tiered provenance conflict rule",
        verification_timestamp=timestamp,
        notes=(
            "Final-report evidence had one normalized value, but lower-tier companion or metadata evidence disagreed.",
            "Companion evidence can support final-report evidence but cannot override it without review.",
        ),
        source_references=tuple(item.source_reference for item in supporting + conflicting),
        diagnostics={
            **_conflict_diagnostics(field_name, by_value),
            "status_reason": "lower_tier_evidence_disagrees_with_final_report",
            "authoritative_candidate_count": len(supporting),
            "lower_tier_conflicting_candidate_count": len(conflicting),
            "authoritative_provenance_tiers": tuple(sorted({_provenance_tier(item) for item in supporting})),
            "lower_tier_conflicting_provenance_tiers": tuple(sorted({_provenance_tier(item) for item in conflicting})),
        },
    )


def _fingerprint(value: str) -> str:
    return hashlib.sha256(f"falcon-verification-v1|{value}".encode("utf-8")).hexdigest()[:10]


def _provenance_key(item: VerificationEvidence) -> str:
    return "|".join((item.source_type, item.source_label, item.source_reference))


def _source_type_from_candidate(item: dict[str, Any]) -> str:
    source_hint = str(item.get("source_hint") or "").lower()
    method = str(item.get("extraction_method") or "").lower()
    if source_hint.startswith("docx final report"):
        return "final_report_docx"
    if source_hint.startswith("docx companion source"):
        return "same_order_docx_companion"
    if source_hint == "intake filename/folder metadata" or "historical intake" in method:
        return "folder_intake_metadata"
    if source_hint.startswith("page ") or source_hint in {"first three pages"}:
        return "final_report_pdf"
    return "extracted_metadata"


def _provenance_tier(item: VerificationEvidence) -> str:
    return item.source_type if item.source_type in PROVENANCE_TIER_ORDER else "extracted_metadata"


def _highest_group_tier(items: Iterable[VerificationEvidence]) -> str:
    item_tuple = tuple(items)
    if not item_tuple:
        return "unknown"
    return min(item_tuple, key=lambda item: PROVENANCE_TIER_ORDER.get(_provenance_tier(item), 99)).source_type


def _normalize_date_value(value: str) -> str | None:
    numeric = re.match(r"^(?P<month>\d{1,2})[/-](?P<day>\d{1,2})[/-](?P<year>(?:19|20)\d{2})$", value)
    if numeric:
        return f"{numeric.group('year')}-{int(numeric.group('month')):02d}-{int(numeric.group('day')):02d}"

    iso_like = re.match(r"^(?P<year>(?:19|20)\d{2})[/-](?P<month>\d{1,2})[/-](?P<day>\d{1,2})$", value)
    if iso_like:
        return f"{iso_like.group('year')}-{int(iso_like.group('month')):02d}-{int(iso_like.group('day')):02d}"

    month_name = re.match(r"^(?P<month>[a-z]+)\s+(?P<day>\d{1,2})\s+(?P<year>(?:19|20)\d{2})$", value)
    if month_name and month_name.group("month") in MONTH_NUMBERS:
        return f"{month_name.group('year')}-{MONTH_NUMBERS[month_name.group('month')]}-{int(month_name.group('day')):02d}"

    year_only = re.match(r"^((?:19|20)\d{2})$", value)
    if year_only:
        return year_only.group(1)
    return None


def _normalize_intended_use(value: str) -> str:
    value = re.sub(r"\b(the )?intended use (of (this|the) (appraisal|report) )?(is|was|will be)?\b", " ", value)
    value = re.sub(r"\b(this|the) (appraisal|report) (is|was) (intended|prepared) (to|for)\b", " ", value)
    value = re.sub(r"\bto (assist|aid|support) (the )?(client|intended user|lender)\b", " ", value)
    value = re.sub(r"\bfor (the )?(use|purpose|purposes) of\b", " ", value)
    value = re.sub(r"\bin connection with\b", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    tokens = set(re.findall(r"[a-z]+", value))
    if tokens.intersection({"loan", "loans", "lending", "financing", "mortgage", "credit", "underwriting", "collateral"}):
        return "loan_underwriting"
    if "portfolio" in tokens and tokens.intersection({"review", "analysis", "monitoring", "valuation"}):
        return "portfolio_review"
    if tokens.intersection({"tax", "assessment", "appeal", "advalorem"}):
        return "tax_assessment"
    if tokens.intersection({"estate", "probate"}):
        return "estate"
    if "litigation" in tokens or "dispute" in tokens:
        return "litigation"
    if "internal" in tokens and tokens.intersection({"decision", "planning", "review"}):
        return "internal_decision"
    return value


def _normalize_property_type(value: str) -> str:
    tokens = set(re.findall(r"[a-z]+", value))
    if "industrial" in tokens:
        return "industrial"
    if tokens.intersection({"warehouse", "distribution", "manufacturing", "logistics"}):
        return "industrial"
    if "multifamily" in tokens or tokens.intersection({"apartment", "apartments"}):
        return "multifamily"
    if "office" in tokens:
        return "office"
    if "retail" in tokens:
        return "retail"
    if tokens.intersection({"land", "site"}) and not tokens.intersection({"building", "improvements"}):
        return "land"
    generic_terms = {
        "building",
        "buildings",
        "property",
        "properties",
        "facility",
        "facilities",
        "improvement",
        "improvements",
        "real",
        "estate",
    }
    normalized_tokens = [token for token in value.split() if token not in generic_terms]
    return " ".join(normalized_tokens) or value


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
