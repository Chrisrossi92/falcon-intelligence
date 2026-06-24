import json
from pathlib import Path

from falcon_intel.data_passport_lookup import (
    load_synthetic_data_passports,
    lookup_data_passport_detail,
)
from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
PASSPORT_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_data_passports" / "data-passports.json"
INTELLIGENCE_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_verified_intelligence" / "verified-intelligence.json"


def test_lookup_returns_full_data_passport_detail() -> None:
    response = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id="synthetic-passport-assignment-industrial-alpha",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()

    assert response["status"] == "found"
    assert response["passport_id"] == "synthetic-passport-assignment-industrial-alpha"
    passport = response["passport"]
    assert passport["fact_id"] == "synthetic-fact-assignment-industrial-alpha-building-size"
    assert passport["verification_status"] == "verified"
    assert passport["reviewed_by"] == "synthetic-reviewer-001"
    assert passport["confidence_dimensions"]["source_quality"] == "verified_synthetic_source_metadata"
    assert passport["evidence_links"][0]["source_document_type"] == "source_report"
    assert passport["audit_event_ids"] == [
        "synthetic-audit-assignment-industrial-alpha-viewed",
        "synthetic-audit-assignment-industrial-alpha-verified",
    ]
    assert passport["searchable_status"] == "searchable"


def test_lookup_returns_safe_not_found_for_wrong_tenant_or_missing_passport() -> None:
    wrong_tenant = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-other",
        passport_id="synthetic-passport-assignment-industrial-alpha",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()
    missing = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id="synthetic-passport-missing",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()

    assert wrong_tenant["status"] == "not_found"
    assert "passport" not in wrong_tenant
    assert missing["status"] == "not_found"
    assert "passport" not in missing


def test_lookup_returns_safe_error_for_invalid_request() -> None:
    response = lookup_data_passport_detail(
        tenant_id="",
        passport_id="synthetic-passport-assignment-industrial-alpha",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()

    assert response["status"] == "error"
    assert "tenant_id is required" in response["error"]


def test_card_top_match_passport_id_resolves_to_detail() -> None:
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

    top_match = card["top_match_cards"][0]
    response = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id=top_match["passport_id"],
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()

    assert response["status"] == "found"
    assert response["passport"]["passport_id"] == top_match["passport_id"]
    assert response["passport"]["verification_status"] == top_match["verification_status"]
    assert len(response["passport"]["evidence_links"]) == top_match["evidence_link_count"]
    assert response["passport"]["searchable_status"] == top_match["searchable_status"]


def test_data_passport_fixture_is_synthetic_only() -> None:
    fixture = load_synthetic_data_passports(PASSPORT_FIXTURE_PATH)
    assert fixture["fixture_kind"] == "synthetic_data_passports"
    assert len(fixture["passports"]) == 3

    serialized = json.dumps(fixture).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized
