import json
from pathlib import Path

from falcon_intel.falcon_api_contract import build_falcon_intelligence_card_response
from falcon_intel.falcon_evidence_contract import build_falcon_evidence_open_response
from falcon_intel.falcon_passport_contract import build_falcon_passport_detail_response
from falcon_intel.schema_registry import (
    FALCON_CARD_API_RESPONSE_SCHEMA_VERSION,
    FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION,
    FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION,
    FIRM_INTELLIGENCE_CARD_SCHEMA_VERSION,
    PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION,
    SCHEMA_REGISTRY,
    SchemaName,
    get_schema_registry_entry,
    schema_registry_to_dict,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CARD_SNAPSHOT_PATH = REPO_ROOT / "tests" / "fixtures" / "synthetic_ui_cards" / "firm-intelligence-card-v1.json"
PASSPORT_DRAWER_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_ui_passports"
    / "passport-detail-drawer-v1.json"
)
API_ENVELOPE_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "synthetic_api_envelopes"
PASSPORT_FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "synthetic_data_passports" / "data-passports.json"


def test_schema_registry_has_required_contract_entries() -> None:
    assert set(SCHEMA_REGISTRY) == {
        SchemaName.FIRM_INTELLIGENCE_CARD,
        SchemaName.PASSPORT_DETAIL_DRAWER,
        SchemaName.FALCON_EVIDENCE_OPEN_RESPONSE,
        SchemaName.FALCON_CARD_API_RESPONSE,
        SchemaName.FALCON_PASSPORT_DETAIL_API_RESPONSE,
    }

    for entry in SCHEMA_REGISTRY.values():
        assert entry.schema_name
        assert entry.current_version == "1"
        assert entry.breaking_change_rules
        assert entry.backward_compatibility_notes
        assert entry.intended_consumer


def test_schema_registry_fixture_paths_match_snapshots() -> None:
    card_entry = get_schema_registry_entry(SchemaName.FIRM_INTELLIGENCE_CARD)
    passport_entry = get_schema_registry_entry(SchemaName.PASSPORT_DETAIL_DRAWER)
    card_api_entry = get_schema_registry_entry(SchemaName.FALCON_CARD_API_RESPONSE)
    passport_api_entry = get_schema_registry_entry(SchemaName.FALCON_PASSPORT_DETAIL_API_RESPONSE)
    evidence_api_entry = get_schema_registry_entry(SchemaName.FALCON_EVIDENCE_OPEN_RESPONSE)

    assert card_entry.fixture_snapshot_path == "tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json"
    assert passport_entry.fixture_snapshot_path == "tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json"
    assert card_api_entry.fixture_snapshot_path == (
        "tests/fixtures/synthetic_api_envelopes/falcon-card-api-response-v1.json"
    )
    assert passport_api_entry.fixture_snapshot_path == (
        "tests/fixtures/synthetic_api_envelopes/falcon-passport-detail-api-response-v1.json"
    )
    assert evidence_api_entry.fixture_snapshot_path == (
        "tests/fixtures/synthetic_api_envelopes/falcon-evidence-open-api-response-v1.json"
    )
    assert json.loads(CARD_SNAPSHOT_PATH.read_text(encoding="utf-8"))["schema_version"] == (
        FIRM_INTELLIGENCE_CARD_SCHEMA_VERSION
    )
    assert json.loads(PASSPORT_DRAWER_SNAPSHOT_PATH.read_text(encoding="utf-8"))["schema_version"] == (
        PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION
    )
    assert _api_snapshot_version("falcon-card-api-response-v1.json") == (
        FALCON_CARD_API_RESPONSE_SCHEMA_VERSION
    )
    assert _api_snapshot_version("falcon-passport-detail-api-response-v1.json") == (
        FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION
    )
    assert _api_snapshot_version("falcon-evidence-open-api-response-v1.json") == (
        FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION
    )


def test_schema_registry_serialization_is_synthetic_only() -> None:
    serialized = json.dumps(schema_registry_to_dict()).lower()

    assert "onedrive" not in serialized
    assert "source_file_path" not in serialized
    assert "report_text" not in serialized
    assert "extraction" not in serialized


def test_contract_responses_source_schema_versions_from_registry() -> None:
    card_response = build_falcon_intelligence_card_response(_order_payload())
    passport_response = build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    evidence_response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
            "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert card_response["schema_version"] == FALCON_CARD_API_RESPONSE_SCHEMA_VERSION
    assert card_response["card"]["schema_version"] == FIRM_INTELLIGENCE_CARD_SCHEMA_VERSION
    assert passport_response["schema_version"] == FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION
    assert evidence_response["schema_version"] == FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION


def _order_payload() -> dict[str, object]:
    return {
        "order_id": "falcon-order-synthetic-001",
        "tenant_id": "tenant-synthetic-001",
        "address": "1000 Example Industrial Way",
        "city": "Sampleton",
        "state": "ST",
        "property_type": "industrial",
        "building_size_sf": 50000,
        "client": "Synthetic Lender A",
    }


def _api_snapshot_version(filename: str) -> str:
    return json.loads((API_ENVELOPE_FIXTURE_ROOT / filename).read_text(encoding="utf-8"))["schema_version"]
