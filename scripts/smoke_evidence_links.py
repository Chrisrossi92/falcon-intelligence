"""Smoke validation for synthetic/local evidence link payloads."""

import json

from falcon_intel.evidence_link import (
    EvidenceAccessLevel,
    build_comparable_support_evidence_link,
    build_market_support_evidence_link,
    build_source_document_evidence_link,
    build_source_report_evidence_link,
)


def main() -> None:
    base_context = {
        "tenant_id": "tenant-synthetic-001",
        "assignment_id": "assignment-synthetic-industrial-001",
        "source_document_id": "source-doc-synthetic-001",
    }
    links = [
        build_source_report_evidence_link(
            **base_context,
            evidence_id="synthetic-evidence-source-report-001",
            display_label="Synthetic source report metadata",
            future_page_number=8,
            future_section_anchor="synthetic-sales-comparison",
        ),
        build_source_document_evidence_link(
            **base_context,
            evidence_id="synthetic-evidence-source-document-001",
            display_label="Synthetic source document metadata",
        ),
        build_comparable_support_evidence_link(
            **base_context,
            evidence_id="synthetic-evidence-comparable-support-001",
            display_label="Synthetic comparable support metadata",
        ),
        build_market_support_evidence_link(
            **base_context,
            evidence_id="synthetic-evidence-market-support-001",
            display_label="Synthetic market support metadata",
            access_level=EvidenceAccessLevel.OWNER_ADMIN_ONLY,
        ),
    ]

    payload = [link.to_dict() for link in links]
    assert [link["source_document_type"] for link in payload] == [
        "source_report",
        "source_document",
        "comparable_support",
        "market_support",
    ]
    assert payload[2]["access_level"] == "appraiser_reviewer_only"
    assert payload[3]["access_level"] == "owner_admin_only"

    serialized = json.dumps(payload).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("evidence link smoke validation passed")


if __name__ == "__main__":
    main()
