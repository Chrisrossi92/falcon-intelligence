import json
from pathlib import Path

from falcon_intel.knowledge_objects import (
    KnowledgeObjectsReport,
    build_knowledge_objects_summary,
    build_report_knowledge_objects,
    render_knowledge_objects_summary,
    run_knowledge_object_builder,
    save_knowledge_object_outputs,
)


def _fact(field_name: str, value: str | None, status: str = "verified", confidence: str = "high") -> dict[str, object]:
    return {
        "field_name": field_name,
        "verified_value": value,
        "verification_status": status,
        "confidence": confidence,
        "supporting_evidence": [],
        "conflicting_evidence": [],
        "verification_method": "synthetic test rule",
        "verification_timestamp": "2026-06-30T00:00:00+00:00",
        "notes": [],
        "source_references": [f"synthetic:{field_name}"] if value else [],
    }


def _report_facts(*facts: dict[str, object]) -> dict[str, object]:
    return {
        "file_id": "synthetic-final",
        "file_name": "Synthetic Restricted Appraisal Report.pdf",
        "file_path": "synthetic/Synthetic Restricted Appraisal Report.pdf",
        "facts": list(facts),
        "warnings": [],
    }


def _objects(report_facts: dict[str, object]) -> dict[str, object]:
    package = build_report_knowledge_objects(report_facts, timestamp="2026-06-30T00:00:00+00:00")
    return {candidate.object_type: candidate for candidate in package.object_candidates}


def test_builds_property_object_from_verified_facts() -> None:
    objects = _objects(
        _report_facts(
            _fact("property_address", "100 Sample Industrial Avenue"),
            _fact("property_type", "Industrial"),
        )
    )

    property_object = objects["property"]

    assert property_object.readiness == "ready"
    assert property_object.readiness_reason == "verified_high_confidence"
    assert property_object.display_label == "100 Sample Industrial Avenue"
    assert property_object.source_verified_facts == ("property_address", "property_type")
    assert property_object.attributes["normalized_identity_key"] == "100-sample-industrial-avenue"


def test_blocks_property_object_on_address_conflict() -> None:
    objects = _objects(
        _report_facts(
            _fact("property_address", None, "conflicting", "conflicting"),
            _fact("property_type", "Industrial", "probable", "medium"),
        )
    )

    property_object = objects["property"]

    assert property_object.readiness == "blocked"
    assert property_object.readiness_reason == "blocked_by_conflict"
    assert property_object.conflicting_fields == ("property_address",)
    assert property_object.missing_required_fields == ("property_address",)


def test_builds_report_object_from_report_identity_facts() -> None:
    objects = _objects(
        _report_facts(
            _fact("report_type", "restricted appraisal report"),
            _fact("effective_date", "June 1, 2026", "probable", "medium"),
            _fact("income_approach", "present", "probable", "medium"),
        )
    )

    report_object = objects["report"]

    assert report_object.readiness == "needs_review"
    assert report_object.display_label == "restricted appraisal report report object"
    assert report_object.attributes["effective_date"] == "June 1, 2026"
    assert report_object.review_required_fields == ("effective_date",)


def test_client_user_conflict_needs_review_without_promotion() -> None:
    objects = _objects(
        _report_facts(
            _fact("client", "Example Bank"),
            _fact("intended_user", None, "conflicting", "conflicting"),
        )
    )

    client_user = objects["client_user"]

    assert client_user.readiness == "blocked"
    assert client_user.conflicting_fields == ("intended_user",)
    assert "intended_user" in client_user.missing_required_fields


def test_personnel_object_needs_review_when_probable_or_reviewer_missing() -> None:
    objects = _objects(
        _report_facts(
            _fact("appraiser_name", "Synthetic Appraiser", "probable", "medium"),
            _fact("reviewer_name", None, "missing", "missing"),
        )
    )

    personnel = objects["personnel"]

    assert personnel.readiness == "needs_review"
    assert personnel.missing_required_fields == ("reviewer_name",)
    assert personnel.review_required_fields == ("appraiser_name",)
    assert personnel.confidence == "low"


def test_probable_property_does_not_promote_to_ready() -> None:
    objects = _objects(
        _report_facts(
            _fact("property_address", "100 Sample Industrial Avenue", "probable", "medium"),
        )
    )

    property_object = objects["property"]

    assert property_object.readiness == "needs_review"
    assert property_object.review_required_fields == ("property_address",)
    assert property_object.missing_required_fields == ()


def test_missing_only_facts_do_not_create_domain_objects() -> None:
    package = build_report_knowledge_objects(
        _report_facts(
            _fact("property_address", None, "missing", "missing"),
            _fact("effective_date", None, "missing", "missing"),
        ),
        timestamp="2026-06-30T00:00:00+00:00",
    )

    assert package.object_candidates == ()


def test_open_issues_object_collects_conflicts_and_missing_fields() -> None:
    objects = _objects(
        _report_facts(
            _fact("property_address", None, "conflicting", "conflicting"),
            _fact("reviewer_name", None, "missing", "missing"),
            _fact("inspection_date", "June 2, 2026", "needs_review", "low"),
        )
    )

    open_issues = objects["open_issues"]

    assert open_issues.readiness == "blocked"
    assert open_issues.conflicting_fields == ("property_address",)
    assert open_issues.missing_required_fields == ("reviewer_name",)
    assert "inspection_date" in open_issues.source_verified_facts


def test_summary_generation_and_outputs(tmp_path: Path) -> None:
    package = build_report_knowledge_objects(
        _report_facts(
            _fact("property_address", "100 Sample Industrial Avenue"),
            _fact("report_type", "restricted appraisal report"),
            _fact("effective_date", "June 1, 2026"),
        ),
        timestamp="2026-06-30T00:00:00+00:00",
    )
    report = KnowledgeObjectsReport(
        knowledge_object_version="1",
        generated_at="2026-06-30T00:00:00+00:00",
        source_verification_path="synthetic-verification.json",
        reports=(package,),
    )

    summary = build_knowledge_objects_summary(report)
    outputs = save_knowledge_object_outputs(report, tmp_path)

    assert summary["object_count"] == 2
    assert Path(outputs["json"]).exists()
    assert Path(outputs["markdown"]).name == "knowledge-objects-summary.md"
    assert "deterministic Knowledge Object candidates only" in render_knowledge_objects_summary(report)


def test_runner_consumes_verification_output(tmp_path: Path) -> None:
    verification_path = tmp_path / "verification-report.json"
    verification_path.write_text(
        json.dumps(
            {
                "report_facts": [
                    _report_facts(
                        _fact("property_address", "100 Sample Industrial Avenue"),
                        _fact("report_type", "restricted appraisal report"),
                        _fact("effective_date", "June 1, 2026"),
                    )
                ],
                "warnings": [],
                "errors": [],
            }
        ),
        encoding="utf-8",
    )

    report = run_knowledge_object_builder(verification_path)

    assert report.reports[0].file_id == "synthetic-final"
    assert build_knowledge_objects_summary(report)["object_type_breakdown"]["property"] == 1
