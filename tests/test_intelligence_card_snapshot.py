import json
from pathlib import Path

from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
INTELLIGENCE_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_verified_intelligence" / "verified-intelligence.json"
CARD_SNAPSHOT_PATH = FIXTURE_ROOT / "synthetic_ui_cards" / "firm-intelligence-card-v1.json"


def test_ui_card_serializer_matches_v1_snapshot() -> None:
    current_card = _build_snapshot_card()
    snapshot_card = json.loads(CARD_SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert snapshot_card["schema_version"] == "1"
    assert current_card == snapshot_card


def test_ui_card_snapshot_is_synthetic_only() -> None:
    snapshot_text = CARD_SNAPSHOT_PATH.read_text(encoding="utf-8").lower()

    assert "report_text" not in snapshot_text
    assert "source_file_path" not in snapshot_text
    assert "onedrive" not in snapshot_text


def _build_snapshot_card() -> dict[str, object]:
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
    return build_firm_intelligence_card(matcher_output, intelligence).to_dict()
