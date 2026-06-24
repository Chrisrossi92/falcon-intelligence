import json
from pathlib import Path

import pytest

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


def test_matches_fake_order_against_synthetic_verified_intelligence() -> None:
    intelligence = load_synthetic_verified_intelligence(FIXTURE_PATH)
    order = FakeOrder(
        address="1000 Example Industrial Way",
        city="Sampleton",
        state="ST",
        property_type="industrial",
        building_size_sf=50000,
        client="Synthetic Lender A",
        borrower_contact="Synthetic Borrower Contact",
    )

    result = match_firm_intelligence(order, intelligence).to_dict()
    groups = result["match_groups"]

    assert groups["same_subject_property"][0]["source_id"] == "synthetic-assignment-industrial-alpha"
    assert groups["same_subject_property"][0]["score"] == 100
    assert "Exact synthetic address" in groups["same_subject_property"][0]["explanation"]

    assert {item["source_id"] for item in groups["nearby_prior_assignments"]} == {
        "synthetic-assignment-industrial-nearby",
        "synthetic-assignment-retail-bravo",
    }
    assert {item["source_id"] for item in groups["same_property_type"]} >= {
        "synthetic-assignment-industrial-alpha",
        "synthetic-assignment-industrial-nearby",
    }
    assert {item["source_id"] for item in groups["similar_building_size"]} >= {
        "synthetic-assignment-industrial-alpha",
        "synthetic-assignment-retail-bravo",
        "synthetic-assignment-office-charlie",
    }
    assert {item["source_id"] for item in groups["same_client"]} == {
        "synthetic-assignment-industrial-alpha",
        "synthetic-assignment-retail-bravo",
    }
    assert groups["verified_sale_comps"][0]["source_id"] == "synthetic-sale-industrial-1"
    assert groups["verified_lease_comps"][0]["source_id"] == "synthetic-lease-industrial-1"
    assert groups["relevant_market_indicators"][0]["source_id"] == "synthetic-market-industrial-sampleton-vacancy"
    assert all(
        assignment["client"].startswith("Synthetic ")
        for assignment in intelligence["assignments"]
    )

    serialized = json.dumps(result).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized


def test_accepts_order_dict_and_keeps_all_match_groups() -> None:
    intelligence = load_synthetic_verified_intelligence(FIXTURE_PATH)
    result = match_firm_intelligence(
        {
            "address": "9999 New Example Avenue",
            "city": "Sampleton",
            "state": "ST",
            "property_type": "retail",
            "building_size_sf": 47000,
            "client": "Synthetic Lender A",
        },
        intelligence,
    ).to_dict()

    assert list(result["match_groups"]) == [
        "same_subject_property",
        "nearby_prior_assignments",
        "same_property_type",
        "similar_building_size",
        "same_client",
        "verified_sale_comps",
        "verified_lease_comps",
        "relevant_market_indicators",
    ]
    assert result["match_groups"]["same_subject_property"] == []
    assert result["match_groups"]["same_property_type"][0]["source_id"] == "synthetic-assignment-retail-bravo"
    assert result["match_groups"]["verified_sale_comps"][0]["source_id"] == "synthetic-sale-retail-1"
    assert result["match_groups"]["relevant_market_indicators"][0]["source_id"] == "synthetic-market-retail-sampleton-rent"


def test_rejects_non_synthetic_or_unverified_intelligence() -> None:
    payload = load_synthetic_verified_intelligence(FIXTURE_PATH)
    payload["assignments"][0]["verification_status"] = "suggested"

    with pytest.raises(ValueError, match="non-verified"):
        match_firm_intelligence(
            FakeOrder(
                address="1000 Example Industrial Way",
                city="Sampleton",
                state="ST",
                property_type="industrial",
                building_size_sf=50000,
                client="Synthetic Lender A",
            ),
            payload,
        )


def test_rejects_prohibited_source_content_fields() -> None:
    payload = load_synthetic_verified_intelligence(FIXTURE_PATH)
    payload["sale_comps"][0]["report_text"] = "prohibited"

    with pytest.raises(ValueError, match="prohibited"):
        match_firm_intelligence(
            FakeOrder(
                address="1000 Example Industrial Way",
                city="Sampleton",
                state="ST",
                property_type="industrial",
                building_size_sf=50000,
                client="Synthetic Lender A",
            ),
            payload,
        )
