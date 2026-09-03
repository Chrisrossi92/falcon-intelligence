"""AIR-backed local intake review application service and UI projection.

This module stores no parallel fact model. Its session is only the deterministic
inputs used to rebuild the canonical Assignment Intelligence Record.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from typing import Any, Sequence

from falcon_intel.assignment_brief import (
    AssignmentPropertyBrief,
    build_assignment_property_brief,
)
from falcon_intel.assignment_intelligence_record import (
    AppraiserFactInput,
    AssignmentIntelligenceRecord,
    CandidateAssertion,
    CandidateEvidenceBundle,
    ComparableReference,
    EntityReference,
    KnowledgeReference,
    ReadinessRequirement,
    ReviewEvent,
    build_assignment_intelligence_record,
    build_candidate_review_event,
)
from falcon_intel.schema_registry import LOCAL_INTAKE_REVIEW_WORKSPACE_SCHEMA_VERSION


REVIEWED_CANDIDATE_STATES = {"accepted", "corrected", "rejected", "deferred"}

TOPIC_ORDER = (
    "assignment_and_engagement",
    "client_and_intended_users",
    "intended_use_and_appraisal_purpose",
    "important_dates",
    "subject_identity_and_location",
    "property_characteristics",
    "ownership_and_transaction_history",
    "zoning_taxes_and_legal",
    "income_and_occupancy",
    "contacts_and_inspection",
    "comparables_and_market_references",
    "signing_and_review_information",
    "unresolved_or_unclassified",
)

TOPIC_LABELS = {
    "assignment_and_engagement": "Assignment and engagement",
    "client_and_intended_users": "Client and intended users",
    "intended_use_and_appraisal_purpose": "Intended use and appraisal purpose",
    "important_dates": "Important dates",
    "subject_identity_and_location": "Subject identity and location",
    "property_characteristics": "Property characteristics",
    "ownership_and_transaction_history": "Ownership and transaction history",
    "zoning_taxes_and_legal": "Zoning, taxes, and legal information",
    "income_and_occupancy": "Income and occupancy",
    "contacts_and_inspection": "Contacts and inspection",
    "comparables_and_market_references": "Comparables and market references",
    "signing_and_review_information": "Signing and review information",
    "unresolved_or_unclassified": "Unresolved or unclassified items",
}


@dataclass(frozen=True)
class ReviewActor:
    """Local actor identity supplied to canonical AIR review events."""

    actor_id: str
    actor_name: str
    actor_role: str


@dataclass(frozen=True)
class LocalIntakeReviewSession:
    """Rebuildable local review inputs; the assembled AIR remains canonical."""

    tenant_id: str
    local_assignment_key: str
    candidate_bundles: tuple[CandidateEvidenceBundle, ...]
    created_at: str
    updated_at: str
    review_events: tuple[ReviewEvent, ...] = ()
    appraiser_facts: tuple[AppraiserFactInput, ...] = ()
    falcon_assignment_reference: EntityReference | None = None
    property_reference: EntityReference | None = None
    assignment_contacts: tuple[EntityReference, ...] = ()
    ownership_references: tuple[EntityReference, ...] = ()
    comparable_references: tuple[ComparableReference, ...] = ()
    market_references: tuple[KnowledgeReference, ...] = ()
    prior_knowledge_references: tuple[KnowledgeReference, ...] = ()
    readiness_requirements: tuple[ReadinessRequirement, ...] = ()

    def assemble_air(self) -> AssignmentIntelligenceRecord:
        """Rebuild canonical AIR state from immutable evidence and review events."""

        kwargs: dict[str, Any] = {}
        if self.readiness_requirements:
            kwargs["readiness_requirements"] = self.readiness_requirements
        return build_assignment_intelligence_record(
            tenant_id=self.tenant_id,
            local_assignment_key=self.local_assignment_key,
            candidate_bundles=self.candidate_bundles,
            review_events=self.review_events,
            appraiser_facts=self.appraiser_facts,
            falcon_assignment_reference=self.falcon_assignment_reference,
            property_reference=self.property_reference,
            assignment_contacts=self.assignment_contacts,
            ownership_references=self.ownership_references,
            comparable_references=self.comparable_references,
            market_references=self.market_references,
            prior_knowledge_references=self.prior_knowledge_references,
            created_at=self.created_at,
            updated_at=self.updated_at,
            **kwargs,
        )

    def accept(
        self,
        candidate_id: str,
        *,
        actor: ReviewActor,
        occurred_at: str,
        reason: str = "Accepted after appraiser review.",
    ) -> "LocalIntakeReviewSession":
        """Accept a candidate and rebuild it as a verified AIR fact."""

        return self._review_candidate(
            candidate_id,
            action="candidate_verified",
            actor=actor,
            occurred_at=occurred_at,
            reason=reason,
        )

    def correct(
        self,
        candidate_id: str,
        corrected_value: Any,
        *,
        actor: ReviewActor,
        occurred_at: str,
        reason: str,
    ) -> "LocalIntakeReviewSession":
        """Create an additive corrected AIR fact while retaining the observation."""

        _require_reason("Correction", reason)
        return self._review_candidate(
            candidate_id,
            action="candidate_corrected",
            actor=actor,
            occurred_at=occurred_at,
            reason=reason,
            corrected_value=corrected_value,
        )

    def reject(
        self,
        candidate_id: str,
        *,
        actor: ReviewActor,
        occurred_at: str,
        reason: str,
    ) -> "LocalIntakeReviewSession":
        """Reject without deleting the candidate or its provenance."""

        _require_reason("Rejection", reason)
        return self._review_candidate(
            candidate_id,
            action="candidate_rejected",
            actor=actor,
            occurred_at=occurred_at,
            reason=reason,
        )

    def defer(
        self,
        candidate_id: str,
        *,
        actor: ReviewActor,
        occurred_at: str,
        reason: str = "Deferred for later appraiser review.",
    ) -> "LocalIntakeReviewSession":
        """Record an explicit defer event without promoting or rejecting a fact."""

        return self._review_candidate(
            candidate_id,
            action="candidate_deferred",
            actor=actor,
            occurred_at=occurred_at,
            reason=reason,
        )

    def resolve_conflict(
        self,
        conflict_id: str,
        selected_candidate_id: str,
        *,
        actor: ReviewActor,
        occurred_at: str,
        reason: str,
        corrected_value: Any = None,
    ) -> "LocalIntakeReviewSession":
        """Resolve a conflict through explicit accept/correct and reject events."""

        _require_reason("Conflict resolution", reason)
        record = self.assemble_air()
        conflict = next(
            (item for item in record.conflicts if item.conflict_id == conflict_id),
            None,
        )
        if conflict is None:
            raise ValueError(f"Unknown conflict: {conflict_id}")
        if conflict.status != "unresolved":
            raise ValueError("Conflict is already resolved.")
        if selected_candidate_id not in conflict.candidate_ids:
            raise ValueError("Selected candidate is not part of the conflict.")

        result = self
        for candidate_id in conflict.candidate_ids:
            if candidate_id == selected_candidate_id:
                result = (
                    result.correct(
                        candidate_id,
                        corrected_value,
                        actor=actor,
                        occurred_at=occurred_at,
                        reason=reason,
                    )
                    if corrected_value is not None
                    else result.accept(
                        candidate_id,
                        actor=actor,
                        occurred_at=occurred_at,
                        reason=reason,
                    )
                )
            else:
                result = result.reject(
                    candidate_id,
                    actor=actor,
                    occurred_at=occurred_at,
                    reason=reason,
                )
        resolved = next(
            item for item in result.assemble_air().conflicts if item.conflict_id == conflict_id
        )
        if resolved.status != "resolved":
            raise ValueError("Conflict resolution did not leave one explicitly selected value.")
        return result

    def add_fact(
        self,
        *,
        field_key: str,
        label: str,
        category: str,
        value: Any,
        value_type: str,
        unit: str | None,
        material: bool,
        actor: ReviewActor,
        occurred_at: str,
        reason: str,
        evidence_ids: Sequence[str] = (),
    ) -> "LocalIntakeReviewSession":
        """Append an appraiser-entered AIR fact with explicit audit provenance."""

        _require_reason("Manual fact entry", reason)
        current = self.assemble_air().current_fact(field_key)
        item = AppraiserFactInput(
            field_key=field_key,
            label=label,
            category=category,
            value=value,
            value_type=value_type,
            unit=unit,
            material=material,
            actor_id=actor.actor_id,
            actor_name=actor.actor_name,
            actor_role=actor.actor_role,
            occurred_at=occurred_at,
            reason=reason,
            evidence_ids=tuple(evidence_ids),
            supersedes_fact_id=current.fact_id if current else None,
        )
        return replace(
            self,
            appraiser_facts=(*self.appraiser_facts, item),
            updated_at=occurred_at,
        )

    def _review_candidate(
        self,
        candidate_id: str,
        *,
        action: str,
        actor: ReviewActor,
        occurred_at: str,
        reason: str,
        corrected_value: Any = None,
    ) -> "LocalIntakeReviewSession":
        candidate = self._candidate(candidate_id)
        event = build_candidate_review_event(
            candidate,
            action=action,
            actor_id=actor.actor_id,
            actor_name=actor.actor_name,
            actor_role=actor.actor_role,
            occurred_at=occurred_at,
            reason=reason,
            corrected_value=corrected_value,
        )
        return replace(
            self,
            review_events=(*self.review_events, event),
            updated_at=occurred_at,
        )

    def _candidate(self, candidate_id: str) -> CandidateAssertion:
        candidate = next(
            (
                item
                for bundle in self.candidate_bundles
                for item in bundle.candidates
                if item.candidate_id == candidate_id
            ),
            None,
        )
        if candidate is None:
            raise ValueError(f"Unknown candidate: {candidate_id}")
        return candidate


def topic_for_field(field_key: str) -> str:
    """Map AIR dot-notation fields to practical appraisal review topics."""

    if field_key in {"assignment.client", "assignment.intended_user"}:
        return "client_and_intended_users"
    if field_key in {
        "assignment.intended_use",
        "assignment.appraisal_purpose",
    }:
        return "intended_use_and_appraisal_purpose"
    if field_key.startswith("assignment.") and any(
        token in field_key for token in ("date", "due")
    ):
        return "important_dates"
    if field_key in {
        "assignment.signing_appraiser",
        "assignment.reviewer",
    }:
        return "signing_and_review_information"
    if field_key.startswith("assignment.") and any(
        token in field_key for token in ("contact", "inspection")
    ):
        return "contacts_and_inspection"
    if field_key.startswith(("assignment.", "report.")):
        return "assignment_and_engagement"
    if field_key in {
        "subject.property_id",
        "subject.name",
        "subject.address",
        "subject.parcel_identifiers",
        "subject.coordinates",
        "subject.property_type",
        "subject.property_subtype",
        "subject.alternate_identifiers",
    }:
        return "subject_identity_and_location"
    if field_key.startswith("subject.") and any(
        token in field_key for token in ("ownership", "sale_history", "transaction")
    ):
        return "ownership_and_transaction_history"
    if field_key.startswith("subject.") and any(
        token in field_key for token in ("zoning", "tax", "legal", "flood", "parcel")
    ):
        return "zoning_taxes_and_legal"
    if field_key.startswith("subject.") and any(
        token in field_key for token in ("income", "occupancy", "tenancy", "operating")
    ):
        return "income_and_occupancy"
    if field_key.startswith("subject."):
        return "property_characteristics"
    if field_key.startswith(("comparable.", "market.", "analysis.approaches.")):
        return "comparables_and_market_references"
    return "unresolved_or_unclassified"


def build_local_intake_review_workspace(
    record: AssignmentIntelligenceRecord,
    brief: AssignmentPropertyBrief | None = None,
) -> dict[str, Any]:
    """Project AIR state into the versioned local React adapter contract."""

    brief = brief or build_assignment_property_brief(record)
    evidence_by_id = {item.evidence_id: item for item in record.evidence}
    source_by_id = {item.source_id: item for item in record.sources}
    conflicts_by_candidate: dict[str, list[Any]] = {}
    for conflict in record.conflicts:
        for candidate_id in conflict.candidate_ids:
            conflicts_by_candidate.setdefault(candidate_id, []).append(conflict)
    latest_event_by_candidate: dict[str, ReviewEvent] = {}
    for event in record.review_events:
        if event.target_type == "candidate":
            latest_event_by_candidate[event.target_id] = event

    grouped: dict[str, list[dict[str, Any]]] = {topic: [] for topic in TOPIC_ORDER}
    for candidate in record.candidates:
        topic = topic_for_field(candidate.field_key)
        candidate_evidence = []
        for evidence_id in candidate.evidence_ids:
            evidence = evidence_by_id[evidence_id]
            source = source_by_id[evidence.source_id]
            candidate_evidence.append(
                {
                    "evidence_id": evidence.evidence_id,
                    "source_document": source.display_label,
                    "safe_reference": source.safe_reference,
                    "locator": asdict(evidence.locator),
                    "extraction_method": evidence.extraction_method,
                    "confidence": evidence.confidence,
                    "quality": evidence.quality,
                }
            )
        latest_event = latest_event_by_candidate.get(candidate.candidate_id)
        grouped[topic].append(
            {
                "candidate_id": candidate.candidate_id,
                "field_key": candidate.field_key,
                "label": candidate.label,
                "value": candidate.value,
                "normalized_value": candidate.normalized_value,
                "value_type": candidate.value_type,
                "unit": candidate.unit,
                "material": candidate.material,
                "machine_verification_status": candidate.machine_verification_status,
                "machine_confidence": candidate.machine_confidence,
                "state": candidate.state,
                "conflict_ids": [
                    item.conflict_id for item in conflicts_by_candidate.get(candidate.candidate_id, ())
                ],
                "latest_review": asdict(latest_event) if latest_event else None,
                "evidence": candidate_evidence,
                "available_actions": [
                    "accept",
                    "correct",
                    "reject",
                    "defer",
                ],
            }
        )
    topics = [
        {
            "topic_key": topic,
            "label": TOPIC_LABELS[topic],
            "candidates": sorted(
                grouped[topic], key=lambda item: (item["field_key"], item["candidate_id"])
            ),
        }
        for topic in TOPIC_ORDER
        if grouped[topic]
    ]
    counts = {state: 0 for state in (*sorted(REVIEWED_CANDIDATE_STATES), "needs_review")}
    for candidate in record.candidates:
        if candidate.state in REVIEWED_CANDIDATE_STATES:
            counts[candidate.state] += 1
        else:
            counts["needs_review"] += 1
    reviewed = sum(counts[state] for state in REVIEWED_CANDIDATE_STATES)
    missing_critical = [
        asdict(item)
        for item in record.readiness.issues
        if item.issue_type == "missing_required_fact" and item.severity == "blocking"
    ]
    assignment_label = (
        record.falcon_assignment_reference.display_label
        if record.falcon_assignment_reference
        else record.local_assignment_key
    )
    payload = {
        "schema_version": LOCAL_INTAKE_REVIEW_WORKSPACE_SCHEMA_VERSION,
        "workspace_type": "local_intake_review",
        "semantic_source": {
            "canonical_model": "assignment_intelligence_record",
            "air_schema_version": record.identity.schema_version,
            "air_record_id": record.identity.record_id,
            "air_record_version": record.identity.record_version,
            "adapter_mode": "local_synthetic_fixture",
        },
        "assignment": {
            "label": assignment_label,
            "local_assignment_key": record.local_assignment_key,
            "lifecycle_state": record.identity.lifecycle_state,
            "overview": [asdict(item) for item in brief.assignment_synopsis],
        },
        "review_progress": {
            "total_candidates": len(record.candidates),
            "reviewed_candidates": reviewed,
            "percent_complete": round(reviewed / len(record.candidates) * 100)
            if record.candidates
            else 100,
            "counts": counts,
        },
        "topics": topics,
        "conflicts": [asdict(item) for item in record.conflicts],
        "readiness": asdict(record.readiness),
        "missing_critical_information": missing_critical,
        "air": record.to_dict(),
        "brief": brief.to_dict(),
        "brief_markdown": brief.to_markdown(),
        "export_formats": ["air_json", "brief_json", "brief_markdown"],
        "guardrail": (
            "Synthetic local proof only. Review actions use AIR event names; source documents, "
            "valuation conclusions, narrative generation, and production persistence are unavailable."
        ),
    }
    return json.loads(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def _require_reason(label: str, reason: str) -> None:
    if not reason.strip():
        raise ValueError(f"{label} requires a reason.")
