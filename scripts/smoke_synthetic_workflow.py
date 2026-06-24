"""Smoke validation for the end-to-end synthetic intelligence workflow."""

import json

from falcon_intel.synthetic_workflow import run_synthetic_intelligence_workflow


def main() -> None:
    result = run_synthetic_intelligence_workflow(
        {
            "order_id": "falcon-order-synthetic-001",
            "tenant_id": "tenant-synthetic-001",
            "address": "1000 Example Industrial Way",
            "city": "Sampleton",
            "state": "ST",
            "property_type": "industrial",
            "building_size_sf": 50000,
            "client": "Synthetic Lender A",
            "borrower_contact": "Synthetic Borrower Contact",
        },
        user_id="user-synthetic-001",
        role="appraiser",
    ).to_dict()

    assert result["status"] == "ok"
    assert result["card"]["schema_version"] == "1"
    assert result["selected_match"]["passport_id"]
    assert result["card_permission"]["allowed"] is True
    assert result["passport_permission"]["allowed"] is True
    assert result["passport_response"]["status"] == "ok"
    assert result["selected_evidence_link"]["evidence_id"]
    assert result["evidence_permission"]["allowed"] is True
    assert result["evidence_response"]["status"] == "ok"
    assert [event["event_code"] for event in result["suggested_audit_events"]] == [
        "viewed_match",
        "opened_evidence",
        "opened_evidence",
    ]

    serialized = json.dumps(result).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("end-to-end synthetic intelligence workflow smoke validation passed")


if __name__ == "__main__":
    main()
