import json

import pytest

from falcon_intel.synthetic_workflow import run_synthetic_intelligence_workflow


ORDER_PAYLOAD = {
    "order_id": "falcon-order-synthetic-001",
    "tenant_id": "tenant-synthetic-001",
    "address": "1000 Example Industrial Way",
    "city": "Sampleton",
    "state": "ST",
    "property_type": "industrial",
    "building_size_sf": 50000,
    "client": "Synthetic Lender A",
    "borrower_contact": "Synthetic Borrower Contact",
}


def test_end_to_end_synthetic_intelligence_workflow() -> None:
    result = run_synthetic_intelligence_workflow(
        ORDER_PAYLOAD,
        user_id="user-synthetic-001",
        role="appraiser",
    ).to_dict()

    assert result["status"] == "ok"
    assert result["card"]["schema_version"] == "1"
    assert result["selected_match"]["passport_id"] == "synthetic-passport-assignment-industrial-alpha"
    assert result["card_permission"]["allowed"] is True
    assert result["passport_permission"]["allowed"] is True
    assert result["passport_response"]["status"] == "ok"
    assert result["passport_response"]["passport"]["passport_id"] == result["selected_match"]["passport_id"]
    assert result["selected_evidence_link"]["evidence_id"] == "synthetic-evidence-assignment-industrial-alpha"
    assert result["evidence_permission"]["allowed"] is True
    assert result["evidence_response"]["status"] == "ok"
    assert result["evidence_response"]["evidence_summary"]["evidence_id"] == result["selected_evidence_link"]["evidence_id"]

    audit_events = result["suggested_audit_events"]
    assert [event["event_code"] for event in audit_events] == [
        "viewed_match",
        "opened_evidence",
        "opened_evidence",
    ]
    assert audit_events[0]["metadata"]["selected_passport_id"] == result["selected_match"]["passport_id"]
    assert audit_events[1]["metadata"]["detail_type"] == "data_passport"
    assert audit_events[2]["metadata"]["detail_type"] == "evidence_link"

    serialized = json.dumps(result).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized


def test_synthetic_workflow_denies_client_role() -> None:
    with pytest.raises(PermissionError, match="denied_client_role"):
        run_synthetic_intelligence_workflow(
            ORDER_PAYLOAD,
            user_id="user-synthetic-client",
            role="client",
        )
