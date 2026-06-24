"""Smoke validation for the UI-facing synthetic intelligence card schema."""

import json
from pathlib import Path

from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_verified_intelligence"
    / "verified-intelligence.json"
)


def main() -> None:
    intelligence = load_synthetic_verified_intelligence(FIXTURE_PATH)
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

    assert card["schema_version"] == "1"
    assert card["headline"].startswith("Firm Intelligence Found")
    assert card["order_summary"]["property_type"] == "industrial"
    assert card["match_group_summaries"]
    assert card["top_match_cards"]
    assert card["confidence_provenance_summary"]["synthetic_fixture_only"] is True
    assert card["warnings"]
    assert card["recommended_actions"]

    serialized = json.dumps(card).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized

    print("synthetic intelligence card schema smoke validation passed")


if __name__ == "__main__":
    main()
