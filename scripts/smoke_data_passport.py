"""Smoke validation for synthetic/local data passport payloads."""

import json

from falcon_intel.data_passport import (
    SearchableStatus,
    VerificationStatus,
    build_confidence_dimensions,
    build_data_passport,
)
from falcon_intel.evidence_link import build_source_report_evidence_link


def main() -> None:
    evidence_link = build_source_report_evidence_link(
        evidence_id="synthetic-evidence-source-report-001",
        tenant_id="tenant-synthetic-001",
        assignment_id="assignment-synthetic-industrial-001",
        source_document_id="source-doc-synthetic-report-001",
        display_label="Synthetic source report metadata",
        future_page_number=10,
        future_section_anchor="synthetic-improvements",
    )
    dimensions = build_confidence_dimensions(
        extraction_confidence="not_applicable_synthetic",
        source_quality="verified_synthetic_source_metadata",
        source_agreement="single_verified_synthetic_record",
        freshness="current_for_synthetic_fixture",
        reviewer_approval="reviewed",
        historical_consistency="consistent_with_synthetic_history",
    )
    passport = build_data_passport(
        fact_id="synthetic-fact-building-size-001",
        tenant_id="tenant-synthetic-001",
        assignment_id="assignment-synthetic-industrial-001",
        fact_type="building_size_sf",
        display_label="Building size",
        display_value="48,000 sf",
        verification_status=VerificationStatus.VERIFIED,
        verified_by="synthetic-appraiser-001",
        verified_at="2026-06-24T12:00:00+00:00",
        reviewed_by="synthetic-reviewer-001",
        reviewed_at="2026-06-24T13:00:00+00:00",
        confidence_dimensions=dimensions,
        evidence_links=[evidence_link],
        audit_event_ids=["audit-synthetic-evidence-001"],
        searchable_status=SearchableStatus.SEARCHABLE,
    ).to_dict()

    assert passport["verification_status"] == "verified"
    assert passport["searchable_status"] == "searchable"
    assert passport["confidence_dimensions"]["reviewer_approval"] == "reviewed"
    assert passport["evidence_links"][0]["source_document_type"] == "source_report"
    assert passport["audit_event_ids"] == ["audit-synthetic-evidence-001"]

    serialized = json.dumps(passport).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("data passport smoke validation passed")


if __name__ == "__main__":
    main()
