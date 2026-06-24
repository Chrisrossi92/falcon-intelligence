"""Smoke validation for the versioned synthetic UI card snapshot."""

import json
from pathlib import Path

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
CARD_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_ui_cards"
    / "firm-intelligence-card-v1.json"
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
    current_card = build_firm_intelligence_card(matcher_output, intelligence).to_dict()
    snapshot_card = json.loads(CARD_SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert snapshot_card["schema_version"] == "1"
    assert current_card == snapshot_card

    serialized = json.dumps(snapshot_card).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized

    print("synthetic intelligence card snapshot smoke validation passed")


if __name__ == "__main__":
    main()
