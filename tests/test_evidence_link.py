import json

import pytest

from falcon_intel.evidence_link import (
    EVIDENCE_ACCESS_LEVEL_CODES,
    EvidenceAccessLevel,
    EvidenceLinkStatus,
    build_comparable_support_evidence_link,
    build_evidence_link,
    build_market_support_evidence_link,
    build_source_document_evidence_link,
    build_source_report_evidence_link,
)


BASE_CONTEXT = {
    "evidence_id": "synthetic-evidence-source-report-001",
    "tenant_id": "tenant-synthetic-001",
    "assignment_id": "assignment-synthetic-industrial-001",
    "source_document_id": "source-doc-synthetic-report-001",
    "display_label": "Synthetic source report metadata",
}


def test_access_level_codes_are_stable() -> None:
    assert list(EVIDENCE_ACCESS_LEVEL_CODES) == [
        "internal_only",
        "appraiser_reviewer_only",
        "owner_admin_only",
        "disabled",
    ]


def test_builds_source_report_evidence_link() -> None:
    link = build_source_report_evidence_link(
        **BASE_CONTEXT,
        future_page_number=12,
        future_section_anchor="sales-comparison-approach",
        future_highlight_text="Synthetic placeholder highlight only.",
    ).to_dict()

    assert link == {
        "evidence_id": "synthetic-evidence-source-report-001",
        "tenant_id": "tenant-synthetic-001",
        "assignment_id": "assignment-synthetic-industrial-001",
        "source_document_id": "source-doc-synthetic-report-001",
        "source_document_type": "source_report",
        "display_label": "Synthetic source report metadata",
        "access_level": "internal_only",
        "future_page_number": 12,
        "future_section_anchor": "sales-comparison-approach",
        "future_highlight_text": "Synthetic placeholder highlight only.",
        "status": "placeholder",
    }


def test_helper_builders_set_expected_source_types_and_access() -> None:
    links = [
        build_source_document_evidence_link(
            **{**BASE_CONTEXT, "evidence_id": "synthetic-evidence-source-document-001"},
        ),
        build_comparable_support_evidence_link(
            **{**BASE_CONTEXT, "evidence_id": "synthetic-evidence-comp-support-001"},
        ),
        build_market_support_evidence_link(
            **{**BASE_CONTEXT, "evidence_id": "synthetic-evidence-market-support-001"},
            access_level=EvidenceAccessLevel.OWNER_ADMIN_ONLY,
        ),
    ]

    assert [link.source_document_type for link in links] == [
        "source_document",
        "comparable_support",
        "market_support",
    ]
    assert links[1].access_level == "appraiser_reviewer_only"
    assert links[2].access_level == "owner_admin_only"


def test_disabled_access_forces_disabled_status() -> None:
    link = build_source_report_evidence_link(
        **BASE_CONTEXT,
        access_level=EvidenceAccessLevel.DISABLED,
        status=EvidenceLinkStatus.PLACEHOLDER,
    )

    assert link.access_level == "disabled"
    assert link.status == "disabled"


def test_validates_required_fields_and_codes() -> None:
    with pytest.raises(ValueError, match="evidence_id"):
        build_source_report_evidence_link(
            **{**BASE_CONTEXT, "evidence_id": ""},
        )

    with pytest.raises(ValueError):
        build_evidence_link(
            **BASE_CONTEXT,
            source_document_type="unsupported_type",
            access_level=EvidenceAccessLevel.INTERNAL_ONLY,
        )

    with pytest.raises(ValueError):
        build_source_report_evidence_link(
            **BASE_CONTEXT,
            access_level="unsupported_access",
        )

    with pytest.raises(ValueError, match="future_page_number"):
        build_source_report_evidence_link(
            **BASE_CONTEXT,
            future_page_number=0,
        )


def test_evidence_link_payload_contains_no_source_content_or_paths() -> None:
    link = build_comparable_support_evidence_link(
        **BASE_CONTEXT,
        future_section_anchor="synthetic-comp-grid",
    ).to_dict()
    serialized = json.dumps(link).lower()

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized
