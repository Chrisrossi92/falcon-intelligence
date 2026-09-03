"""Canonical Assignment Intelligence Record V1.

This module composes synthetic/local extraction candidates, provenance,
appraiser review decisions, reusable knowledge references, and readiness into
one deterministic assignment-scoped record. It does not provide production
persistence, Falcon authorization, source preview, narrative generation, or
valuation conclusions.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from falcon_intel.schema_registry import ASSIGNMENT_INTELLIGENCE_RECORD_SCHEMA_VERSION
from falcon_intel.verification_engine import (
    VerificationEvidence,
    collect_candidate_evidence,
    normalize_fact_value,
    verify_report_candidate,
)


JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

CANDIDATE_STATES = {
    "extracted_candidate",
    "accepted",
    "corrected",
    "rejected",
    "deferred",
    "unresolved_conflict",
}
FACT_STATES = {"verified", "corrected", "appraiser_entered", "superseded"}
REVIEW_ACTIONS = {
    "candidate_verified",
    "candidate_corrected",
    "candidate_rejected",
    "candidate_deferred",
    "appraiser_fact_entered",
    "conclusion_entered",
}
CONFLICT_STATES = {"unresolved", "resolved"}
READINESS_STATES = {"ready", "needs_review", "blocked"}
LIFECYCLE_STATES = {"draft", "in_review", "analysis_ready", "superseded", "archived"}
SEVERITIES = {"blocking", "nonblocking"}
COMPARABLE_SELECTION_STATES = {"candidate", "selected", "rejected"}
CONCLUSION_STATES = {"draft", "in_review", "approved", "superseded"}


@dataclass(frozen=True)
class EntityReference:
    """Stable reference to an entity owned by Falcon or another knowledge model."""

    reference_id: str
    reference_type: str
    display_label: str
    source_system: str


@dataclass(frozen=True)
class RecordLineage:
    """Link to the immediately preceding immutable record version, when any."""

    previous_record_id: str | None = None
    previous_record_version: int | None = None


@dataclass(frozen=True)
class RecordIdentity:
    """Identity and lifecycle metadata for one record version."""

    record_id: str
    record_version: int
    schema_version: str
    created_at: str
    updated_at: str
    lifecycle_state: str
    lineage: RecordLineage


@dataclass(frozen=True)
class SourceReference:
    """Metadata-only source identity; source content is never embedded by default."""

    source_id: str
    source_type: str
    display_label: str
    safe_reference: str
    document_id: str | None = None
    content_included: bool = False


@dataclass(frozen=True)
class EvidenceLocator:
    """Optional structured locator within a source."""

    page_number: int | None = None
    section: str | None = None
    table: str | None = None
    cell: str | None = None
    paragraph: str | None = None
    region: str | None = None


@dataclass(frozen=True)
class EvidenceReference:
    """Immutable provenance for one machine observation or human support item."""

    evidence_id: str
    source_id: str
    field_key: str
    source_field_key: str
    candidate_reference: str
    locator: EvidenceLocator
    extraction_method: str
    extracted_at: str
    confidence: str
    extractor_name: str
    extractor_version: str
    source_excerpt: str | None = None
    freshness: str = "unknown"
    quality: str = "unknown"


@dataclass(frozen=True)
class CandidateAssertion:
    """One grouped machine observation before an appraiser decision."""

    candidate_id: str
    field_key: str
    source_field_key: str
    label: str
    category: str
    value: JsonValue
    normalized_value: str
    value_type: str
    unit: str | None
    material: bool
    machine_verification_status: str
    machine_confidence: str
    evidence_ids: tuple[str, ...]
    state: str
    observed_at: str


@dataclass(frozen=True)
class ReviewEvent:
    """Append-only reviewer/appraiser event for a candidate, fact, or conclusion."""

    event_id: str
    action: str
    target_type: str
    target_id: str
    field_key: str
    actor_id: str
    actor_name: str
    actor_role: str
    occurred_at: str
    reason: str
    prior_value: JsonValue = None
    resulting_value: JsonValue = None
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CanonicalFact:
    """One fact revision accepted or entered by an appraiser."""

    fact_id: str
    field_key: str
    label: str
    category: str
    value: JsonValue
    value_type: str
    unit: str | None
    material: bool
    state: str
    origin: str
    candidate_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    review_event_ids: tuple[str, ...]
    created_at: str
    supersedes_fact_id: str | None = None


@dataclass(frozen=True)
class FactConflict:
    """A preserved disagreement between candidate assertions."""

    conflict_id: str
    field_key: str
    candidate_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    status: str
    material: bool
    reason: str
    resolution_event_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class FactGroup:
    """Reference-only grouping over canonical fact IDs."""

    group_key: str
    fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class AssignmentContext:
    """Assignment facts and contacts without duplicating Falcon order state."""

    fact_ids: tuple[str, ...]
    contact_references: tuple[EntityReference, ...] = ()


@dataclass(frozen=True)
class SubjectProperty:
    """Subject identity plus typed fact groups referencing the canonical ledger."""

    property_reference: EntityReference | None
    identity_fact_ids: tuple[str, ...]
    characteristic_groups: tuple[FactGroup, ...]
    ownership_references: tuple[EntityReference, ...] = ()


@dataclass(frozen=True)
class ComparableReference:
    """Bounded reference to candidate or selected comparable intelligence."""

    reference_id: str
    comparable_id: str
    comparable_type: str
    selection_status: str
    property_id: str | None = None
    knowledge_object_id: str | None = None
    source_assignment_id: str | None = None
    evidence_ids: tuple[str, ...] = ()
    adjustment_reference_ids: tuple[str, ...] = ()
    qualitative_comparison_reference_ids: tuple[str, ...] = ()
    freshness: str = "unknown"
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class KnowledgeReference:
    """Reference to market observations, prior-firm knowledge, or graph objects."""

    reference_id: str
    reference_type: str
    relationship: str
    evidence_ids: tuple[str, ...] = ()
    freshness: str = "unknown"
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReportSectionReference:
    """Reference to a future report section; no narrative body is embedded."""

    section_id: str
    section_type: str
    status: str
    fact_ids: tuple[str, ...] = ()
    conclusion_ids: tuple[str, ...] = ()
    source_document_id: str | None = None


@dataclass(frozen=True)
class AppraiserConclusion:
    """Professional conclusion kept structurally separate from observed facts."""

    conclusion_id: str
    conclusion_type: str
    area: str
    statement: str
    status: str
    authored_by: str
    authored_at: str
    supporting_fact_ids: tuple[str, ...] = ()
    supporting_evidence_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadinessRequirement:
    """Deterministic minimum fact requirement for an appraisal area."""

    area: str
    field_keys: tuple[str, ...]
    blocking: bool


@dataclass(frozen=True)
class ReadinessIssue:
    """One explainable issue affecting analysis readiness."""

    issue_id: str
    area: str
    issue_type: str
    severity: str
    field_keys: tuple[str, ...]
    related_ids: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class AreaReadiness:
    """Readiness result for one assignment/report area."""

    area: str
    status: str
    required_field_keys: tuple[str, ...]
    current_fact_ids: tuple[str, ...]
    issue_ids: tuple[str, ...]


@dataclass(frozen=True)
class AnalysisReadiness:
    """Deterministic readiness result; never an appraisal conclusion."""

    overall_status: str
    calculated_at: str
    blocking_issue_ids: tuple[str, ...]
    nonblocking_issue_ids: tuple[str, ...]
    areas: tuple[AreaReadiness, ...]
    issues: tuple[ReadinessIssue, ...]


@dataclass(frozen=True)
class CandidateEvidenceBundle:
    """Reusable composition output from existing extraction and verification models."""

    sources: tuple[SourceReference, ...]
    evidence: tuple[EvidenceReference, ...]
    candidates: tuple[CandidateAssertion, ...]


@dataclass(frozen=True)
class AppraiserFactInput:
    """Input for a fact entered directly by an appraiser rather than extracted."""

    field_key: str
    label: str
    category: str
    value: JsonValue
    value_type: str
    unit: str | None
    material: bool
    actor_id: str
    actor_name: str
    actor_role: str
    occurred_at: str
    reason: str
    evidence_ids: tuple[str, ...] = ()
    supersedes_fact_id: str | None = None


@dataclass(frozen=True)
class AppraiserConclusionInput:
    """Input for an explicitly authored professional conclusion."""

    conclusion_type: str
    area: str
    statement: str
    status: str
    actor_id: str
    actor_name: str
    actor_role: str
    occurred_at: str
    reason: str
    supporting_fact_ids: tuple[str, ...] = ()
    supporting_evidence_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssignmentIntelligenceRecord:
    """Canonical composed view for one appraisal assignment."""

    identity: RecordIdentity
    tenant_id: str
    local_assignment_key: str
    falcon_assignment_reference: EntityReference | None
    sources: tuple[SourceReference, ...]
    evidence: tuple[EvidenceReference, ...]
    candidates: tuple[CandidateAssertion, ...]
    review_events: tuple[ReviewEvent, ...]
    facts: tuple[CanonicalFact, ...]
    current_fact_ids: tuple[str, ...]
    conflicts: tuple[FactConflict, ...]
    assignment_context: AssignmentContext
    subject_property: SubjectProperty
    comparable_references: tuple[ComparableReference, ...]
    market_references: tuple[KnowledgeReference, ...]
    prior_knowledge_references: tuple[KnowledgeReference, ...]
    report_section_references: tuple[ReportSectionReference, ...]
    conclusions: tuple[AppraiserConclusion, ...]
    readiness: AnalysisReadiness

    def __post_init__(self) -> None:
        _validate_record(self)

    def current_fact(self, field_key: str) -> CanonicalFact | None:
        """Return the current fact for a key, if one exists."""

        current_ids = set(self.current_fact_ids)
        return next(
            (fact for fact in self.facts if fact.fact_id in current_ids and fact.field_key == field_key),
            None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize in stable key/list order for storage or Falcon exchange."""

        return {
            "identity": _plain(self.identity),
            "tenant_id": self.tenant_id,
            "local_assignment_key": self.local_assignment_key,
            "falcon_assignment_reference": (
                _plain(self.falcon_assignment_reference)
                if self.falcon_assignment_reference is not None
                else None
            ),
            "sources": [_plain(item) for item in sorted(self.sources, key=lambda item: item.source_id)],
            "evidence": [_plain(item) for item in sorted(self.evidence, key=lambda item: item.evidence_id)],
            "candidates": [_plain(item) for item in sorted(self.candidates, key=lambda item: item.candidate_id)],
            "review_events": [
                _plain(item)
                for item in sorted(self.review_events, key=lambda item: (item.occurred_at, item.event_id))
            ],
            "facts": [_plain(item) for item in sorted(self.facts, key=lambda item: item.fact_id)],
            "current_fact_ids": sorted(self.current_fact_ids),
            "conflicts": [_plain(item) for item in sorted(self.conflicts, key=lambda item: item.conflict_id)],
            "assignment_context": _plain(self.assignment_context),
            "subject_property": _plain(self.subject_property),
            "comparable_references": [
                _plain(item)
                for item in sorted(self.comparable_references, key=lambda item: item.reference_id)
            ],
            "market_references": [
                _plain(item) for item in sorted(self.market_references, key=lambda item: item.reference_id)
            ],
            "prior_knowledge_references": [
                _plain(item)
                for item in sorted(self.prior_knowledge_references, key=lambda item: item.reference_id)
            ],
            "report_section_references": [
                _plain(item)
                for item in sorted(self.report_section_references, key=lambda item: item.section_id)
            ],
            "conclusions": [
                _plain(item) for item in sorted(self.conclusions, key=lambda item: item.conclusion_id)
            ],
            "readiness": _plain(self.readiness),
        }

    def to_json(self) -> str:
        """Return deterministic, newline-terminated JSON."""

        return json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AssignmentIntelligenceRecord":
        """Rebuild and validate a record from its serialized contract."""

        return _record_from_dict(payload)

    @classmethod
    def from_json(cls, payload: str) -> "AssignmentIntelligenceRecord":
        """Rebuild a record from deterministic JSON."""

        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True)
class _FieldSpec:
    field_key: str
    label: str
    category: str
    material: bool = True
    value_type: str = "string"
    unit: str | None = None


FIELD_SPECS: dict[str, _FieldSpec] = {
    "report_title": _FieldSpec("report.title", "Report title", "report", False),
    "report_type": _FieldSpec("assignment.report_format", "Report format", "assignment"),
    "property_address": _FieldSpec("subject.address", "Property address", "subject_identity"),
    "property_type": _FieldSpec("subject.property_type", "Property type", "subject_identity"),
    "client": _FieldSpec("assignment.client", "Client", "assignment"),
    "intended_user": _FieldSpec("assignment.intended_user", "Intended user", "assignment"),
    "intended_use": _FieldSpec("assignment.intended_use", "Intended use", "assignment"),
    "effective_date": _FieldSpec(
        "assignment.effective_date_requirement", "Effective date requirement", "assignment"
    ),
    "report_date": _FieldSpec(
        "assignment.report_date_requirement", "Report date requirement", "assignment", False
    ),
    "inspection_date": _FieldSpec("assignment.inspection_date", "Inspection date", "inspection", False),
    "appraiser_name": _FieldSpec(
        "assignment.signing_appraiser", "Signing appraiser", "professional_review"
    ),
    "reviewer_name": _FieldSpec("assignment.reviewer", "Reviewer", "professional_review", False),
    "sales_comparison_approach": _FieldSpec(
        "analysis.approaches.sales_comparison", "Sales comparison approach referenced", "analysis", False
    ),
    "income_approach": _FieldSpec(
        "analysis.approaches.income", "Income approach referenced", "analysis", False
    ),
    "cost_approach": _FieldSpec(
        "analysis.approaches.cost", "Cost approach referenced", "analysis", False
    ),
    "extraordinary_assumptions_present": _FieldSpec(
        "assignment.extraordinary_assumptions_present",
        "Extraordinary assumptions present",
        "assignment",
    ),
    "hypothetical_conditions_present": _FieldSpec(
        "assignment.hypothetical_conditions_present", "Hypothetical conditions present", "assignment"
    ),
    "certification_section_present": _FieldSpec(
        "report.certification_section_present", "Certification section present", "report", False
    ),
    "limiting_conditions_section_present": _FieldSpec(
        "report.limiting_conditions_section_present",
        "Limiting conditions section present",
        "report",
        False,
    ),
}

SUBJECT_IDENTITY_KEYS = {
    "subject.property_id",
    "subject.name",
    "subject.address",
    "subject.parcel_identifiers",
    "subject.coordinates",
    "subject.property_type",
    "subject.property_subtype",
    "subject.alternate_identifiers",
}

DEFAULT_READINESS_REQUIREMENTS = (
    ReadinessRequirement(
        area="assignment_context",
        field_keys=(
            "assignment.client",
            "assignment.intended_user",
            "assignment.intended_use",
            "assignment.interest_appraised",
            "assignment.effective_date_requirement",
        ),
        blocking=True,
    ),
    ReadinessRequirement(
        area="subject_identity",
        field_keys=("subject.address", "subject.property_type"),
        blocking=True,
    ),
    ReadinessRequirement(area="site", field_keys=("subject.site_area",), blocking=False),
    ReadinessRequirement(
        area="improvements", field_keys=("subject.building_area",), blocking=False
    ),
    ReadinessRequirement(
        area="professional_review",
        field_keys=("assignment.signing_appraiser",),
        blocking=False,
    ),
)


def build_candidate_evidence_bundle(
    extracted_candidate: Mapping[str, Any] | Any,
    *,
    extracted_at: str,
    extractor_name: str = "falcon_historical_knowledge",
    extractor_version: str = "1",
) -> CandidateEvidenceBundle:
    """Adapt existing extraction and deterministic verification into V1 candidates."""

    _parse_timestamp(extracted_at)
    payload = (
        asdict(extracted_candidate)
        if not isinstance(extracted_candidate, Mapping)
        else dict(extracted_candidate)
    )
    file_id = str(payload.get("file_id") or "unknown-source")
    file_name = str(payload.get("file_name") or file_id)
    file_path = str(payload.get("file_path") or file_name)
    source_id = _stable_id("source", file_id)
    source = SourceReference(
        source_id=source_id,
        source_type="source_document",
        display_label=file_name,
        safe_reference=Path(file_path).name,
        document_id=file_id,
        content_included=False,
    )

    verification = verify_report_candidate(payload, timestamp=extracted_at)
    verification_by_field = {fact.field_name: fact for fact in verification.facts}
    evidence_by_source_field = collect_candidate_evidence(payload)
    grouped: dict[tuple[str, str, str], list[VerificationEvidence]] = defaultdict(list)
    for source_field_key, items in evidence_by_source_field.items():
        spec = _field_spec(source_field_key)
        for item in items:
            normalized = item.normalized_value or normalize_fact_value(source_field_key, item.value or "")
            if not normalized:
                continue
            grouped[(spec.field_key, source_field_key, normalized)].append(item)

    evidence_items: dict[str, EvidenceReference] = {}
    candidates: list[CandidateAssertion] = []
    for (field_key, source_field_key, normalized), items in sorted(grouped.items()):
        spec = _field_spec(source_field_key)
        candidate_evidence_ids: list[str] = []
        for item in sorted(items, key=lambda value: value.source_reference):
            evidence_id = _stable_id(
                "evidence",
                "|".join((source_id, item.source_reference, source_field_key, normalized)),
            )
            evidence_items[evidence_id] = EvidenceReference(
                evidence_id=evidence_id,
                source_id=source_id,
                field_key=field_key,
                source_field_key=source_field_key,
                candidate_reference=item.source_reference,
                locator=_locator_from_source_label(item.source_label),
                extraction_method=item.method,
                extracted_at=extracted_at,
                confidence=item.confidence,
                extractor_name=extractor_name,
                extractor_version=extractor_version,
                source_excerpt=None,
                freshness="unknown",
                quality=_quality_from_source_type(item.source_type),
            )
            candidate_evidence_ids.append(evidence_id)

        machine_fact = verification_by_field.get(source_field_key)
        machine_status = machine_fact.verification_status if machine_fact else "probable"
        machine_confidence = machine_fact.confidence if machine_fact else "medium"
        candidate_id = _stable_id("candidate", "|".join((file_id, field_key, normalized)))
        candidates.append(
            CandidateAssertion(
                candidate_id=candidate_id,
                field_key=field_key,
                source_field_key=source_field_key,
                label=spec.label,
                category=spec.category,
                value=next((item.value for item in items if item.value is not None), None),
                normalized_value=normalized,
                value_type=spec.value_type,
                unit=spec.unit,
                material=spec.material,
                machine_verification_status=machine_status,
                machine_confidence=machine_confidence,
                evidence_ids=tuple(sorted(set(candidate_evidence_ids))),
                state="extracted_candidate",
                observed_at=extracted_at,
            )
        )

    candidates = _mark_candidate_conflicts(candidates)
    return CandidateEvidenceBundle(
        sources=(source,),
        evidence=tuple(sorted(evidence_items.values(), key=lambda item: item.evidence_id)),
        candidates=tuple(sorted(candidates, key=lambda item: item.candidate_id)),
    )


def build_candidate_review_event(
    candidate: CandidateAssertion,
    *,
    action: str,
    actor_id: str,
    actor_name: str,
    actor_role: str,
    occurred_at: str,
    reason: str,
    corrected_value: JsonValue = None,
    evidence_ids: Sequence[str] = (),
) -> ReviewEvent:
    """Build a deterministic human review event for one extracted candidate."""

    if action not in {
        "candidate_verified",
        "candidate_corrected",
        "candidate_rejected",
        "candidate_deferred",
    }:
        raise ValueError(f"Unsupported candidate review action: {action}")
    if action == "candidate_corrected" and corrected_value is None:
        raise ValueError("corrected_value is required for candidate_corrected.")
    resulting_value = (
        corrected_value
        if action == "candidate_corrected"
        else candidate.value
        if action == "candidate_verified"
        else None
    )
    event_id = _stable_id(
        "review",
        json.dumps(
            [candidate.candidate_id, action, actor_id, occurred_at, reason, resulting_value],
            sort_keys=True,
        ),
    )
    return ReviewEvent(
        event_id=event_id,
        action=action,
        target_type="candidate",
        target_id=candidate.candidate_id,
        field_key=candidate.field_key,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        occurred_at=occurred_at,
        reason=reason,
        prior_value=candidate.value,
        resulting_value=resulting_value,
        evidence_ids=tuple(sorted(set(evidence_ids))),
    )


def build_assignment_intelligence_record(
    *,
    tenant_id: str,
    local_assignment_key: str,
    candidate_bundles: Sequence[CandidateEvidenceBundle],
    review_events: Sequence[ReviewEvent],
    created_at: str,
    updated_at: str,
    falcon_assignment_reference: EntityReference | None = None,
    record_id: str | None = None,
    record_version: int = 1,
    lineage: RecordLineage | None = None,
    appraiser_facts: Sequence[AppraiserFactInput] = (),
    appraiser_conclusions: Sequence[AppraiserConclusionInput] = (),
    property_reference: EntityReference | None = None,
    assignment_contacts: Sequence[EntityReference] = (),
    ownership_references: Sequence[EntityReference] = (),
    comparable_references: Sequence[ComparableReference] = (),
    market_references: Sequence[KnowledgeReference] = (),
    prior_knowledge_references: Sequence[KnowledgeReference] = (),
    report_section_references: Sequence[ReportSectionReference] = (),
    readiness_requirements: Sequence[ReadinessRequirement] = DEFAULT_READINESS_REQUIREMENTS,
) -> AssignmentIntelligenceRecord:
    """Assemble one immutable V1 record from existing models and explicit human actions."""

    _require_text("tenant_id", tenant_id)
    _require_text("local_assignment_key", local_assignment_key)
    _parse_timestamp(created_at)
    _parse_timestamp(updated_at)
    if record_version < 1:
        raise ValueError("record_version must be at least 1.")

    sources = _dedupe_by_id(
        (source for bundle in candidate_bundles for source in bundle.sources), "source_id"
    )
    evidence = _dedupe_by_id(
        (item for bundle in candidate_bundles for item in bundle.evidence), "evidence_id"
    )
    candidate_list = list(
        _dedupe_by_id(
            (candidate for bundle in candidate_bundles for candidate in bundle.candidates),
            "candidate_id",
        )
    )
    candidates_by_id = {candidate.candidate_id: candidate for candidate in candidate_list}
    evidence_ids = {item.evidence_id for item in evidence}
    facts: list[CanonicalFact] = []
    current_by_field: dict[str, str] = {}
    applied_events: list[ReviewEvent] = []

    for event in sorted(review_events, key=lambda item: (item.occurred_at, item.event_id)):
        _validate_review_event(event)
        candidate = candidates_by_id.get(event.target_id)
        if candidate is None:
            raise ValueError(f"Review event references unknown candidate: {event.target_id}")
        if event.field_key != candidate.field_key:
            raise ValueError("Review event field_key does not match its candidate.")
        _require_known_ids("review event evidence", event.evidence_ids, evidence_ids)
        candidate_list = _replace_candidate_state(candidate_list, candidate.candidate_id, _candidate_state(event.action))
        candidates_by_id = {item.candidate_id: item for item in candidate_list}
        if event.action == "candidate_rejected":
            _supersede_candidate_fact(
                facts,
                current_by_field,
                candidate.field_key,
                candidate.candidate_id,
            )
            applied_events.append(event)
            continue
        if event.action == "candidate_deferred":
            applied_events.append(event)
            continue

        _supersede_current_fact(facts, current_by_field, candidate.field_key)
        state = "corrected" if event.action == "candidate_corrected" else "verified"
        value = event.resulting_value
        fact_id = _stable_id("fact", event.event_id)
        prior_fact_id = _latest_superseded_fact_id(facts, candidate.field_key)
        fact = CanonicalFact(
            fact_id=fact_id,
            field_key=candidate.field_key,
            label=candidate.label,
            category=candidate.category,
            value=value,
            value_type=_json_value_type(value, candidate.value_type),
            unit=candidate.unit,
            material=candidate.material,
            state=state,
            origin="corrected_candidate" if state == "corrected" else "verified_candidate",
            candidate_ids=(candidate.candidate_id,),
            evidence_ids=tuple(sorted(set(candidate.evidence_ids + event.evidence_ids))),
            review_event_ids=(event.event_id,),
            created_at=event.occurred_at,
            supersedes_fact_id=prior_fact_id,
        )
        facts.append(fact)
        current_by_field[candidate.field_key] = fact.fact_id
        applied_events.append(event)

    for fact_input in sorted(appraiser_facts, key=lambda item: (item.occurred_at, item.field_key)):
        _validate_appraiser_fact_input(fact_input)
        _require_known_ids("appraiser fact evidence", fact_input.evidence_ids, evidence_ids)
        prior_fact_id = current_by_field.get(fact_input.field_key)
        if prior_fact_id and fact_input.supersedes_fact_id != prior_fact_id:
            raise ValueError(
                f"Appraiser-entered fact for {fact_input.field_key} must explicitly supersede {prior_fact_id}."
            )
        if fact_input.supersedes_fact_id and fact_input.supersedes_fact_id != prior_fact_id:
            raise ValueError("supersedes_fact_id is not the current fact for the field.")
        _supersede_current_fact(facts, current_by_field, fact_input.field_key)
        event_id = _stable_id(
            "review",
            json.dumps(
                [
                    "appraiser_fact_entered",
                    fact_input.field_key,
                    fact_input.actor_id,
                    fact_input.occurred_at,
                    fact_input.reason,
                    fact_input.value,
                ],
                sort_keys=True,
            ),
        )
        event = ReviewEvent(
            event_id=event_id,
            action="appraiser_fact_entered",
            target_type="fact",
            target_id=_stable_id("fact", event_id),
            field_key=fact_input.field_key,
            actor_id=fact_input.actor_id,
            actor_name=fact_input.actor_name,
            actor_role=fact_input.actor_role,
            occurred_at=fact_input.occurred_at,
            reason=fact_input.reason,
            prior_value=None,
            resulting_value=fact_input.value,
            evidence_ids=tuple(sorted(set(fact_input.evidence_ids))),
        )
        fact = CanonicalFact(
            fact_id=event.target_id,
            field_key=fact_input.field_key,
            label=fact_input.label,
            category=fact_input.category,
            value=fact_input.value,
            value_type=_json_value_type(fact_input.value, fact_input.value_type),
            unit=fact_input.unit,
            material=fact_input.material,
            state="appraiser_entered",
            origin="appraiser_entry",
            candidate_ids=(),
            evidence_ids=tuple(sorted(set(fact_input.evidence_ids))),
            review_event_ids=(event.event_id,),
            created_at=fact_input.occurred_at,
            supersedes_fact_id=prior_fact_id,
        )
        facts.append(fact)
        current_by_field[fact.field_key] = fact.fact_id
        applied_events.append(event)

    conflicts = _build_conflicts(candidate_list, applied_events)
    conclusions, conclusion_events = _build_conclusions(
        appraiser_conclusions,
        fact_ids={fact.fact_id for fact in facts},
        evidence_ids=evidence_ids,
    )
    applied_events.extend(conclusion_events)

    current_fact_ids = tuple(sorted(current_by_field.values()))
    current_facts = tuple(fact for fact in facts if fact.fact_id in set(current_fact_ids))
    readiness = calculate_analysis_readiness(
        facts=current_facts,
        candidates=tuple(candidate_list),
        conflicts=conflicts,
        evidence=evidence,
        requirements=readiness_requirements,
        calculated_at=updated_at,
    )
    lifecycle_state = "analysis_ready" if readiness.overall_status == "ready" else (
        "in_review" if applied_events else "draft"
    )
    stable_record_id = record_id or _stable_id(
        "air",
        "|".join(
            (
                tenant_id,
                falcon_assignment_reference.reference_id
                if falcon_assignment_reference is not None
                else local_assignment_key,
            )
        ),
    )
    identity = RecordIdentity(
        record_id=stable_record_id,
        record_version=record_version,
        schema_version=ASSIGNMENT_INTELLIGENCE_RECORD_SCHEMA_VERSION,
        created_at=created_at,
        updated_at=updated_at,
        lifecycle_state=lifecycle_state,
        lineage=lineage or RecordLineage(),
    )
    assignment_context = AssignmentContext(
        fact_ids=tuple(
            sorted(
                fact.fact_id
                for fact in current_facts
                if fact.field_key.startswith(("assignment.", "report."))
            )
        ),
        contact_references=tuple(sorted(assignment_contacts, key=lambda item: item.reference_id)),
    )
    subject_property = SubjectProperty(
        property_reference=property_reference,
        identity_fact_ids=tuple(
            sorted(fact.fact_id for fact in current_facts if fact.field_key in SUBJECT_IDENTITY_KEYS)
        ),
        characteristic_groups=_build_characteristic_groups(current_facts),
        ownership_references=tuple(sorted(ownership_references, key=lambda item: item.reference_id)),
    )
    return AssignmentIntelligenceRecord(
        identity=identity,
        tenant_id=tenant_id,
        local_assignment_key=local_assignment_key,
        falcon_assignment_reference=falcon_assignment_reference,
        sources=tuple(sources),
        evidence=tuple(evidence),
        candidates=tuple(candidate_list),
        review_events=tuple(sorted(applied_events, key=lambda item: (item.occurred_at, item.event_id))),
        facts=tuple(sorted(facts, key=lambda item: item.fact_id)),
        current_fact_ids=current_fact_ids,
        conflicts=conflicts,
        assignment_context=assignment_context,
        subject_property=subject_property,
        comparable_references=tuple(sorted(comparable_references, key=lambda item: item.reference_id)),
        market_references=tuple(sorted(market_references, key=lambda item: item.reference_id)),
        prior_knowledge_references=tuple(
            sorted(prior_knowledge_references, key=lambda item: item.reference_id)
        ),
        report_section_references=tuple(
            sorted(report_section_references, key=lambda item: item.section_id)
        ),
        conclusions=conclusions,
        readiness=readiness,
    )


def calculate_analysis_readiness(
    *,
    facts: Sequence[CanonicalFact],
    candidates: Sequence[CandidateAssertion],
    conflicts: Sequence[FactConflict],
    evidence: Sequence[EvidenceReference],
    requirements: Sequence[ReadinessRequirement],
    calculated_at: str,
) -> AnalysisReadiness:
    """Calculate explainable, deterministic readiness without producing conclusions."""

    _parse_timestamp(calculated_at)
    current_by_field = {fact.field_key: fact for fact in facts if fact.state != "superseded"}
    evidence_by_id = {item.evidence_id: item for item in evidence}
    requirement_by_field: dict[str, ReadinessRequirement] = {}
    for requirement in requirements:
        for field_key in requirement.field_keys:
            requirement_by_field[field_key] = requirement

    issues: list[ReadinessIssue] = []
    for requirement in sorted(requirements, key=lambda item: item.area):
        for field_key in requirement.field_keys:
            if field_key in current_by_field:
                continue
            severity = "blocking" if requirement.blocking else "nonblocking"
            issues.append(
                _readiness_issue(
                    area=requirement.area,
                    issue_type="missing_required_fact",
                    severity=severity,
                    field_keys=(field_key,),
                    related_ids=(),
                    message=f"Required fact is missing: {field_key}.",
                )
            )

    for conflict in conflicts:
        if conflict.status != "unresolved":
            continue
        requirement = requirement_by_field.get(conflict.field_key)
        severity = "blocking" if conflict.material or (requirement and requirement.blocking) else "nonblocking"
        area = requirement.area if requirement else _area_for_field(conflict.field_key)
        issues.append(
            _readiness_issue(
                area=area,
                issue_type="unresolved_conflict",
                severity=severity,
                field_keys=(conflict.field_key,),
                related_ids=(conflict.conflict_id,),
                message=f"Conflicting candidate values remain unresolved for {conflict.field_key}.",
            )
        )

    conflict_candidate_ids = {
        candidate_id
        for conflict in conflicts
        if conflict.status == "unresolved"
        for candidate_id in conflict.candidate_ids
    }
    for candidate in candidates:
        if candidate.candidate_id in conflict_candidate_ids:
            continue
        if candidate.state == "deferred":
            requirement = requirement_by_field.get(candidate.field_key)
            severity = "blocking" if requirement and requirement.blocking else "nonblocking"
            issues.append(
                _readiness_issue(
                    area=requirement.area if requirement else _area_for_field(candidate.field_key),
                    issue_type="deferred_review_candidate",
                    severity=severity,
                    field_keys=(candidate.field_key,),
                    related_ids=(candidate.candidate_id,),
                    message=f"Candidate review was deferred: {candidate.field_key}.",
                )
            )
            continue
        if not candidate.material:
            continue
        if candidate.state not in {"extracted_candidate", "unresolved_conflict"}:
            continue
        requirement = requirement_by_field.get(candidate.field_key)
        severity = "blocking" if requirement and requirement.blocking else "nonblocking"
        issues.append(
            _readiness_issue(
                area=requirement.area if requirement else _area_for_field(candidate.field_key),
                issue_type="unverified_material_candidate",
                severity=severity,
                field_keys=(candidate.field_key,),
                related_ids=(candidate.candidate_id,),
                message=f"Material candidate still requires an appraiser decision: {candidate.field_key}.",
            )
        )

    for fact in facts:
        if fact.origin == "appraiser_entry":
            continue
        supporting = tuple(evidence_by_id[item] for item in fact.evidence_ids if item in evidence_by_id)
        requirement = requirement_by_field.get(fact.field_key)
        severity = "blocking" if requirement and requirement.blocking else "nonblocking"
        if supporting and all(item.confidence in {"low", "missing", "conflicting"} for item in supporting):
            issues.append(
                _readiness_issue(
                    area=requirement.area if requirement else _area_for_field(fact.field_key),
                    issue_type="weak_evidence",
                    severity=severity,
                    field_keys=(fact.field_key,),
                    related_ids=fact.evidence_ids,
                    message=f"Current fact relies only on weak evidence: {fact.field_key}.",
                )
            )
        stale_ids = tuple(item.evidence_id for item in supporting if item.freshness == "stale")
        if stale_ids:
            issues.append(
                _readiness_issue(
                    area=requirement.area if requirement else _area_for_field(fact.field_key),
                    issue_type="stale_evidence",
                    severity=severity,
                    field_keys=(fact.field_key,),
                    related_ids=stale_ids,
                    message=f"Current fact has stale supporting evidence: {fact.field_key}.",
                )
            )

    issues = sorted(issues, key=lambda item: item.issue_id)
    issues_by_area: dict[str, list[ReadinessIssue]] = defaultdict(list)
    for issue in issues:
        issues_by_area[issue.area].append(issue)
    areas: list[AreaReadiness] = []
    area_names = sorted({item.area for item in requirements}.union(issues_by_area))
    for area in area_names:
        requirement = next((item for item in requirements if item.area == area), None)
        area_issues = issues_by_area.get(area, [])
        status = "blocked" if any(item.severity == "blocking" for item in area_issues) else (
            "needs_review" if area_issues else "ready"
        )
        required = requirement.field_keys if requirement else ()
        areas.append(
            AreaReadiness(
                area=area,
                status=status,
                required_field_keys=tuple(required),
                current_fact_ids=tuple(
                    sorted(
                        fact.fact_id
                        for field_key, fact in current_by_field.items()
                        if field_key in required or _area_for_field(field_key) == area
                    )
                ),
                issue_ids=tuple(sorted(item.issue_id for item in area_issues)),
            )
        )
    blocking = tuple(item.issue_id for item in issues if item.severity == "blocking")
    nonblocking = tuple(item.issue_id for item in issues if item.severity == "nonblocking")
    overall = "blocked" if blocking else "needs_review" if nonblocking else "ready"
    return AnalysisReadiness(
        overall_status=overall,
        calculated_at=calculated_at,
        blocking_issue_ids=blocking,
        nonblocking_issue_ids=nonblocking,
        areas=tuple(areas),
        issues=tuple(issues),
    )


def save_assignment_intelligence_record(
    record: AssignmentIntelligenceRecord,
    output_path: str | Path,
) -> Path:
    """Save deterministic JSON; callers must choose an ignored local output path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.to_json(), encoding="utf-8")
    return path


def _field_spec(source_field_key: str) -> _FieldSpec:
    if source_field_key in FIELD_SPECS:
        return FIELD_SPECS[source_field_key]
    safe_key = re.sub(r"[^a-z0-9_]+", "_", source_field_key.lower()).strip("_") or "unknown"
    return _FieldSpec(
        field_key=f"extended.{safe_key}",
        label=source_field_key.replace("_", " ").title(),
        category="extended",
        material=False,
    )


def _mark_candidate_conflicts(candidates: list[CandidateAssertion]) -> list[CandidateAssertion]:
    by_field: dict[str, list[CandidateAssertion]] = defaultdict(list)
    for candidate in candidates:
        by_field[candidate.field_key].append(candidate)
    conflicting_ids = {
        candidate.candidate_id
        for values in by_field.values()
        if len({item.normalized_value for item in values}) > 1
        for candidate in values
    }
    return [
        replace(candidate, state="unresolved_conflict")
        if candidate.candidate_id in conflicting_ids
        else candidate
        for candidate in candidates
    ]


def _build_conflicts(
    candidates: Sequence[CandidateAssertion],
    events: Sequence[ReviewEvent],
) -> tuple[FactConflict, ...]:
    by_field: dict[str, list[CandidateAssertion]] = defaultdict(list)
    for candidate in candidates:
        by_field[candidate.field_key].append(candidate)
    event_by_candidate: dict[str, list[ReviewEvent]] = defaultdict(list)
    for event in events:
        if event.target_type == "candidate":
            event_by_candidate[event.target_id].append(event)
    conflicts: list[FactConflict] = []
    for field_key, field_candidates in sorted(by_field.items()):
        if len({candidate.normalized_value for candidate in field_candidates}) <= 1:
            continue
        non_rejected = [candidate for candidate in field_candidates if candidate.state != "rejected"]
        accepted = [candidate for candidate in non_rejected if candidate.state in {"accepted", "corrected"}]
        status = "resolved" if len(non_rejected) == 1 and len(accepted) == 1 else "unresolved"
        candidate_ids = tuple(sorted(candidate.candidate_id for candidate in field_candidates))
        resolution_event_ids = tuple(
            sorted(
                event.event_id
                for candidate in field_candidates
                for event in event_by_candidate.get(candidate.candidate_id, ())
                if event.action in {"candidate_verified", "candidate_corrected", "candidate_rejected"}
            )
        )
        conflicts.append(
            FactConflict(
                conflict_id=_stable_id("conflict", "|".join((field_key, *candidate_ids))),
                field_key=field_key,
                candidate_ids=candidate_ids,
                evidence_ids=tuple(
                    sorted({evidence_id for candidate in field_candidates for evidence_id in candidate.evidence_ids})
                ),
                status=status,
                material=any(candidate.material for candidate in field_candidates),
                reason=(
                    "All competing values except one were explicitly rejected."
                    if status == "resolved"
                    else "Distinct normalized candidate values require an explicit appraiser resolution."
                ),
                resolution_event_ids=resolution_event_ids if status == "resolved" else (),
            )
        )
    return tuple(conflicts)


def _build_conclusions(
    inputs: Sequence[AppraiserConclusionInput],
    *,
    fact_ids: set[str],
    evidence_ids: set[str],
) -> tuple[tuple[AppraiserConclusion, ...], tuple[ReviewEvent, ...]]:
    conclusions: list[AppraiserConclusion] = []
    events: list[ReviewEvent] = []
    for item in sorted(inputs, key=lambda value: (value.occurred_at, value.area, value.conclusion_type)):
        _parse_timestamp(item.occurred_at)
        _require_text("conclusion statement", item.statement)
        _require_text("conclusion reason", item.reason)
        _require_known_ids("conclusion supporting facts", item.supporting_fact_ids, fact_ids)
        _require_known_ids("conclusion evidence", item.supporting_evidence_ids, evidence_ids)
        conclusion_id = _stable_id(
            "conclusion",
            json.dumps(
                [item.conclusion_type, item.area, item.statement, item.actor_id, item.occurred_at],
                sort_keys=True,
            ),
        )
        event_id = _stable_id("review", f"conclusion_entered|{conclusion_id}|{item.reason}")
        conclusions.append(
            AppraiserConclusion(
                conclusion_id=conclusion_id,
                conclusion_type=item.conclusion_type,
                area=item.area,
                statement=item.statement,
                status=item.status,
                authored_by=item.actor_id,
                authored_at=item.occurred_at,
                supporting_fact_ids=tuple(sorted(set(item.supporting_fact_ids))),
                supporting_evidence_ids=tuple(sorted(set(item.supporting_evidence_ids))),
                notes=tuple(item.notes),
            )
        )
        events.append(
            ReviewEvent(
                event_id=event_id,
                action="conclusion_entered",
                target_type="conclusion",
                target_id=conclusion_id,
                field_key=f"conclusion.{item.area}.{item.conclusion_type}",
                actor_id=item.actor_id,
                actor_name=item.actor_name,
                actor_role=item.actor_role,
                occurred_at=item.occurred_at,
                reason=item.reason,
                resulting_value=item.statement,
                evidence_ids=tuple(sorted(set(item.supporting_evidence_ids))),
            )
        )
    return tuple(conclusions), tuple(events)


def _build_characteristic_groups(facts: Sequence[CanonicalFact]) -> tuple[FactGroup, ...]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for fact in facts:
        if fact.field_key in SUBJECT_IDENTITY_KEYS or fact.field_key.startswith(("assignment.", "report.")):
            continue
        if fact.field_key.startswith("subject."):
            suffix = fact.field_key.removeprefix("subject.")
            if suffix.startswith(("site", "zoning", "flood", "access", "utilities", "parking")):
                group = "physical_legal"
            elif suffix.startswith(("income", "occupancy", "tenancy", "tax", "sale")):
                group = "economic_operational"
            else:
                group = "improvements"
        else:
            group = fact.category
        grouped[group].append(fact.fact_id)
    return tuple(
        FactGroup(group_key=group, fact_ids=tuple(sorted(fact_ids)))
        for group, fact_ids in sorted(grouped.items())
    )


def _readiness_issue(
    *,
    area: str,
    issue_type: str,
    severity: str,
    field_keys: tuple[str, ...],
    related_ids: tuple[str, ...],
    message: str,
) -> ReadinessIssue:
    return ReadinessIssue(
        issue_id=_stable_id(
            "issue", "|".join((area, issue_type, severity, *sorted(field_keys), *sorted(related_ids)))
        ),
        area=area,
        issue_type=issue_type,
        severity=severity,
        field_keys=tuple(sorted(field_keys)),
        related_ids=tuple(sorted(related_ids)),
        message=message,
    )


def _replace_candidate_state(
    candidates: list[CandidateAssertion], candidate_id: str, state: str
) -> list[CandidateAssertion]:
    return [replace(item, state=state) if item.candidate_id == candidate_id else item for item in candidates]


def _candidate_state(action: str) -> str:
    return {
        "candidate_verified": "accepted",
        "candidate_corrected": "corrected",
        "candidate_rejected": "rejected",
        "candidate_deferred": "deferred",
    }[action]


def _supersede_candidate_fact(
    facts: list[CanonicalFact],
    current_by_field: dict[str, str],
    field_key: str,
    candidate_id: str,
) -> None:
    """Supersede only a current fact created from the rejected candidate.

    Competing candidates share a field key. Rejecting one side of a conflict
    must not remove the fact promoted from the selected side.
    """

    current_fact_id = current_by_field.get(field_key)
    if current_fact_id is None:
        return
    current_fact = next((fact for fact in facts if fact.fact_id == current_fact_id), None)
    if current_fact is None or candidate_id not in current_fact.candidate_ids:
        return
    _supersede_current_fact(facts, current_by_field, field_key)


def _supersede_current_fact(
    facts: list[CanonicalFact], current_by_field: dict[str, str], field_key: str
) -> None:
    prior_id = current_by_field.pop(field_key, None)
    if prior_id is None:
        return
    for index, fact in enumerate(facts):
        if fact.fact_id == prior_id:
            facts[index] = replace(fact, state="superseded")
            return


def _latest_superseded_fact_id(facts: Sequence[CanonicalFact], field_key: str) -> str | None:
    matching = [fact for fact in facts if fact.field_key == field_key and fact.state == "superseded"]
    return matching[-1].fact_id if matching else None


def _locator_from_source_label(source_label: str) -> EvidenceLocator:
    page_match = re.search(r"\bpage\s+(\d+)\b", source_label, re.IGNORECASE)
    section = None
    if ";" in source_label:
        section = source_label.split(";", 1)[1].strip() or None
    return EvidenceLocator(
        page_number=int(page_match.group(1)) if page_match else None,
        section=section,
    )


def _quality_from_source_type(source_type: str) -> str:
    if source_type in {"final_report_pdf", "final_report_docx"}:
        return "primary_report"
    if source_type == "same_order_docx_companion":
        return "same_assignment_companion"
    if source_type in {"filename", "folder_intake_metadata", "derived_report_title"}:
        return "metadata_only"
    return "unknown"


def _area_for_field(field_key: str) -> str:
    if field_key.startswith("assignment."):
        return "assignment_context"
    if field_key in SUBJECT_IDENTITY_KEYS:
        return "subject_identity"
    if field_key.startswith("subject.site"):
        return "site"
    if field_key.startswith("subject."):
        return "improvements"
    if field_key.startswith("analysis."):
        return "analysis"
    if field_key.startswith("report."):
        return "report"
    return "extended"


def _validate_record(record: AssignmentIntelligenceRecord) -> None:
    _require_text("record_id", record.identity.record_id)
    _require_text("tenant_id", record.tenant_id)
    _require_text("local_assignment_key", record.local_assignment_key)
    if record.identity.schema_version != ASSIGNMENT_INTELLIGENCE_RECORD_SCHEMA_VERSION:
        raise ValueError("Unsupported Assignment Intelligence Record schema version.")
    if record.identity.record_version < 1:
        raise ValueError("record_version must be at least 1.")
    if record.identity.lifecycle_state not in LIFECYCLE_STATES:
        raise ValueError(f"Unsupported lifecycle state: {record.identity.lifecycle_state}")
    created_at = _parse_timestamp(record.identity.created_at)
    updated_at = _parse_timestamp(record.identity.updated_at)
    if updated_at < created_at:
        raise ValueError("updated_at cannot be earlier than created_at.")
    if (record.identity.lineage.previous_record_id is None) != (
        record.identity.lineage.previous_record_version is None
    ):
        raise ValueError("Record lineage requires both previous_record_id and previous_record_version.")
    if (
        record.identity.lineage.previous_record_version is not None
        and record.identity.lineage.previous_record_version >= record.identity.record_version
    ):
        raise ValueError("previous_record_version must be lower than record_version.")
    if record.identity.record_version > 1 and record.identity.lineage.previous_record_id is None:
        raise ValueError("Record versions after V1 require previous-version lineage.")
    if record.readiness.overall_status not in READINESS_STATES:
        raise ValueError(f"Unsupported readiness status: {record.readiness.overall_status}")
    if (record.identity.lifecycle_state == "analysis_ready") != (
        record.readiness.overall_status == "ready"
    ):
        raise ValueError("analysis_ready lifecycle must match ready analysis readiness.")

    source_ids = _unique_ids(record.sources, "source_id")
    evidence_ids = _unique_ids(record.evidence, "evidence_id")
    candidate_ids = _unique_ids(record.candidates, "candidate_id")
    event_ids = _unique_ids(record.review_events, "event_id")
    fact_ids = _unique_ids(record.facts, "fact_id")
    conclusion_ids = _unique_ids(record.conclusions, "conclusion_id")
    for source in record.sources:
        if source.content_included:
            raise ValueError("Assignment Intelligence Record V1 sources must remain metadata-only.")
    for item in record.evidence:
        if item.source_id not in source_ids:
            raise ValueError(f"Evidence references unknown source: {item.source_id}")
        _parse_timestamp(item.extracted_at)
        if item.locator.page_number is not None and item.locator.page_number < 1:
            raise ValueError("Evidence locator page_number must be greater than zero.")
    for candidate in record.candidates:
        if candidate.state not in CANDIDATE_STATES:
            raise ValueError(f"Unsupported candidate state: {candidate.state}")
        _validate_json_value(candidate.value)
        _parse_timestamp(candidate.observed_at)
        _require_known_ids("candidate evidence", candidate.evidence_ids, evidence_ids)
    for fact in record.facts:
        if fact.state not in FACT_STATES:
            raise ValueError(f"Unsupported fact state: {fact.state}")
        _validate_json_value(fact.value)
        _parse_timestamp(fact.created_at)
        _require_known_ids("fact candidates", fact.candidate_ids, candidate_ids)
        _require_known_ids("fact evidence", fact.evidence_ids, evidence_ids)
        _require_known_ids("fact review events", fact.review_event_ids, event_ids)
        if fact.supersedes_fact_id and fact.supersedes_fact_id not in fact_ids:
            raise ValueError(f"Fact supersedes unknown fact: {fact.supersedes_fact_id}")
    _require_known_ids("current facts", record.current_fact_ids, fact_ids)
    current_facts = tuple(
        fact for fact in record.facts if fact.fact_id in set(record.current_fact_ids)
    )
    current_field_keys = [fact.field_key for fact in current_facts]
    if len(current_field_keys) != len(set(current_field_keys)):
        raise ValueError("Only one current canonical fact is allowed per field_key.")
    if any(
        fact.state == "superseded"
        for fact in record.facts
        if fact.fact_id in set(record.current_fact_ids)
    ):
        raise ValueError("current_fact_ids cannot include superseded facts.")
    for conflict in record.conflicts:
        if conflict.status not in CONFLICT_STATES:
            raise ValueError(f"Unsupported conflict state: {conflict.status}")
        _require_known_ids("conflict candidates", conflict.candidate_ids, candidate_ids)
        _require_known_ids("conflict evidence", conflict.evidence_ids, evidence_ids)
        _require_known_ids("conflict resolution events", conflict.resolution_event_ids, event_ids)
    for conclusion in record.conclusions:
        _require_known_ids("conclusion facts", conclusion.supporting_fact_ids, fact_ids)
        _require_known_ids("conclusion evidence", conclusion.supporting_evidence_ids, evidence_ids)
    current_ids = set(record.current_fact_ids)
    _require_known_ids("assignment context facts", record.assignment_context.fact_ids, current_ids)
    _require_known_ids("subject identity facts", record.subject_property.identity_fact_ids, current_ids)
    for group in record.subject_property.characteristic_groups:
        _require_known_ids("subject characteristic facts", group.fact_ids, current_ids)
    for comparable in record.comparable_references:
        if comparable.selection_status not in COMPARABLE_SELECTION_STATES:
            raise ValueError(
                f"Unsupported comparable selection status: {comparable.selection_status}"
            )
        _require_known_ids("comparable evidence", comparable.evidence_ids, evidence_ids)
    for reference in record.market_references + record.prior_knowledge_references:
        _require_known_ids("knowledge reference evidence", reference.evidence_ids, evidence_ids)
    for section in record.report_section_references:
        _require_known_ids("report section facts", section.fact_ids, fact_ids)
        _require_known_ids("report section conclusions", section.conclusion_ids, conclusion_ids)
    for conclusion in record.conclusions:
        if conclusion.status not in CONCLUSION_STATES:
            raise ValueError(f"Unsupported conclusion status: {conclusion.status}")
    for event in record.review_events:
        _validate_review_event(event)
        _require_known_ids("review event evidence", event.evidence_ids, evidence_ids)
        if event.target_type == "candidate" and event.target_id not in candidate_ids:
            raise ValueError(f"Review event references unknown candidate: {event.target_id}")
        if event.target_type == "fact" and event.target_id not in fact_ids:
            raise ValueError(f"Review event references unknown fact: {event.target_id}")
        if event.target_type == "conclusion" and event.target_id not in conclusion_ids:
            raise ValueError(f"Review event references unknown conclusion: {event.target_id}")
    readiness_issue_ids = _unique_ids(record.readiness.issues, "issue_id")
    _require_known_ids(
        "readiness blocking issues", record.readiness.blocking_issue_ids, readiness_issue_ids
    )
    _require_known_ids(
        "readiness nonblocking issues", record.readiness.nonblocking_issue_ids, readiness_issue_ids
    )
    for issue in record.readiness.issues:
        if issue.severity not in SEVERITIES:
            raise ValueError(f"Unsupported readiness severity: {issue.severity}")
    for area in record.readiness.areas:
        if area.status not in READINESS_STATES:
            raise ValueError(f"Unsupported area readiness status: {area.status}")
        _require_known_ids("area readiness facts", area.current_fact_ids, current_ids)
        _require_known_ids("area readiness issues", area.issue_ids, readiness_issue_ids)


def _validate_review_event(event: ReviewEvent) -> None:
    if event.action not in REVIEW_ACTIONS:
        raise ValueError(f"Unsupported review action: {event.action}")
    _require_text("review event id", event.event_id)
    _require_text("review actor id", event.actor_id)
    _require_text("review actor name", event.actor_name)
    _require_text("review actor role", event.actor_role)
    _require_text("review reason", event.reason)
    _parse_timestamp(event.occurred_at)
    _validate_json_value(event.prior_value)
    _validate_json_value(event.resulting_value)


def _validate_appraiser_fact_input(item: AppraiserFactInput) -> None:
    _require_text("field_key", item.field_key)
    if "." not in item.field_key:
        raise ValueError("Appraiser fact field_key must use dot notation.")
    _require_text("fact label", item.label)
    _require_text("fact category", item.category)
    _require_text("fact actor id", item.actor_id)
    _require_text("fact actor name", item.actor_name)
    _require_text("fact actor role", item.actor_role)
    _require_text("fact reason", item.reason)
    _parse_timestamp(item.occurred_at)
    _validate_json_value(item.value)


def _record_from_dict(payload: Mapping[str, Any]) -> AssignmentIntelligenceRecord:
    identity_data = dict(payload["identity"])
    identity_data["lineage"] = RecordLineage(**dict(identity_data.get("lineage") or {}))
    sources = tuple(SourceReference(**dict(item)) for item in payload.get("sources", ()))
    evidence = tuple(
        EvidenceReference(
            **{
                **dict(item),
                "locator": EvidenceLocator(**dict(item.get("locator") or {})),
            }
        )
        for item in payload.get("evidence", ())
    )
    candidates = tuple(
        CandidateAssertion(**_tuple_fields(item, ("evidence_ids",)))
        for item in payload.get("candidates", ())
    )
    review_events = tuple(
        ReviewEvent(**_tuple_fields(item, ("evidence_ids",)))
        for item in payload.get("review_events", ())
    )
    facts = tuple(
        CanonicalFact(
            **_tuple_fields(
                item,
                ("candidate_ids", "evidence_ids", "review_event_ids"),
            )
        )
        for item in payload.get("facts", ())
    )
    conflicts = tuple(
        FactConflict(
            **_tuple_fields(
                item,
                ("candidate_ids", "evidence_ids", "resolution_event_ids"),
            )
        )
        for item in payload.get("conflicts", ())
    )
    assignment_data = dict(payload.get("assignment_context") or {})
    assignment_context = AssignmentContext(
        fact_ids=tuple(assignment_data.get("fact_ids", ())),
        contact_references=tuple(
            EntityReference(**dict(item)) for item in assignment_data.get("contact_references", ())
        ),
    )
    subject_data = dict(payload.get("subject_property") or {})
    property_data = subject_data.get("property_reference")
    subject_property = SubjectProperty(
        property_reference=EntityReference(**dict(property_data)) if property_data else None,
        identity_fact_ids=tuple(subject_data.get("identity_fact_ids", ())),
        characteristic_groups=tuple(
            FactGroup(**_tuple_fields(item, ("fact_ids",)))
            for item in subject_data.get("characteristic_groups", ())
        ),
        ownership_references=tuple(
            EntityReference(**dict(item)) for item in subject_data.get("ownership_references", ())
        ),
    )
    readiness_data = dict(payload["readiness"])
    readiness = AnalysisReadiness(
        overall_status=str(readiness_data["overall_status"]),
        calculated_at=str(readiness_data["calculated_at"]),
        blocking_issue_ids=tuple(readiness_data.get("blocking_issue_ids", ())),
        nonblocking_issue_ids=tuple(readiness_data.get("nonblocking_issue_ids", ())),
        areas=tuple(
            AreaReadiness(
                **_tuple_fields(
                    item,
                    ("required_field_keys", "current_fact_ids", "issue_ids"),
                )
            )
            for item in readiness_data.get("areas", ())
        ),
        issues=tuple(
            ReadinessIssue(**_tuple_fields(item, ("field_keys", "related_ids")))
            for item in readiness_data.get("issues", ())
        ),
    )
    falcon_data = payload.get("falcon_assignment_reference")
    return AssignmentIntelligenceRecord(
        identity=RecordIdentity(**identity_data),
        tenant_id=str(payload["tenant_id"]),
        local_assignment_key=str(payload["local_assignment_key"]),
        falcon_assignment_reference=EntityReference(**dict(falcon_data)) if falcon_data else None,
        sources=sources,
        evidence=evidence,
        candidates=candidates,
        review_events=review_events,
        facts=facts,
        current_fact_ids=tuple(payload.get("current_fact_ids", ())),
        conflicts=conflicts,
        assignment_context=assignment_context,
        subject_property=subject_property,
        comparable_references=tuple(
            ComparableReference(
                **_tuple_fields(
                    item,
                    (
                        "evidence_ids",
                        "adjustment_reference_ids",
                        "qualitative_comparison_reference_ids",
                        "notes",
                    ),
                )
            )
            for item in payload.get("comparable_references", ())
        ),
        market_references=tuple(
            KnowledgeReference(**_tuple_fields(item, ("evidence_ids", "notes")))
            for item in payload.get("market_references", ())
        ),
        prior_knowledge_references=tuple(
            KnowledgeReference(**_tuple_fields(item, ("evidence_ids", "notes")))
            for item in payload.get("prior_knowledge_references", ())
        ),
        report_section_references=tuple(
            ReportSectionReference(**_tuple_fields(item, ("fact_ids", "conclusion_ids")))
            for item in payload.get("report_section_references", ())
        ),
        conclusions=tuple(
            AppraiserConclusion(
                **_tuple_fields(
                    item,
                    ("supporting_fact_ids", "supporting_evidence_ids", "notes"),
                )
            )
            for item in payload.get("conclusions", ())
        ),
        readiness=readiness,
    )


def _plain(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _plain(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


def _tuple_fields(payload: Mapping[str, Any], field_names: Iterable[str]) -> dict[str, Any]:
    output = dict(payload)
    for field_name in field_names:
        output[field_name] = tuple(output.get(field_name, ()))
    return output


def _dedupe_by_id(values: Iterable[Any], id_field: str) -> tuple[Any, ...]:
    by_id: dict[str, Any] = {}
    for value in values:
        identifier = str(getattr(value, id_field))
        if identifier in by_id and by_id[identifier] != value:
            raise ValueError(f"Conflicting objects share {id_field}: {identifier}")
        by_id[identifier] = value
    return tuple(by_id[key] for key in sorted(by_id))


def _unique_ids(values: Iterable[Any], id_field: str) -> set[str]:
    identifiers = [str(getattr(value, id_field)) for value in values]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"Duplicate {id_field} values are not allowed.")
    return set(identifiers)


def _require_known_ids(label: str, values: Iterable[str], known: set[str]) -> None:
    unknown = sorted(set(values) - known)
    if unknown:
        raise ValueError(f"{label} reference unknown IDs: {', '.join(unknown)}")


def _parse_timestamp(value: str) -> datetime:
    _require_text("timestamp", value)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _require_text(field_name: str, value: Any) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")


def _validate_json_value(value: JsonValue) -> None:
    try:
        json.dumps(value, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("Fact and review values must be deterministic JSON values.") from error


def _json_value_type(value: JsonValue, fallback: str) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return fallback or "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return fallback or "null"


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(f"falcon-air-v1|{prefix}|{value}".encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"
