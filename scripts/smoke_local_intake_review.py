"""Dependency-free smoke proof for Local Intake Review and Brief V1."""

from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.assignment_brief import export_assignment_property_brief
from falcon_intel.assignment_intelligence_record import AssignmentIntelligenceRecord
from falcon_intel.synthetic_local_intake_review import build_synthetic_local_intake_review_proof


def main() -> None:
    first = build_synthetic_local_intake_review_proof()
    second = build_synthetic_local_intake_review_proof()
    assert len(first.record.candidates) >= 15
    assert first.record.to_json() == second.record.to_json()
    assert first.brief.to_json() == second.brief.to_json()
    assert {item.state for item in first.record.candidates} >= {
        "accepted",
        "corrected",
        "rejected",
        "deferred",
    }
    assert {item.status for item in first.record.conflicts} == {"resolved", "unresolved"}
    assert first.record.current_fact("assignment.appraisal_purpose") is None
    assert first.record.readiness.overall_status == "blocked"

    with TemporaryDirectory() as directory:
        paths = export_assignment_property_brief(first.record, first.brief, directory)
        rebuilt = AssignmentIntelligenceRecord.from_json(
            Path(paths["air_json"]).read_text(encoding="utf-8")
        )
        assert rebuilt == first.record
        assert Path(paths["brief_json"]).read_text(encoding="utf-8") == first.brief.to_json()
        assert Path(paths["brief_markdown"]).read_text(encoding="utf-8") == first.brief.to_markdown()

    print("local intake review and brief smoke validation passed")


if __name__ == "__main__":
    main()
