import pytest

from falcon_intel.correction_audit import (
    ConfidenceImpact,
    CorrectionAuditEvent,
    CorrectionEvent,
    SupportingEvidenceReference,
    build_demo_correction_audit_workspace,
    resolve_current_value,
)


def test_approved_correction_preserves_prior_value_and_resolves_current_value() -> None:
    workspace = build_demo_correction_audit_workspace()
    correction = workspace["corrections"][0]

    assert correction["priorValue"] == 4200
    assert correction["correctedValue"] == 4800
    assert correction["currentValue"] == 4800
    assert correction["originalActor"] == "Chad"
    assert correction["correctedBy"] == "Chris"
    assert correction["reason"] == "based on auditor"


def test_audit_event_includes_actor_timestamp_reason_source_and_values() -> None:
    workspace = build_demo_correction_audit_workspace()
    audit_events = workspace["corrections"][0]["auditEvents"]
    evidence_event = next(event for event in audit_events if event["event_type"] == "supporting_evidence_added")

    assert evidence_event["actor_name"] == "Chris"
    assert evidence_event["timestamp"] == "2026-06-25T14:16:00+00:00"
    assert evidence_event["old_value"] == 4200
    assert evidence_event["new_value"] == 4800
    assert evidence_event["reason"] == "Attached synthetic auditor property record card."
    assert evidence_event["evidence_id"] == "evidence-auditor-card-1220-main"


def test_confidence_impact_is_represented() -> None:
    workspace = build_demo_correction_audit_workspace()
    confidence = workspace["corrections"][0]["confidenceImpact"]

    assert confidence["prior_confidence"] == 58
    assert confidence["corrected_confidence"] == 88
    assert confidence["delta"] == 30
    assert "auditor record" in confidence["impact_summary"]


def test_pending_or_rejected_correction_does_not_overwrite_trusted_value() -> None:
    workspace = build_demo_correction_audit_workspace()
    pending_subject = workspace["corrections"][1]
    rejected_candidate = workspace["corrections"][2]

    assert pending_subject["reviewStatus"] == "needs_review"
    assert pending_subject["currentValue"] == 6120
    assert rejected_candidate["reviewStatus"] == "rejected"
    assert rejected_candidate["currentValue"] == 6400


def test_resolve_current_value_uses_only_approved_corrections() -> None:
    corrections = _sample_corrections()

    assert resolve_current_value(4200, corrections) == 4800
    assert resolve_current_value(4200, corrections[1:]) == 4200


def test_confidence_range_is_validated() -> None:
    with pytest.raises(ValueError):
        ConfidenceImpact(
            prior_confidence=101,
            corrected_confidence=88,
            impact_summary="Invalid confidence for test.",
        )


def _sample_corrections() -> tuple[CorrectionEvent, ...]:
    evidence = SupportingEvidenceReference(
        evidence_id="evidence-test",
        source_type="synthetic_property_record_card",
        display_label="Synthetic evidence",
        source_reference="TEST-1",
        access_level="internal_only",
        status="available",
    )
    workspace = build_demo_correction_audit_workspace()
    approved = workspace["corrections"][0]
    rejected = workspace["corrections"][2]
    return (
        CorrectionEvent(
            correction_id="approved-test",
            target_type="property_library_field",
            target_id="prop-test",
            field_key="building_size_sf",
            label="GBA",
            prior_value=approved["priorValue"],
            corrected_value=approved["correctedValue"],
            original_actor="Chad",
            corrected_by="Chris",
            corrected_at="2026-06-25T14:15:00+00:00",
            reason="based on auditor",
            review_status="approved",
            supporting_evidence=evidence,
            confidence_impact=ConfidenceImpact(
                prior_confidence=58,
                corrected_confidence=88,
                impact_summary="Approved test correction.",
            ),
            audit_events=(_sample_audit_event("audit-approved-test", "correction_approved"),),
        ),
        CorrectionEvent(
            correction_id="rejected-test",
            target_type="property_library_field",
            target_id="prop-test",
            field_key="building_size_sf",
            label="GBA",
            prior_value=rejected["priorValue"],
            corrected_value=rejected["correctedValue"],
            original_actor="Chad",
            corrected_by="Chris",
            corrected_at="2026-06-25T15:25:00+00:00",
            reason="unsupported",
            review_status="rejected",
            supporting_evidence=evidence,
            confidence_impact=ConfidenceImpact(
                prior_confidence=58,
                corrected_confidence=42,
                impact_summary="Rejected test correction.",
            ),
            audit_events=(_sample_audit_event("audit-rejected-test", "correction_rejected"),),
        ),
    )


def _sample_audit_event(audit_event_id: str, event_type: str) -> CorrectionAuditEvent:
    return CorrectionAuditEvent(
        audit_event_id=audit_event_id,
        event_type=event_type,
        actor_id="user-chris",
        actor_name="Chris",
        actor_role="reviewer",
        timestamp="2026-06-25T16:00:00+00:00",
        target_type="property_library_field",
        target_id="prop-test",
        field_key="building_size_sf",
        old_value=4200,
        new_value=4800,
        reason="test event",
        evidence_id="evidence-test",
    )
