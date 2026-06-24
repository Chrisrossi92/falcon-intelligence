"""Smoke validation for the local Falcon passport detail API/RPC contract boundary."""

import json
from pathlib import Path

from falcon_intel.falcon_passport_contract import build_falcon_passport_detail_response
from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
INTELLIGENCE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_verified_intelligence"
    / "verified-intelligence.json"
)
PASSPORT_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_data_passports"
    / "data-passports.json"
)


def main() -> None:
    intelligence = load_synthetic_verified_intelligence(INTELLIGENCE_FIXTURE_PATH)
    card = build_firm_intelligence_card(
        match_firm_intelligence(
            FakeOrder(
                address="1000 Example Industrial Way",
                city="Sampleton",
                state="ST",
                property_type="industrial",
                building_size_sf=50000,
                client="Synthetic Lender A",
            ),
            intelligence,
        ),
        intelligence,
    ).to_dict()
    passport_id = card["top_match_cards"][0]["passport_id"]
    response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": passport_id,
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response["status"] == "ok"
    assert response["passport"]["passport_id"] == passport_id
    assert response["suggested_audit_event"]["event_code"] == "opened_evidence"
    assert response["suggested_audit_event"]["metadata"]["detail_type"] == "data_passport"

    missing_response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    assert missing_response["status"] == "missing_required_input"

    not_found_response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-other",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": passport_id,
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    assert not_found_response["status"] == "not_found"

    serialized = json.dumps(response).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("falcon passport detail contract smoke validation passed")


if __name__ == "__main__":
    main()
