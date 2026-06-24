import json

import pytest

from falcon_intel.data_passport import (
    SearchableStatus,
    VerificationStatus,
    build_confidence_dimensions,
    build_data_passport,
)
from falcon_intel.evidence_link import build_source_report_evidence_link


BASE_LINK = build_source_report_evidence_link(
    evidence_id="synthetic-evidence-source-report-001",
    tenant_id="tenant-synthetic-001",
    assignment_id="assignment-synthetic-industrial-001",
    source_document_id="source-doc-synthetic-report-001",
    display_label="Synthetic source report metadata",
    future_page_number=10,
    future_section_anchor="synthetic-improvements",
)

BASE_DIMENSIONS = build_confidence_dimensions(
    extraction_confidence="not_applicable_synthetic",
    source_quality="verified_synthetic_source_metadata",
    source_agreement="single_verified_synthetic_record",
    freshness="current_for_synthetic_fixture",
    reviewer_approval="reviewed",
    historical_consistency="consistent_with_synthetic_history",
)


def test_builds_data_passport_payload_with_evidence_links() -> None:
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
        confidence_dimensions=BASE_DIMENSIONS,
        evidence_links=[BASE_LINK],
        audit_event_ids=["audit-synthetic-viewed-001", "audit-synthetic-evidence-001"],
        searchable_status=SearchableStatus.SEARCHABLE,
    ).to_dict()

    assert passport == {
        "fact_id": "synthetic-fact-building-size-001",
        "tenant_id": "tenant-synthetic-001",
        "assignment_id": "assignment-synthetic-industrial-001",
        "fact_type": "building_size_sf",
        "display_label": "Building size",
        "display_value": "48,000 sf",
        "verification_status": "verified",
        "verified_by": "synthetic-appraiser-001",
        "verified_at": "2026-06-24T12:00:00+00:00",
        "reviewed_by": "synthetic-reviewer-001",
        "reviewed_at": "2026-06-24T13:00:00+00:00",
        "confidence_dimensions": {
            "extraction_confidence": "not_applicable_synthetic",
            "source_quality": "verified_synthetic_source_metadata",
            "source_agreement": "single_verified_synthetic_record",
            "freshness": "current_for_synthetic_fixture",
            "reviewer_approval": "reviewed",
            "historical_consistency": "consistent_with_synthetic_history",
        },
        "evidence_links": [BASE_LINK.to_dict()],
        "audit_event_ids": ["audit-synthetic-viewed-001", "audit-synthetic-evidence-001"],
        "searchable_status": "searchable",
    }


def test_accepts_confidence_dimensions_and_evidence_links_as_dicts() -> None:
    passport = build_data_passport(
        fact_id="synthetic-fact-market-rent-001",
        tenant_id="tenant-synthetic-001",
        assignment_id="assignment-synthetic-retail-001",
        fact_type="market_indicator",
        display_label="Market rent range",
        display_value="Synthetic range only",
        verification_status="reviewed",
        verified_by="synthetic-appraiser-002",
        verified_at="2026-06-24T12:00:00+00:00",
        confidence_dimensions=BASE_DIMENSIONS.to_dict(),
        evidence_links=[BASE_LINK.to_dict()],
        searchable_status="restricted",
    )

    assert passport.verification_status == "reviewed"
    assert passport.searchable_status == "restricted"
    assert passport.reviewed_by is None
    assert passport.audit_event_ids == []


def test_validates_required_fields_and_statuses() -> None:
    with pytest.raises(ValueError, match="fact_id"):
        build_data_passport(
            fact_id="",
            tenant_id="tenant-synthetic-001",
            assignment_id="assignment-synthetic-industrial-001",
            fact_type="building_size_sf",
            display_label="Building size",
            display_value="48,000 sf",
            verification_status=VerificationStatus.VERIFIED,
            verified_by="synthetic-appraiser-001",
            verified_at="2026-06-24T12:00:00+00:00",
            confidence_dimensions=BASE_DIMENSIONS,
            evidence_links=[BASE_LINK],
            searchable_status=SearchableStatus.SEARCHABLE,
        )

    with pytest.raises(ValueError):
        build_data_passport(
            fact_id="synthetic-fact-building-size-001",
            tenant_id="tenant-synthetic-001",
            assignment_id="assignment-synthetic-industrial-001",
            fact_type="building_size_sf",
            display_label="Building size",
            display_value="48,000 sf",
            verification_status="unsupported_status",
            verified_by="synthetic-appraiser-001",
            verified_at="2026-06-24T12:00:00+00:00",
            confidence_dimensions=BASE_DIMENSIONS,
            evidence_links=[BASE_LINK],
            searchable_status=SearchableStatus.SEARCHABLE,
        )

    with pytest.raises(ValueError, match="evidence_links"):
        build_data_passport(
            fact_id="synthetic-fact-building-size-001",
            tenant_id="tenant-synthetic-001",
            assignment_id="assignment-synthetic-industrial-001",
            fact_type="building_size_sf",
            display_label="Building size",
            display_value="48,000 sf",
            verification_status=VerificationStatus.VERIFIED,
            verified_by="synthetic-appraiser-001",
            verified_at="2026-06-24T12:00:00+00:00",
            confidence_dimensions=BASE_DIMENSIONS,
            evidence_links=[],
            searchable_status=SearchableStatus.SEARCHABLE,
        )


def test_validates_confidence_dimension_fields() -> None:
    with pytest.raises(ValueError, match="freshness"):
        build_confidence_dimensions(
            extraction_confidence="not_applicable_synthetic",
            source_quality="verified_synthetic_source_metadata",
            source_agreement="single_verified_synthetic_record",
            freshness="",
            reviewer_approval="reviewed",
            historical_consistency="consistent_with_synthetic_history",
        )

    with pytest.raises(ValueError, match="missing required fields"):
        build_data_passport(
            fact_id="synthetic-fact-building-size-001",
            tenant_id="tenant-synthetic-001",
            assignment_id="assignment-synthetic-industrial-001",
            fact_type="building_size_sf",
            display_label="Building size",
            display_value="48,000 sf",
            verification_status=VerificationStatus.VERIFIED,
            verified_by="synthetic-appraiser-001",
            verified_at="2026-06-24T12:00:00+00:00",
            confidence_dimensions={"source_quality": "verified_synthetic_source_metadata"},
            evidence_links=[BASE_LINK],
            searchable_status=SearchableStatus.SEARCHABLE,
        )


def test_data_passport_payload_contains_no_source_content_or_paths() -> None:
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
        confidence_dimensions=BASE_DIMENSIONS,
        evidence_links=[BASE_LINK],
        searchable_status=SearchableStatus.SEARCHABLE,
    ).to_dict()
    serialized = json.dumps(passport).lower()

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized
