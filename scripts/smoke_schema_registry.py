"""Smoke validation for the Falcon Intelligence schema version registry."""

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
    SchemaName,
    get_schema_registry_entry,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PASSPORT_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_data_passports"
    / "data-passports.json"
)


def main() -> None:
    card_entry = get_schema_registry_entry(SchemaName.FIRM_INTELLIGENCE_CARD)
    passport_entry = get_schema_registry_entry(SchemaName.PASSPORT_DETAIL_DRAWER)
    card_api_entry = get_schema_registry_entry(SchemaName.FALCON_CARD_API_RESPONSE)
    passport_api_entry = get_schema_registry_entry(SchemaName.FALCON_PASSPORT_DETAIL_API_RESPONSE)
    evidence_api_entry = get_schema_registry_entry(SchemaName.FALCON_EVIDENCE_OPEN_RESPONSE)
    assert card_entry.current_version == FIRM_INTELLIGENCE_CARD_SCHEMA_VERSION
    assert passport_entry.current_version == PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION
    assert card_entry.fixture_snapshot_path is not None
    assert passport_entry.fixture_snapshot_path is not None
    assert card_api_entry.fixture_snapshot_path is not None
    assert passport_api_entry.fixture_snapshot_path is not None
    assert evidence_api_entry.fixture_snapshot_path is not None

    card_response = build_falcon_intelligence_card_response(
        {
            "order_id": "falcon-order-synthetic-001",
            "tenant_id": "tenant-synthetic-001",
            "address": "1000 Example Industrial Way",
            "city": "Sampleton",
            "state": "ST",
            "property_type": "industrial",
            "building_size_sf": 50000,
            "client": "Synthetic Lender A",
        }
    )
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

    serialized = json.dumps(
        {
            "card": card_response,
            "passport": passport_response,
            "evidence": evidence_response,
        }
    ).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized

    print("schema registry smoke validation passed")


if __name__ == "__main__":
    main()
