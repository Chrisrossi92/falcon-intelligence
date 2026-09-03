"""Smoke check for the synthetic Assignment Intelligence Record V1 proof."""

from falcon_intel.assignment_intelligence_record import AssignmentIntelligenceRecord
from falcon_intel.synthetic_assignment_record import (
    build_synthetic_assignment_intelligence_record,
)


def main() -> int:
    first = build_synthetic_assignment_intelligence_record()
    rebuilt = build_synthetic_assignment_intelligence_record()
    assert first.to_json() == rebuilt.to_json()

    round_trip = AssignmentIntelligenceRecord.from_json(first.to_json())
    assert round_trip.to_json() == first.to_json()
    assert first.identity.schema_version == "1"
    assert first.current_fact("assignment.client") is not None
    assert first.current_fact("subject.property_type").state == "corrected"
    assert any(candidate.state == "rejected" for candidate in first.candidates)
    assert any(conflict.status == "unresolved" for conflict in first.conflicts)
    assert first.readiness.overall_status == "blocked"
    assert first.comparable_references[0].comparable_id
    assert first.conclusions == ()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
