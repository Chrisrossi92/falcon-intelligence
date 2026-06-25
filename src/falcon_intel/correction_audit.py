"""Synthetic correction and audit trail models for field-level review."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Literal


CorrectionTargetType = Literal[
    "subject_profile_field",
    "property_library_field",
    "candidate_match_field",
]
CorrectionReviewStatus = Literal["proposed", "needs_review", "approved", "rejected"]
CorrectionAuditEventType = Literal[
    "original_value_recorded",
    "correction_submitted",
    "supporting_evidence_added",
    "correction_approved",
    "correction_rejected",
]


@dataclass(frozen=True)
class SupportingEvidenceReference:
    """Metadata-only support reference for a synthetic correction."""

    evidence_id: str
    source_type: str
    display_label: str
    source_reference: str
    access_level: str
    status: str

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            _require_non_empty(field_name, value)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ConfidenceImpact:
    """Confidence movement caused by a correction and its supporting evidence."""

    prior_confidence: int
    corrected_confidence: int
    impact_summary: str

    def __post_init__(self) -> None:
        _require_confidence("prior_confidence", self.prior_confidence)
        _require_confidence("corrected_confidence", self.corrected_confidence)
        _require_non_empty("impact_summary", self.impact_summary)

    @property
    def delta(self) -> int:
        return self.corrected_confidence - self.prior_confidence

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["delta"] = self.delta
        return payload


@dataclass(frozen=True)
class CorrectionAuditEvent:
    """Append-only synthetic audit event for one correction lifecycle step."""

    audit_event_id: str
    event_type: CorrectionAuditEventType
    actor_id: str
    actor_name: str
    actor_role: str
    timestamp: str
    target_type: CorrectionTargetType
    target_id: str
    field_key: str
    old_value: str | int | float | None
    new_value: str | int | float | None
    reason: str
    evidence_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty("audit_event_id", self.audit_event_id)
        _require_non_empty("event_type", self.event_type)
        _require_non_empty("actor_id", self.actor_id)
        _require_non_empty("actor_name", self.actor_name)
        _require_non_empty("actor_role", self.actor_role)
        datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        _require_non_empty("target_type", self.target_type)
        _require_non_empty("target_id", self.target_id)
        _require_non_empty("field_key", self.field_key)
        _require_non_empty("reason", self.reason)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.evidence_id is None:
            payload.pop("evidence_id")
        return payload


@dataclass(frozen=True)
class FieldProvenance:
    """Current field provenance and visible correction history."""

    target_type: CorrectionTargetType
    target_id: str
    field_key: str
    current_value: str | int | float | None
    current_confidence: int
    current_source: str
    original_value: str | int | float | None
    original_source: str
    audit_event_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_empty("target_type", self.target_type)
        _require_non_empty("target_id", self.target_id)
        _require_non_empty("field_key", self.field_key)
        _require_confidence("current_confidence", self.current_confidence)
        _require_non_empty("current_source", self.current_source)
        _require_non_empty("original_source", self.original_source)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["audit_event_ids"] = list(self.audit_event_ids)
        return payload


@dataclass(frozen=True)
class CorrectionEvent:
    """One synthetic correction preserving prior value, corrected value, and audit."""

    correction_id: str
    target_type: CorrectionTargetType
    target_id: str
    field_key: str
    label: str
    prior_value: str | int | float | None
    corrected_value: str | int | float | None
    original_actor: str
    corrected_by: str
    corrected_at: str
    reason: str
    review_status: CorrectionReviewStatus
    supporting_evidence: SupportingEvidenceReference
    confidence_impact: ConfidenceImpact
    audit_events: tuple[CorrectionAuditEvent, ...]

    def __post_init__(self) -> None:
        _require_non_empty("correction_id", self.correction_id)
        _require_non_empty("target_type", self.target_type)
        _require_non_empty("target_id", self.target_id)
        _require_non_empty("field_key", self.field_key)
        _require_non_empty("label", self.label)
        _require_non_empty("original_actor", self.original_actor)
        _require_non_empty("corrected_by", self.corrected_by)
        datetime.fromisoformat(self.corrected_at.replace("Z", "+00:00"))
        _require_non_empty("reason", self.reason)
        _require_non_empty("review_status", self.review_status)
        if not self.audit_events:
            raise ValueError("audit_events is required.")

    def approved(self) -> bool:
        return self.review_status == "approved"

    def current_value(self) -> str | int | float | None:
        if self.approved():
            return self.corrected_value
        return self.prior_value

    def current_confidence(self) -> int:
        if self.approved():
            return self.confidence_impact.corrected_confidence
        return self.confidence_impact.prior_confidence

    def provenance(self) -> FieldProvenance:
        current_source = (
            self.supporting_evidence.display_label
            if self.approved()
            else f"Original entry by {self.original_actor}"
        )
        return FieldProvenance(
            target_type=self.target_type,
            target_id=self.target_id,
            field_key=self.field_key,
            current_value=self.current_value(),
            current_confidence=self.current_confidence(),
            current_source=current_source,
            original_value=self.prior_value,
            original_source=f"Original entry by {self.original_actor}",
            audit_event_ids=tuple(event.audit_event_id for event in self.audit_events),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "correctionId": self.correction_id,
            "targetType": self.target_type,
            "targetId": self.target_id,
            "fieldKey": self.field_key,
            "label": self.label,
            "priorValue": self.prior_value,
            "correctedValue": self.corrected_value,
            "currentValue": self.current_value(),
            "originalActor": self.original_actor,
            "correctedBy": self.corrected_by,
            "correctedAt": self.corrected_at,
            "reason": self.reason,
            "reviewStatus": self.review_status,
            "supportingEvidence": self.supporting_evidence.to_dict(),
            "confidenceImpact": self.confidence_impact.to_dict(),
            "fieldProvenance": self.provenance().to_dict(),
            "auditEvents": [event.to_dict() for event in self.audit_events],
        }


def build_demo_correction_audit_workspace() -> dict[str, Any]:
    """Build a synthetic correction/audit preview for profile and comp fields."""

    corrections = _demo_corrections()
    approved_corrections = [correction for correction in corrections if correction.approved()]
    return {
        "workspaceType": "synthetic_evidence_correction_audit_preview",
        "guardrail": (
            "Synthetic correction data only. No persistence, uploads, OneDrive access, "
            "OCR, embeddings, report parsing, or report export is performed."
        ),
        "scenario": (
            "Chad originally entered a comparable GBA of 4,200 SF. Chris corrected "
            "it to 4,800 SF based on a synthetic auditor property record card."
        ),
        "summary": {
            "correctionCount": len(corrections),
            "approvedCorrectionCount": len(approved_corrections),
            "auditEventCount": sum(len(correction.audit_events) for correction in corrections),
        },
        "corrections": [correction.to_dict() for correction in corrections],
        "currentResolvedValues": {
            correction.correction_id: correction.current_value() for correction in corrections
        },
    }


def resolve_current_value(
    prior_value: str | int | float | None,
    corrections: tuple[CorrectionEvent, ...],
) -> str | int | float | None:
    """Resolve the trusted current value from approved corrections only."""

    current_value = prior_value
    for correction in corrections:
        if correction.approved():
            current_value = correction.corrected_value
    return current_value


def _demo_corrections() -> tuple[CorrectionEvent, ...]:
    auditor_evidence = SupportingEvidenceReference(
        evidence_id="evidence-auditor-card-1220-main",
        source_type="synthetic_property_record_card",
        display_label="Synthetic auditor property record card",
        source_reference="AUD-DEMO-1220-MAIN-GBA",
        access_level="appraiser_reviewer_only",
        status="available",
    )
    profile_evidence = SupportingEvidenceReference(
        evidence_id="evidence-subject-sketch-riverview",
        source_type="synthetic_subject_profile_card",
        display_label="Synthetic subject profile review card",
        source_reference="SUBJECT-DEMO-517-RIVERVIEW-SKETCH",
        access_level="appraiser_reviewer_only",
        status="placeholder",
    )
    rejected_evidence = SupportingEvidenceReference(
        evidence_id="evidence-unsupported-comp-note",
        source_type="synthetic_comp_note",
        display_label="Synthetic unsupported comp note",
        source_reference="COMP-DEMO-UNSUPPORTED-GBA",
        access_level="internal_only",
        status="placeholder",
    )
    return (
        CorrectionEvent(
            correction_id="correction-main-1220-gba",
            target_type="property_library_field",
            target_id="prop-main-1220",
            field_key="building_size_sf",
            label="Comparable GBA",
            prior_value=4200,
            corrected_value=4800,
            original_actor="Chad",
            corrected_by="Chris",
            corrected_at="2026-06-25T14:15:00+00:00",
            reason="based on auditor",
            review_status="approved",
            supporting_evidence=auditor_evidence,
            confidence_impact=ConfidenceImpact(
                prior_confidence=58,
                corrected_confidence=88,
                impact_summary="Confidence increased after auditor record support was added.",
            ),
            audit_events=(
                _audit_event(
                    "audit-main-gba-original",
                    "original_value_recorded",
                    "user-chad",
                    "Chad",
                    "appraiser",
                    "2026-06-20T13:00:00+00:00",
                    "property_library_field",
                    "prop-main-1220",
                    "building_size_sf",
                    None,
                    4200,
                    "Initial synthetic comparable entry.",
                    None,
                ),
                _audit_event(
                    "audit-main-gba-correction",
                    "correction_submitted",
                    "user-chris",
                    "Chris",
                    "reviewer",
                    "2026-06-25T14:15:00+00:00",
                    "property_library_field",
                    "prop-main-1220",
                    "building_size_sf",
                    4200,
                    4800,
                    "based on auditor",
                    None,
                ),
                _audit_event(
                    "audit-main-gba-evidence",
                    "supporting_evidence_added",
                    "user-chris",
                    "Chris",
                    "reviewer",
                    "2026-06-25T14:16:00+00:00",
                    "property_library_field",
                    "prop-main-1220",
                    "building_size_sf",
                    4200,
                    4800,
                    "Attached synthetic auditor property record card.",
                    "evidence-auditor-card-1220-main",
                ),
                _audit_event(
                    "audit-main-gba-approved",
                    "correction_approved",
                    "user-chris",
                    "Chris",
                    "reviewer",
                    "2026-06-25T14:18:00+00:00",
                    "property_library_field",
                    "prop-main-1220",
                    "building_size_sf",
                    4200,
                    4800,
                    "Approved correction after evidence review.",
                    "evidence-auditor-card-1220-main",
                ),
            ),
        ),
        CorrectionEvent(
            correction_id="correction-subject-riverview-gba",
            target_type="subject_profile_field",
            target_id="subject-profile-517-riverview",
            field_key="improvements.gba_sf",
            label="Subject GBA",
            prior_value=6120,
            corrected_value=6180,
            original_actor="Falcon Demo Intake",
            corrected_by="Chris",
            corrected_at="2026-06-25T15:05:00+00:00",
            reason="aligned profile with reviewed sketch card",
            review_status="needs_review",
            supporting_evidence=profile_evidence,
            confidence_impact=ConfidenceImpact(
                prior_confidence=72,
                corrected_confidence=81,
                impact_summary="Confidence would increase after appraiser approval.",
            ),
            audit_events=(
                _audit_event(
                    "audit-subject-gba-original",
                    "original_value_recorded",
                    "system-demo",
                    "Falcon Demo Intake",
                    "system",
                    "2026-06-24T16:00:00+00:00",
                    "subject_profile_field",
                    "subject-profile-517-riverview",
                    "improvements.gba_sf",
                    None,
                    6120,
                    "Initial synthetic subject profile value.",
                    None,
                ),
                _audit_event(
                    "audit-subject-gba-correction",
                    "correction_submitted",
                    "user-chris",
                    "Chris",
                    "appraiser",
                    "2026-06-25T15:05:00+00:00",
                    "subject_profile_field",
                    "subject-profile-517-riverview",
                    "improvements.gba_sf",
                    6120,
                    6180,
                    "aligned profile with reviewed sketch card",
                    "evidence-subject-sketch-riverview",
                ),
            ),
        ),
        CorrectionEvent(
            correction_id="correction-riverview-alt-rejected-gba",
            target_type="candidate_match_field",
            target_id="match-riverview-address-size",
            field_key="conflicting_fields.building_size_sf",
            label="Candidate Match GBA",
            prior_value=6400,
            corrected_value=6000,
            original_actor="Chad",
            corrected_by="Chris",
            corrected_at="2026-06-25T15:25:00+00:00",
            reason="unsupported alternate comp note",
            review_status="rejected",
            supporting_evidence=rejected_evidence,
            confidence_impact=ConfidenceImpact(
                prior_confidence=58,
                corrected_confidence=42,
                impact_summary="Confidence decreased because the note did not support overwriting the candidate.",
            ),
            audit_events=(
                _audit_event(
                    "audit-candidate-gba-original",
                    "original_value_recorded",
                    "user-chad",
                    "Chad",
                    "appraiser",
                    "2026-06-20T13:30:00+00:00",
                    "candidate_match_field",
                    "match-riverview-address-size",
                    "conflicting_fields.building_size_sf",
                    None,
                    6400,
                    "Original duplicate candidate value.",
                    None,
                ),
                _audit_event(
                    "audit-candidate-gba-rejected",
                    "correction_rejected",
                    "user-chris",
                    "Chris",
                    "reviewer",
                    "2026-06-25T15:30:00+00:00",
                    "candidate_match_field",
                    "match-riverview-address-size",
                    "conflicting_fields.building_size_sf",
                    6400,
                    6000,
                    "Rejected because support was insufficient.",
                    "evidence-unsupported-comp-note",
                ),
            ),
        ),
    )


def _audit_event(
    audit_event_id: str,
    event_type: CorrectionAuditEventType,
    actor_id: str,
    actor_name: str,
    actor_role: str,
    timestamp: str,
    target_type: CorrectionTargetType,
    target_id: str,
    field_key: str,
    old_value: str | int | float | None,
    new_value: str | int | float | None,
    reason: str,
    evidence_id: str | None,
) -> CorrectionAuditEvent:
    return CorrectionAuditEvent(
        audit_event_id=audit_event_id,
        event_type=event_type,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        timestamp=timestamp,
        target_type=target_type,
        target_id=target_id,
        field_key=field_key,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
        evidence_id=evidence_id,
    )


def _require_confidence(field_name: str, value: int) -> None:
    if value < 0 or value > 100:
        raise ValueError(f"{field_name} must be between 0 and 100.")


def _require_non_empty(field_name: str, value: Any | None) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")
