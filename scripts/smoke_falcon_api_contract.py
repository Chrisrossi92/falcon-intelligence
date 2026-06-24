"""Smoke validation for the local Falcon card API/RPC contract boundary."""

import json
from pathlib import Path

from falcon_intel.falcon_api_contract import build_falcon_intelligence_card_response


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_ui_cards"
    / "firm-intelligence-card-v1.json"
)


def main() -> None:
    response = build_falcon_intelligence_card_response(
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
        }
    )
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert response["status"] == "ok"
    assert response["card"]["schema_version"] == "1"
    assert response["card"] == snapshot

    missing_response = build_falcon_intelligence_card_response(
        {
            "order_id": "falcon-order-synthetic-001",
            "tenant_id": "tenant-synthetic-001",
            "address": "1000 Example Industrial Way",
        }
    )
    assert missing_response["status"] == "missing_required_input"

    serialized = json.dumps(response).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized

    print("falcon API contract smoke validation passed")


if __name__ == "__main__":
    main()
