import json
from pathlib import Path

from falcon_intel.falcon_api_contract import build_falcon_intelligence_card_response
from falcon_intel.schema_registry import FALCON_CARD_API_RESPONSE_SCHEMA_VERSION


SNAPSHOT_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "synthetic_ui_cards"
    / "firm-intelligence-card-v1.json"
)


def test_falcon_card_boundary_returns_v1_snapshot_schema() -> None:
    response = build_falcon_intelligence_card_response(_order_payload())
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert response["status"] == "ok"
    assert response["order_id"] == "falcon-order-synthetic-001"
    assert response["tenant_id"] == "tenant-synthetic-001"
    assert response["schema_version"] == FALCON_CARD_API_RESPONSE_SCHEMA_VERSION
    assert response["card"]["schema_version"] == "1"
    assert response["card"] == snapshot


def test_falcon_card_boundary_reports_missing_required_fields() -> None:
    payload = _order_payload()
    payload.pop("property_type")
    payload["client"] = ""

    response = build_falcon_intelligence_card_response(payload)

    assert response == {
        "status": "missing_required_input",
        "order_id": "falcon-order-synthetic-001",
        "tenant_id": "tenant-synthetic-001",
        "schema_version": FALCON_CARD_API_RESPONSE_SCHEMA_VERSION,
        "error": {
            "code": "missing_required_input",
            "message": "Falcon order payload is missing required fields.",
            "missing_fields": ["property_type", "client"],
        },
    }


def test_falcon_card_boundary_output_is_synthetic_only() -> None:
    response = build_falcon_intelligence_card_response(_order_payload())
    serialized = json.dumps(response).lower()

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized


def _order_payload() -> dict[str, object]:
    return {
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
