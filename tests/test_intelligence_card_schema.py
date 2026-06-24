import json
from pathlib import Path

from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "synthetic_verified_intelligence"
    / "verified-intelligence.json"
)


def test_builds_ui_facing_intelligence_card_schema() -> None:
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
    assert card["headline"] == "Firm Intelligence Found: 17 synthetic matches across 8 groups."
    assert card["order_summary"] == {
        "address": "1000 Example Industrial Way",
        "building_size_sf": 50000,
        "city": "Sampleton",
        "client": "Synthetic Lender A",
        "property_type": "industrial",
        "state": "ST",
    }
    assert card["match_group_summaries"][0] == {
        "count": 1,
        "group": "same_subject_property",
        "label": "Same Subject Property",
        "top_score": 100,
    }
    assert card["confidence_provenance_summary"] == {
        "highest_score": 100,
        "source_fixture_kind": "synthetic_verified_intelligence",
        "source_fixture_version": "1",
        "synthetic_fixture_only": True,
        "total_matches": 17,
        "verified_match_count": 16,
    }

    first_match = card["top_match_cards"][0]
    assert first_match["source_id"] == "synthetic-assignment-industrial-alpha"
    assert first_match["confidence_label"] == "high"
    assert first_match["provenance"]["verification_status"] == "verified"
    assert first_match["stale_data_flags"] == []
    assert {warning["code"] for warning in card["warnings"]} == {
        "appraiser_review_required",
        "synthetic_preview_only",
    }
    assert {action["code"] for action in card["recommended_actions"]} == {
        "confirm_relevance",
        "evaluate_comparable_reuse",
        "review_top_matches",
    }

    serialized = json.dumps(card).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized


def test_schema_includes_stale_warning_when_fixture_marks_record_stale() -> None:
    intelligence = load_synthetic_verified_intelligence(FIXTURE_PATH)
    intelligence["sale_comps"][0]["stale_after"] = "expired"
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

    sale_cards = [
        match_card
        for match_card in card["top_match_cards"]
        if match_card["source_id"] == "synthetic-sale-industrial-1"
    ]
    assert sale_cards[0]["stale_data_flags"] == ["stale"]
    assert "stale_data_present" in {warning["code"] for warning in card["warnings"]}
