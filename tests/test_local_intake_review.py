import json
from pathlib import Path

from falcon_intel.assignment_brief import (
    build_assignment_property_brief,
    export_assignment_property_brief,
    validate_local_output_directory,
)
from falcon_intel.assignment_intelligence_record import AssignmentIntelligenceRecord
from falcon_intel.local_intake_review import ReviewActor, topic_for_field
from falcon_intel.synthetic_local_intake_review import (
    build_synthetic_local_intake_review_proof,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "synthetic_intake_review"
    / "local-intake-review-workspace-v1.json"
)


def test_synthetic_review_proof_uses_extracted_candidates_across_topics() -> None:
    proof = build_synthetic_local_intake_review_proof()

    assert len(proof.record.candidates) >= 15
    assert len(proof.record.sources) == 2
    assert len(proof.workspace["topics"]) >= 6
    assert proof.workspace["semantic_source"]["canonical_model"] == "assignment_intelligence_record"
    assert {topic_for_field(item.field_key) for item in proof.record.candidates} >= {
        "assignment_and_engagement",
        "client_and_intended_users",
        "intended_use_and_appraisal_purpose",
        "important_dates",
        "subject_identity_and_location",
        "comparables_and_market_references",
        "signing_and_review_information",
    }


def test_accept_correct_reject_and_defer_preserve_air_semantics() -> None:
    record = build_synthetic_local_intake_review_proof().record
    states = {item.state for item in record.candidates}
    property_candidate = next(
        item for item in record.candidates if item.field_key == "subject.property_type"
    )
    corrected = record.current_fact("subject.property_type")
    rejected = next(item for item in record.candidates if item.state == "rejected")
    deferred = next(item for item in record.candidates if item.state == "deferred")

    assert {"accepted", "corrected", "rejected", "deferred"}.issubset(states)
    assert property_candidate.value == "Industrial"
    assert corrected.value == "Industrial / Distribution Warehouse"
    assert corrected.candidate_ids == (property_candidate.candidate_id,)
    assert record.current_fact(rejected.field_key) is None
    assert record.current_fact(deferred.field_key) is None
    assert any(
        item.action == "candidate_deferred" and item.target_id == deferred.candidate_id
        for item in record.review_events
    )


def test_rejection_retains_candidate_reason_and_evidence() -> None:
    record = build_synthetic_local_intake_review_proof().record
    candidate = next(
        item
        for item in record.candidates
        if item.field_key == "assignment.reviewer" and item.state == "rejected"
    )
    event = next(item for item in record.review_events if item.target_id == candidate.candidate_id)

    assert candidate.evidence_ids
    assert event.action == "candidate_rejected"
    assert "not assigned" in event.reason
    assert event.prior_value == candidate.value


def test_appraiser_entered_fact_has_explicit_provenance() -> None:
    record = build_synthetic_local_intake_review_proof().record
    fact = record.current_fact("subject.building_area")
    event = next(item for item in record.review_events if item.event_id in fact.review_event_ids)

    assert fact.origin == "appraiser_entry"
    assert fact.state == "appraiser_entered"
    assert fact.value == 186500
    assert event.action == "appraiser_fact_entered"
    assert event.actor_role == "appraiser"
    assert event.reason


def test_conflict_resolution_selects_one_candidate_without_losing_its_fact() -> None:
    record = build_synthetic_local_intake_review_proof().record
    conflict = next(item for item in record.conflicts if item.field_key == "assignment.client")
    client = record.current_fact("assignment.client")

    assert conflict.status == "resolved"
    assert len(conflict.resolution_event_ids) == len(conflict.candidate_ids)
    assert client.value == "Example Regional Bank, N.A."
    assert client.candidate_ids[0] in conflict.candidate_ids
    assert len(
        [item for item in record.candidates if item.candidate_id in conflict.candidate_ids and item.state == "rejected"]
    ) == len(conflict.candidate_ids) - 1


def test_unresolved_conflicts_and_missing_critical_fields_remain_visible() -> None:
    proof = build_synthetic_local_intake_review_proof()
    unresolved_fields = {
        item.field_key for item in proof.record.conflicts if item.status == "unresolved"
    }
    missing_fields = {
        key
        for item in proof.workspace["missing_critical_information"]
        for key in item["field_keys"]
    }

    assert "assignment.intended_use" in unresolved_fields
    assert "assignment.appraisal_purpose" in missing_fields
    assert proof.record.readiness.overall_status == "blocked"
    assert any(
        item.issue_type == "deferred_review_candidate"
        for item in proof.record.readiness.issues
    )


def test_readiness_recalculates_after_an_explicit_candidate_decision() -> None:
    proof = build_synthetic_local_intake_review_proof()
    candidate = next(
        item
        for item in proof.record.candidates
        if item.field_key == "assignment.extraordinary_assumptions_present"
    )
    assert any(
        candidate.candidate_id in item.related_ids
        for item in proof.record.readiness.issues
    )

    reviewed = proof.session.accept(
        candidate.candidate_id,
        actor=ReviewActor(
            actor_id="synthetic-readiness-test",
            actor_name="Readiness Test Appraiser",
            actor_role="appraiser",
        ),
        occurred_at="2026-09-03T16:01:00+00:00",
    ).assemble_air()

    assert reviewed.current_fact(candidate.field_key) is not None
    assert not any(
        candidate.candidate_id in item.related_ids
        for item in reviewed.readiness.issues
    )


def test_review_actions_requiring_reasons_are_enforced() -> None:
    proof = build_synthetic_local_intake_review_proof()
    candidate = next(item for item in proof.record.candidates if item.state == "extracted_candidate")

    try:
        proof.session.reject(
            candidate.candidate_id,
            actor=ReviewActor(
                actor_id="synthetic-reason-test",
                actor_name="Reason Test Appraiser",
                actor_role="appraiser",
            ),
            occurred_at="2026-09-03T16:00:00+00:00",
            reason="",
        )
    except ValueError as error:
        assert "requires a reason" in str(error)
    else:
        raise AssertionError("Expected a blank rejection reason to fail.")


def test_brief_uses_only_current_air_facts_and_never_fabricates_absent_values() -> None:
    proof = build_synthetic_local_intake_review_proof()
    brief = build_assignment_property_brief(proof.record)
    fields = {
        item.field_key for item in (*brief.assignment_synopsis, *brief.subject_synopsis)
    }

    assert "assignment.client" in fields
    assert "subject.address" in fields
    assert "assignment.appraisal_purpose" not in fields
    assert "assignment.intended_use" not in fields
    assert brief.professional_conclusions == ()
    assert "No professional conclusions" in brief.to_markdown()


def test_brief_separates_verified_corrected_and_appraiser_entered_facts() -> None:
    brief = build_synthetic_local_intake_review_proof().brief
    boundaries = {
        item.field_key: item.professional_boundary
        for item in (*brief.assignment_synopsis, *brief.subject_synopsis)
    }

    assert boundaries["assignment.client"] == "verified_fact"
    assert boundaries["subject.property_type"] == "corrected_fact"
    assert boundaries["subject.building_area"] == "appraiser_entered_fact"
    assert any("Professional conclusions are separate" in item for item in brief.professional_boundary)


def test_brief_evidence_is_traceable_to_air_sources_and_facts() -> None:
    proof = build_synthetic_local_intake_review_proof()
    evidence_ids = {item.evidence_id for item in proof.record.evidence}
    fact_ids = {item.fact_id for item in proof.record.facts}

    assert proof.brief.evidence_summary
    assert all(item.evidence_id in evidence_ids for item in proof.brief.evidence_summary)
    assert all(set(item.fact_ids).issubset(fact_ids) for item in proof.brief.evidence_summary)
    assert all(item.source_document.startswith("Synthetic") for item in proof.brief.evidence_summary)
    assert all(item.extraction_method for item in proof.brief.evidence_summary)


def test_brief_exports_are_deterministic_and_round_trip_air(tmp_path: Path) -> None:
    proof = build_synthetic_local_intake_review_proof()
    first = export_assignment_property_brief(proof.record, proof.brief, tmp_path / "first")
    second = export_assignment_property_brief(proof.record, proof.brief, tmp_path / "second")

    for key in first:
        assert Path(first[key]).read_bytes() == Path(second[key]).read_bytes()
    rebuilt = AssignmentIntelligenceRecord.from_json(
        Path(first["air_json"]).read_text(encoding="utf-8")
    )
    assert rebuilt == proof.record
    assert json.loads(Path(first["brief_json"]).read_text(encoding="utf-8")) == json.loads(
        proof.brief.to_json()
    )


def test_safe_export_boundary_rejects_tracked_repository_locations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"

    try:
        validate_local_output_directory(repo / "src" / "generated", repository_root=repo)
    except ValueError as error:
        assert "ignored local output root" in str(error)
    else:
        raise AssertionError("Expected a tracked repository destination to fail.")

    assert validate_local_output_directory(
        repo / "data" / "local-intake-review",
        repository_root=repo,
    ) == (repo / "data" / "local-intake-review").resolve()


def test_workspace_progress_and_provenance_are_derived_from_air() -> None:
    proof = build_synthetic_local_intake_review_proof()
    progress = proof.workspace["review_progress"]
    rows = [item for topic in proof.workspace["topics"] for item in topic["candidates"]]

    assert progress["total_candidates"] == len(proof.record.candidates)
    assert progress["reviewed_candidates"] == sum(
        item.state in {"accepted", "corrected", "rejected", "deferred"}
        for item in proof.record.candidates
    )
    assert all(item["field_key"].count(".") >= 1 for item in rows)
    assert all(item["evidence"] for item in rows)
    assert all(item["evidence"][0]["source_document"] for item in rows)


def test_synthetic_proof_is_rebuild_equivalent() -> None:
    first = build_synthetic_local_intake_review_proof()
    second = build_synthetic_local_intake_review_proof()

    assert first.session.assemble_air() == first.record
    assert first.record.to_json() == second.record.to_json()
    assert first.brief.to_json() == second.brief.to_json()
    assert first.workspace == second.workspace


def test_committed_frontend_workspace_snapshot_matches_backend_projection() -> None:
    proof = build_synthetic_local_intake_review_proof()

    assert json.loads(FIXTURE_PATH.read_text(encoding="utf-8")) == proof.workspace
