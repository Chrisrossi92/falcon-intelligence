import json
from pathlib import Path

from falcon_intel.falcon_passport_contract import build_falcon_passport_detail_response
from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)
from falcon_intel.schema_registry import FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
INTELLIGENCE_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_verified_intelligence" / "verified-intelligence.json"
PASSPORT_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_data_passports" / "data-passports.json"


def test_card_top_match_passport_id_resolves_through_falcon_boundary() -> None:
    card = _build_card()
    top_match = card["top_match_cards"][0]

    response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": top_match["passport_id"],
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response["status"] == "ok"
    assert response["schema_version"] == FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION
    assert response["tenant_id"] == "tenant-synthetic-001"
    assert response["order_id"] == "falcon-order-synthetic-001"
    assert response["user_id"] == "user-synthetic-001"
    assert response["passport_id"] == top_match["passport_id"]
    assert response["passport"]["passport_id"] == top_match["passport_id"]
    assert response["passport"]["verification_status"] == top_match["verification_status"]
    assert len(response["passport"]["evidence_links"]) == top_match["evidence_link_count"]
    assert response["suggested_audit_event"]["event_code"] == "opened_evidence"
    assert response["suggested_audit_event"]["match_id"] == top_match["passport_id"]
    assert response["suggested_audit_event"]["metadata"] == {
        "detail_type": "data_passport",
        "passport_id": top_match["passport_id"],
        "fact_id": "synthetic-fact-assignment-industrial-alpha-building-size",
        "evidence_link_count": 1,
        "searchable_status": "searchable",
    }


def test_falcon_passport_boundary_validates_missing_required_input() -> None:
    response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "passport_id": "",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response == {
        "status": "missing_required_input",
        "tenant_id": "tenant-synthetic-001",
        "order_id": "falcon-order-synthetic-001",
        "user_id": None,
        "passport_id": None,
        "schema_version": FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION,
        "error": {
            "code": "missing_required_input",
            "message": "Falcon passport detail payload is missing required fields.",
            "missing_fields": ["user_id", "passport_id"],
        },
    }


def test_falcon_passport_boundary_enforces_tenant_scoping_as_not_found() -> None:
    response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-other",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response["status"] == "not_found"
    assert "passport" not in response
    assert "suggested_audit_event" not in response


def test_falcon_passport_boundary_output_is_synthetic_only() -> None:
    response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-sale-industrial-1",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    serialized = json.dumps(response).lower()

    assert response["status"] == "ok"
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized


def _build_card() -> dict[str, object]:
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
