"""Smoke validation for synthetic data passport detail lookup."""

import json
from pathlib import Path

from falcon_intel.data_passport_lookup import lookup_data_passport_detail
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
    matcher_output = match_firm_intelligence(
        FakeOrder(
            address="1000 Example Industrial Way",
            city="Sampleton",
            state="ST",
            property_type="industrial",
            building_size_sf=50000,
            client="Synthetic Lender A",
        ),
        intelligence,
    )
    card = build_firm_intelligence_card(matcher_output, intelligence).to_dict()
    passport_id = card["top_match_cards"][0]["passport_id"]

    response = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id=passport_id,
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()

    assert response["status"] == "found"
    assert response["passport"]["passport_id"] == passport_id
    assert response["passport"]["verification_status"] == "verified"
    assert response["passport"]["evidence_links"]
    assert response["passport"]["audit_event_ids"]

    missing = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id="synthetic-passport-missing",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()
    assert missing["status"] == "not_found"
    assert "passport" not in missing

    serialized = json.dumps(response).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("data passport lookup smoke validation passed")


if __name__ == "__main__":
    main()
