from dataclasses import replace

from falcon_intel.assignment_intelligence_record import (
    AppraiserConclusionInput,
    AppraiserFactInput,
    AssignmentIntelligenceRecord,
    CandidateEvidenceBundle,
    EntityReference,
    RecordLineage,
    build_assignment_intelligence_record,
    build_candidate_review_event,
    save_assignment_intelligence_record,
)
from falcon_intel.schema_registry import ASSIGNMENT_INTELLIGENCE_RECORD_SCHEMA_VERSION
from falcon_intel.synthetic_assignment_record import (
    SYNTHETIC_TIMESTAMP,
    build_synthetic_assignment_intelligence_record,
)


def test_synthetic_vertical_proof_enters_existing_extraction_path() -> None:
    record = build_synthetic_assignment_intelligence_record()

    assert record.sources[0].document_id == "synthetic-air-final-report"
    assert record.sources[0].content_included is False
    assert record.sources[0].safe_reference == "final-report.pdf"
    assert all(item.source_excerpt is None for item in record.evidence)
    assert record.current_fact("assignment.client").value == "Example Regional Bank"
    assert record.current_fact("assignment.interest_appraised").value == "Leased fee interest"
    assert record.current_fact("subject.address").value == "800 Meridian Commerce Drive"
    assert record.current_fact("subject.building_area").value == 48000


def test_record_identity_and_rebuild_are_deterministic() -> None:
    first = build_synthetic_assignment_intelligence_record()
    second = build_synthetic_assignment_intelligence_record()

    assert first.identity.record_id == second.identity.record_id
    assert first.to_dict() == second.to_dict()
    assert first.to_json() == second.to_json()


def test_explicit_record_identity_and_lineage_are_preserved() -> None:
    record = build_assignment_intelligence_record(
        tenant_id="tenant-synthetic",
        local_assignment_key="assignment-synthetic",
        candidate_bundles=(),
        review_events=(),
        record_id="air-explicit-synthetic-001",
        record_version=2,
        lineage=RecordLineage(
            previous_record_id="air-explicit-synthetic-001",
            previous_record_version=1,
        ),
        created_at=SYNTHETIC_TIMESTAMP,
        updated_at=SYNTHETIC_TIMESTAMP,
    )

    assert record.identity.record_id == "air-explicit-synthetic-001"
    assert record.identity.record_version == 2
    assert record.identity.lineage.previous_record_version == 1


def test_machine_candidate_requires_human_promotion_to_become_current_fact() -> None:
    record = build_synthetic_assignment_intelligence_record()
    client_candidate = _candidate(record, "assignment.client")
    report_date_candidate = _candidate(record, "assignment.report_date_requirement")

    assert client_candidate.machine_verification_status in {"verified", "probable"}
    assert client_candidate.state == "accepted"
    assert record.current_fact("assignment.client").origin == "verified_candidate"
    assert report_date_candidate.state == "extracted_candidate"
    assert record.current_fact("assignment.report_date_requirement") is None


def test_candidate_promotion_preserves_provenance() -> None:
    record = build_synthetic_assignment_intelligence_record()
    candidate = _candidate(record, "subject.address")
    fact = record.current_fact("subject.address")
    evidence_by_id = {item.evidence_id: item for item in record.evidence}

    assert fact.candidate_ids == (candidate.candidate_id,)
    assert fact.evidence_ids == candidate.evidence_ids
    assert all(evidence_id in evidence_by_id for evidence_id in fact.evidence_ids)
    assert any(evidence_by_id[item].locator.page_number == 1 for item in fact.evidence_ids)
    assert all(evidence_by_id[item].extraction_method for item in fact.evidence_ids)


def test_review_history_identifies_actor_reason_and_action() -> None:
    record = build_synthetic_assignment_intelligence_record()
    client = record.current_fact("assignment.client")
    event_by_id = {item.event_id: item for item in record.review_events}
    event = event_by_id[client.review_event_ids[0]]

    assert event.action == "candidate_verified"
    assert event.actor_id == "user-synthetic-appraiser-001"
    assert event.actor_role == "appraiser"
    assert event.reason
    assert event.occurred_at == "2026-09-03T14:15:00+00:00"
    assert {item.actor_role for item in record.review_events} >= {"appraiser", "reviewer"}


def test_correction_preserves_original_candidate_and_evidence() -> None:
    record = build_synthetic_assignment_intelligence_record()
    candidate = _candidate(record, "subject.property_type")
    corrected_fact = record.current_fact("subject.property_type")

    assert candidate.value == "Industrial"
    assert candidate.state == "corrected"
    assert corrected_fact.value == "Industrial / Warehouse"
    assert corrected_fact.state == "corrected"
    assert corrected_fact.origin == "corrected_candidate"
    assert corrected_fact.candidate_ids == (candidate.candidate_id,)
    assert set(candidate.evidence_ids).issubset(corrected_fact.evidence_ids)


def test_later_correction_adds_revision_and_supersedes_prior_fact() -> None:
    source_record = build_synthetic_assignment_intelligence_record()
    bundle = CandidateEvidenceBundle(
        sources=source_record.sources,
        evidence=source_record.evidence,
        candidates=tuple(
            replace(candidate, state="extracted_candidate")
            for candidate in source_record.candidates
        ),
    )
    client_candidate = next(
        candidate for candidate in bundle.candidates if candidate.field_key == "assignment.client"
    )
    accepted = build_candidate_review_event(
        client_candidate,
        action="candidate_verified",
        actor_id="appraiser-synthetic-001",
        actor_name="Alex Appraiser",
        actor_role="appraiser",
        occurred_at="2026-09-03T14:15:00+00:00",
        reason="Synthetic client accepted.",
    )
    corrected = build_candidate_review_event(
        client_candidate,
        action="candidate_corrected",
        actor_id="reviewer-synthetic-001",
        actor_name="Robin Reviewer",
        actor_role="reviewer",
        occurred_at="2026-09-03T14:16:00+00:00",
        reason="Synthetic client legal name corrected.",
        corrected_value="Example Regional Bank, N.A.",
    )

    record = build_assignment_intelligence_record(
        tenant_id="tenant-synthetic",
        local_assignment_key="assignment-synthetic-revision",
        candidate_bundles=(bundle,),
        review_events=(corrected, accepted),
        created_at=SYNTHETIC_TIMESTAMP,
        updated_at="2026-09-03T14:20:00+00:00",
    )
    revisions = [fact for fact in record.facts if fact.field_key == "assignment.client"]
    prior = next(fact for fact in revisions if fact.state == "superseded")
    current = record.current_fact("assignment.client")

    assert len(revisions) == 2
    assert prior.value == "Example Regional Bank"
    assert current.value == "Example Regional Bank, N.A."
    assert current.supersedes_fact_id == prior.fact_id
    assert set(prior.evidence_ids).issubset(current.evidence_ids)


def test_rejected_candidate_remains_in_history_but_not_current_facts() -> None:
    record = build_synthetic_assignment_intelligence_record()
    candidate = _candidate(record, "assignment.reviewer")
    rejection = next(
        event
        for event in record.review_events
        if event.target_id == candidate.candidate_id and event.action == "candidate_rejected"
    )

    assert candidate.state == "rejected"
    assert record.current_fact("assignment.reviewer") is None
    assert rejection.prior_value == candidate.value
    assert rejection.resulting_value is None


def test_unresolved_conflict_retains_all_candidates_and_blocks_readiness() -> None:
    record = build_synthetic_assignment_intelligence_record()
    conflict = next(
        item for item in record.conflicts if item.field_key == "assignment.intended_use"
    )
    candidates = [
        candidate
        for candidate in record.candidates
        if candidate.candidate_id in set(conflict.candidate_ids)
    ]

    assert conflict.status == "unresolved"
    assert len(candidates) == 2
    assert {candidate.value for candidate in candidates} == {
        "Internal portfolio planning",
        "Loan underwriting",
    }
    assert all(candidate.state == "unresolved_conflict" for candidate in candidates)
    assert any(
        issue.issue_type == "unresolved_conflict"
        and issue.severity == "blocking"
        and issue.field_keys == ("assignment.intended_use",)
        for issue in record.readiness.issues
    )


def test_appraiser_entered_fact_has_audit_basis_without_machine_candidate() -> None:
    record = build_synthetic_assignment_intelligence_record()
    fact = record.current_fact("assignment.interest_appraised")
    event = next(item for item in record.review_events if item.event_id in fact.review_event_ids)

    assert fact.state == "appraiser_entered"
    assert fact.candidate_ids == ()
    assert event.action == "appraiser_fact_entered"
    assert event.reason == "Professional assignment condition entered by the appraiser."


def test_conclusions_are_separate_from_fact_ledger_and_have_audit_event() -> None:
    record = build_assignment_intelligence_record(
        tenant_id="tenant-synthetic",
        local_assignment_key="assignment-with-conclusion",
        candidate_bundles=(),
        review_events=(),
        appraiser_conclusions=(
            AppraiserConclusionInput(
                conclusion_type="highest_and_best_use",
                area="highest_and_best_use",
                statement="Synthetic appraiser-authored conclusion for contract testing only.",
                status="draft",
                actor_id="appraiser-synthetic-001",
                actor_name="Alex Appraiser",
                actor_role="appraiser",
                occurred_at=SYNTHETIC_TIMESTAMP,
                reason="Explicitly authored by the synthetic appraiser.",
            ),
        ),
        created_at=SYNTHETIC_TIMESTAMP,
        updated_at=SYNTHETIC_TIMESTAMP,
    )

    assert record.facts == ()
    assert len(record.conclusions) == 1
    assert record.conclusions[0].conclusion_type == "highest_and_best_use"
    assert any(event.action == "conclusion_entered" for event in record.review_events)


def test_property_comparable_market_and_prior_knowledge_are_references() -> None:
    record = build_synthetic_assignment_intelligence_record()

    assert record.subject_property.property_reference.reference_type == "property"
    assert {item.selection_status for item in record.comparable_references} == {
        "candidate",
        "selected",
    }
    selected = next(item for item in record.comparable_references if item.selection_status == "selected")
    assert selected.knowledge_object_id
    assert record.market_references[0].reference_type == "market_observation"
    assert record.prior_knowledge_references[0].reference_type == "knowledge_object"
    assert not hasattr(record.comparable_references[0], "sale_price")


def test_readiness_explains_missing_conflict_and_unverified_candidate_issues() -> None:
    record = build_synthetic_assignment_intelligence_record()
    issue_types = {item.issue_type for item in record.readiness.issues}
    assignment_area = next(
        area for area in record.readiness.areas if area.area == "assignment_context"
    )

    assert record.readiness.overall_status == "blocked"
    assert "missing_required_fact" in issue_types
    assert "unresolved_conflict" in issue_types
    assert "unverified_material_candidate" in issue_types
    assert record.readiness.blocking_issue_ids
    assert assignment_area.status == "blocked"


def test_schema_version_is_present_and_registered() -> None:
    record = build_synthetic_assignment_intelligence_record()

    assert record.identity.schema_version == ASSIGNMENT_INTELLIGENCE_RECORD_SCHEMA_VERSION
    assert record.to_dict()["identity"]["schema_version"] == "1"


def test_round_trip_serialization_preserves_canonical_record() -> None:
    record = build_synthetic_assignment_intelligence_record()

    rebuilt = AssignmentIntelligenceRecord.from_json(record.to_json())

    assert rebuilt == record
    assert rebuilt.to_json() == record.to_json()


def test_saved_export_uses_the_deterministic_serializer(tmp_path) -> None:
    record = build_synthetic_assignment_intelligence_record()
    output = save_assignment_intelligence_record(record, tmp_path / "synthetic-air.json")

    assert output.read_text(encoding="utf-8") == record.to_json()


def test_section_views_reference_facts_instead_of_copying_values() -> None:
    record = build_synthetic_assignment_intelligence_record()
    current_ids = set(record.current_fact_ids)

    assert set(record.assignment_context.fact_ids).issubset(current_ids)
    assert set(record.subject_property.identity_fact_ids).issubset(current_ids)
    assert all(
        set(group.fact_ids).issubset(current_ids)
        for group in record.subject_property.characteristic_groups
    )
    assert "value" not in record.to_dict()["assignment_context"]


def test_appraiser_entry_must_explicitly_supersede_a_current_fact() -> None:
    record = build_synthetic_assignment_intelligence_record()
    bundle = CandidateEvidenceBundle(
        sources=record.sources,
        evidence=record.evidence,
        candidates=tuple(
            replace(candidate, state="extracted_candidate") for candidate in record.candidates
        ),
    )
    client_review = next(
        event
        for event in record.review_events
        if event.action == "candidate_verified" and event.field_key == "assignment.client"
    )
    replacement = AppraiserFactInput(
        field_key="assignment.client",
        label="Client",
        category="assignment",
        value="Replacement Synthetic Bank",
        value_type="string",
        unit=None,
        material=True,
        actor_id="appraiser-synthetic-001",
        actor_name="Alex Appraiser",
        actor_role="appraiser",
        occurred_at="2026-09-03T14:30:00+00:00",
        reason="Synthetic replacement without explicit lineage.",
    )

    try:
        build_assignment_intelligence_record(
            tenant_id="tenant-synthetic",
            local_assignment_key="assignment-synthetic",
            candidate_bundles=(bundle,),
            review_events=(client_review,),
            appraiser_facts=(replacement,),
            created_at=SYNTHETIC_TIMESTAMP,
            updated_at="2026-09-03T14:30:00+00:00",
        )
    except ValueError as error:
        assert "must explicitly supersede" in str(error)
    else:
        raise AssertionError("Expected explicit supersession validation to fail.")


def _candidate(record: AssignmentIntelligenceRecord, field_key: str):
    return next(item for item in record.candidates if item.field_key == field_key)
