"""Local Knowledge Object Builder V1 for Falcon Intelligence.

The builder converts local Verified Fact ledgers into structured knowledge
object candidates. It does not create production schemas, APIs, uploads,
Memory Graph nodes, embeddings, OCR, or AI output.
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


KNOWLEDGE_OBJECT_VERSION = "1"
PROMOTABLE_STATUSES = {"verified"}
REVIEW_STATUSES = {"probable", "needs_review"}
ISSUE_STATUSES = {"conflicting", "missing", "needs_review", "probable"}
CRITICAL_FIELDS = {"property_address", "report_type", "effective_date"}


@dataclass(frozen=True)
class KnowledgeObjectCandidate:
    """One local candidate object built from Verified Facts."""

    object_type: str
    object_id: str
    stable_key: str
    display_label: str
    source_verified_facts: tuple[str, ...]
    confidence: str
    readiness: str
    readiness_reason: str
    missing_required_fields: tuple[str, ...]
    conflicting_fields: tuple[str, ...]
    review_required_fields: tuple[str, ...]
    notes: tuple[str, ...]
    attributes: dict[str, str]
    created_timestamp: str


@dataclass(frozen=True)
class ReportKnowledgeObjects:
    """Knowledge object candidates for one verified report package."""

    file_id: str
    file_name: str
    object_candidates: tuple[KnowledgeObjectCandidate, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class KnowledgeObjectsReport:
    """Complete local Knowledge Object Builder output."""

    knowledge_object_version: str
    generated_at: str
    source_verification_path: str
    reports: tuple[ReportKnowledgeObjects, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_object_version": self.knowledge_object_version,
            "generated_at": self.generated_at,
            "source_verification_path": self.source_verification_path,
            "reports": [asdict(item) for item in self.reports],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "summary": build_knowledge_objects_summary(self),
        }


def build_report_knowledge_objects(report_facts: dict[str, Any], *, timestamp: str | None = None) -> ReportKnowledgeObjects:
    """Build V1 object candidates for one verified report facts payload."""

    timestamp = timestamp or datetime.now(UTC).isoformat()
    facts = {fact.get("field_name"): fact for fact in report_facts.get("facts", []) if fact.get("field_name")}
    file_id = str(report_facts.get("file_id", "unknown-report"))
    file_name = str(report_facts.get("file_name", "Unknown report"))

    candidates = tuple(
        candidate
        for candidate in (
        _build_property_object(file_id, facts, timestamp),
        _build_report_object(file_id, facts, timestamp),
        _build_client_user_object(file_id, facts, timestamp),
        _build_personnel_object(file_id, facts, timestamp),
        _build_open_issues_object(file_id, facts, timestamp),
    )
        if candidate is not None
    )

    return ReportKnowledgeObjects(
        file_id=file_id,
        file_name=file_name,
        object_candidates=candidates,
        warnings=tuple(str(item) for item in report_facts.get("warnings", []) if item),
    )


def run_knowledge_object_builder(verification_report_path: str | Path) -> KnowledgeObjectsReport:
    """Build local knowledge object candidates from ignored verification output."""

    path = Path(verification_report_path)
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    timestamp = datetime.now(UTC).isoformat()
    reports = tuple(build_report_knowledge_objects(item, timestamp=timestamp) for item in payload.get("report_facts", []))
    return KnowledgeObjectsReport(
        knowledge_object_version=KNOWLEDGE_OBJECT_VERSION,
        generated_at=timestamp,
        source_verification_path=str(path),
        reports=reports,
        warnings=tuple(str(item) for item in payload.get("warnings", []) if item),
        errors=tuple(str(item) for item in payload.get("errors", []) if item),
    )


def build_knowledge_objects_summary(report: KnowledgeObjectsReport) -> dict[str, Any]:
    """Build compact object and readiness counts."""

    object_types = Counter()
    readiness = Counter()
    readiness_reasons = Counter()
    total_issues = 0
    review_fields = 0
    for package in report.reports:
        for candidate in package.object_candidates:
            object_types[candidate.object_type] += 1
            readiness[candidate.readiness] += 1
            readiness_reasons[candidate.readiness_reason] += 1
            total_issues += len(candidate.missing_required_fields) + len(candidate.conflicting_fields)
            review_fields += len(candidate.review_required_fields)

    return {
        "report_count": len(report.reports),
        "object_count": sum(object_types.values()),
        "object_type_breakdown": dict(sorted(object_types.items())),
        "readiness_breakdown": dict(sorted(readiness.items())),
        "readiness_reason_breakdown": dict(sorted(readiness_reasons.items())),
        "issue_count": total_issues,
        "review_required_field_count": review_fields,
        "warnings": list(report.warnings),
        "errors": list(report.errors),
    }


def render_knowledge_objects_summary(report: KnowledgeObjectsReport) -> str:
    """Render local Markdown summary without source report text."""

    summary = build_knowledge_objects_summary(report)
    lines = [
        "# Knowledge Objects Summary",
        "",
        "This local output contains deterministic Knowledge Object candidates only. It does not create production schemas, Memory Graph nodes, AI output, OCR output, embeddings, or uploads.",
        "",
        "## Totals",
        "",
        f"- Reports processed: {summary['report_count']}",
        f"- Object candidates: {summary['object_count']}",
        f"- Issues surfaced: {summary['issue_count']}",
        "",
        "## Object Types",
        "",
    ]
    lines.extend(_markdown_count_lines(summary["object_type_breakdown"]))
    lines.extend(["", "## Readiness", ""])
    lines.extend(_markdown_count_lines(summary["readiness_breakdown"]))
    lines.extend(["", "## Readiness Reasons", ""])
    lines.extend(_markdown_count_lines(summary["readiness_reason_breakdown"]))
    lines.extend(["", "## Report Packages", ""])
    if report.reports:
        for package in report.reports:
            ready_counts = Counter(candidate.readiness for candidate in package.object_candidates)
            lines.append(f"- {package.file_id}: {dict(sorted(ready_counts.items()))}")
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings / Errors", ""])
    warnings = list(report.warnings) + list(report.errors)
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_knowledge_object_outputs(
    report: KnowledgeObjectsReport,
    output_directory: str | Path,
    *,
    basename: str = "knowledge-objects-report",
) -> dict[str, str]:
    """Save ignored JSON and Markdown knowledge object outputs."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / "knowledge-objects-summary.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_knowledge_objects_summary(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _build_property_object(file_id: str, facts: dict[str, dict[str, Any]], timestamp: str) -> KnowledgeObjectCandidate | None:
    fields = ("property_address", "property_type")
    if not _has_object_material(facts, fields):
        return None
    address = _value(facts, "property_address")
    missing = _missing_required(facts, ("property_address",))
    conflicts = _conflicting_fields(facts, fields)
    review = _review_required(facts, ("property_address",))
    readiness, readiness_reason = _readiness_from_required(facts, ("property_address",), conflicts)
    confidence = "high" if readiness == "ready" else "low"
    display = address or "Property object needs address review"
    attributes = _attributes(facts, fields)
    attributes["normalized_identity_key"] = _normalize_key(address or display)
    return _candidate(
        object_type="property",
        file_id=file_id,
        display_label=display,
        facts=facts,
        fields=fields,
        confidence=confidence,
        readiness=readiness,
        readiness_reason=readiness_reason,
        missing=missing,
        conflicts=conflicts,
        review=review,
        notes=("Property Object is ready only when address is verified with high-confidence support and not conflicting.",),
        attributes=attributes,
        timestamp=timestamp,
    )


def _build_report_object(file_id: str, facts: dict[str, dict[str, Any]], timestamp: str) -> KnowledgeObjectCandidate | None:
    fields = (
        "report_type",
        "report_date",
        "effective_date",
        "inspection_date",
        "sales_comparison_approach",
        "income_approach",
        "cost_approach",
        "certification_section_present",
        "limiting_conditions_section_present",
        "extraordinary_assumptions_present",
        "hypothetical_conditions_present",
    )
    if not _has_object_material(facts, fields):
        return None
    missing = _missing_required(facts, ("report_type", "effective_date"))
    conflicts = _conflicting_fields(facts, fields)
    review = _review_required(facts, ("report_type", "effective_date"))
    readiness, readiness_reason = _readiness_from_required(facts, ("report_type", "effective_date"), conflicts)
    display = "Report object"
    if _value(facts, "report_type"):
        display = f"{_value(facts, 'report_type')} report object"
    return _candidate(
        object_type="report",
        file_id=file_id,
        display_label=display,
        facts=facts,
        fields=fields,
        confidence="high" if readiness == "ready" else "low",
        readiness=readiness,
        readiness_reason=readiness_reason,
        missing=missing,
        conflicts=conflicts,
        review=review,
        notes=("Report Object is ready only when report type and effective date are verified with high-confidence support.",),
        attributes=_attributes(facts, fields),
        timestamp=timestamp,
    )


def _build_client_user_object(file_id: str, facts: dict[str, dict[str, Any]], timestamp: str) -> KnowledgeObjectCandidate | None:
    fields = ("client", "intended_user", "intended_use")
    if not _has_object_material(facts, fields):
        return None
    conflicts = _conflicting_fields(facts, fields)
    missing = _missing_required(facts, ("client", "intended_user"))
    review = _review_required(facts, ("client", "intended_user"))
    readiness, readiness_reason = _readiness_from_required(facts, ("client", "intended_user"), conflicts)
    return _candidate(
        object_type="client_user",
        file_id=file_id,
        display_label=_value(facts, "client") or "Client/User object needs review",
        facts=facts,
        fields=fields,
        confidence="medium" if readiness == "ready" else "low",
        readiness=readiness,
        readiness_reason=readiness_reason,
        missing=missing,
        conflicts=conflicts,
        review=review,
        notes=("Client/User Object is ready only when client and intended user are verified; probable values remain review items.",),
        attributes=_attributes(facts, fields),
        timestamp=timestamp,
    )


def _build_personnel_object(file_id: str, facts: dict[str, dict[str, Any]], timestamp: str) -> KnowledgeObjectCandidate | None:
    fields = ("appraiser_name", "reviewer_name")
    if not _has_object_material(facts, fields):
        return None
    conflicts = _conflicting_fields(facts, fields)
    missing = _missing_required(facts, ("appraiser_name", "reviewer_name"))
    review = _review_required(facts, ("appraiser_name", "reviewer_name"))
    readiness, readiness_reason = _readiness_from_required(facts, ("appraiser_name", "reviewer_name"), conflicts)
    return _candidate(
        object_type="personnel",
        file_id=file_id,
        display_label=_value(facts, "appraiser_name") or "Personnel object needs review",
        facts=facts,
        fields=fields,
        confidence="high" if readiness == "ready" else "low",
        readiness=readiness,
        readiness_reason=readiness_reason,
        missing=missing,
        conflicts=conflicts,
        review=review,
        notes=("Personnel Object is ready only when appraiser and reviewer names are verified; probable names remain review items.",),
        attributes=_attributes(facts, fields),
        timestamp=timestamp,
    )


def _build_open_issues_object(file_id: str, facts: dict[str, dict[str, Any]], timestamp: str) -> KnowledgeObjectCandidate | None:
    issue_fields = tuple(field for field, fact in sorted(facts.items()) if _status_value(fact) in ISSUE_STATUSES and field in CRITICAL_FIELDS.union({"client", "intended_user", "reviewer_name", "inspection_date"}))
    conflicts = tuple(field for field in issue_fields if _status(facts, field) == "conflicting")
    missing = tuple(field for field in issue_fields if _status(facts, field) == "missing")
    needs_review = tuple(field for field in issue_fields if _status(facts, field) in REVIEW_STATUSES)
    readiness = "blocked" if conflicts else "needs_review" if issue_fields else "ready"
    if not issue_fields or (missing and not conflicts and not needs_review):
        return None
    readiness_reason = "blocked_by_conflict" if conflicts else "needs_review_required"
    notes = []
    if conflicts:
        notes.append(f"Resolve conflicting fields before promotion: {', '.join(conflicts)}.")
    if missing:
        notes.append(f"Verify missing fields when relevant: {', '.join(missing)}.")
    if needs_review:
        notes.append(f"Review probable or low-confidence fields before promotion: {', '.join(needs_review)}.")
    if not notes:
        notes.append("No open issues were surfaced by V1 rules.")
    return _candidate(
        object_type="open_issues",
        file_id=file_id,
        display_label="Open Issues",
        facts=facts,
        fields=issue_fields,
        confidence="low" if issue_fields else "high",
        readiness=readiness,
        readiness_reason=readiness_reason,
        missing=missing,
        conflicts=conflicts,
        review=needs_review,
        notes=tuple(notes),
        attributes={field: _status(facts, field) for field in issue_fields},
        timestamp=timestamp,
    )


def _candidate(
    *,
    object_type: str,
    file_id: str,
    display_label: str,
    facts: dict[str, dict[str, Any]],
    fields: Iterable[str],
    confidence: str,
    readiness: str,
    readiness_reason: str,
    missing: tuple[str, ...],
    conflicts: tuple[str, ...],
    review: tuple[str, ...],
    notes: tuple[str, ...],
    attributes: dict[str, str],
    timestamp: str,
) -> KnowledgeObjectCandidate:
    fact_ids = tuple(field for field in fields if field in facts and (_value(facts, field) or _status(facts, field) == "conflicting"))
    stable_key = _stable_key(object_type, file_id, display_label)
    return KnowledgeObjectCandidate(
        object_type=object_type,
        object_id=f"ko-{stable_key[:16]}",
        stable_key=stable_key,
        display_label=display_label,
        source_verified_facts=fact_ids,
        confidence=confidence,
        readiness=readiness,
        readiness_reason=readiness_reason,
        missing_required_fields=missing,
        conflicting_fields=conflicts,
        review_required_fields=review,
        notes=notes,
        attributes=attributes,
        created_timestamp=timestamp,
    )


def _attributes(facts: dict[str, dict[str, Any]], fields: Iterable[str]) -> dict[str, str]:
    attributes = {}
    for field in fields:
        if field not in facts:
            continue
        value = _value(facts, field)
        status = _status(facts, field)
        if value:
            attributes[field] = value
        elif status == "conflicting":
            attributes[field] = "conflicting"
    return attributes


def _missing_required(facts: dict[str, dict[str, Any]], fields: Iterable[str]) -> tuple[str, ...]:
    return tuple(field for field in fields if not _value(facts, field) or _status(facts, field) in {"missing", "conflicting"})


def _conflicting_fields(facts: dict[str, dict[str, Any]], fields: Iterable[str]) -> tuple[str, ...]:
    return tuple(field for field in fields if _status(facts, field) == "conflicting")


def _review_required(facts: dict[str, dict[str, Any]], fields: Iterable[str]) -> tuple[str, ...]:
    return tuple(field for field in fields if _value(facts, field) and _status(facts, field) in REVIEW_STATUSES)


def _promotable(facts: dict[str, dict[str, Any]], field: str) -> bool:
    fact = facts.get(field, {})
    return _status_value(fact) in PROMOTABLE_STATUSES and str(fact.get("confidence") or "") == "high" and bool(_value(facts, field))


def _has_object_material(facts: dict[str, dict[str, Any]], fields: Iterable[str]) -> bool:
    for field in fields:
        if _value(facts, field) or _status(facts, field) == "conflicting":
            return True
    return False


def _readiness_from_required(
    facts: dict[str, dict[str, Any]],
    required_fields: Iterable[str],
    conflicts: tuple[str, ...],
) -> tuple[str, str]:
    required = tuple(required_fields)
    if conflicts:
        return "blocked", "blocked_by_conflict"
    if all(_promotable(facts, field) for field in required):
        return "ready", "verified_high_confidence"
    if any(_status(facts, field) == "missing" or not _value(facts, field) for field in required):
        return "needs_review", "needs_review_missing_required"
    return "needs_review", "needs_review_probable_or_low_confidence"


def _value(facts: dict[str, dict[str, Any]], field: str) -> str | None:
    value = facts.get(field, {}).get("verified_value")
    return str(value) if value not in (None, "") else None


def _status(facts: dict[str, dict[str, Any]], field: str) -> str:
    return _status_value(facts.get(field, {}))


def _status_value(fact: dict[str, Any]) -> str:
    return str(fact.get("verification_status") or "missing")


def _normalize_key(value: str) -> str:
    normalized = value.lower().replace("&", " and ")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-") or "unknown"


def _stable_key(object_type: str, file_id: str, display_label: str) -> str:
    digest = hashlib.sha256(f"{object_type}|{file_id}|{display_label}".encode("utf-8")).hexdigest()
    return f"{object_type}-{digest}"


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
