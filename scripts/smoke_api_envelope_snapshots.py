"""Smoke validation for versioned synthetic Falcon API envelope snapshots."""

import json
from pathlib import Path
from typing import Any

from falcon_intel.falcon_api_contract import build_falcon_intelligence_card_response
from falcon_intel.falcon_evidence_contract import build_falcon_evidence_open_response
from falcon_intel.falcon_passport_contract import build_falcon_passport_detail_response
from falcon_intel.schema_registry import (
    FALCON_CARD_API_RESPONSE_SCHEMA_VERSION,
    FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION,
    FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
API_ENVELOPE_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "synthetic_api_envelopes"
PASSPORT_FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "synthetic_data_passports" / "data-passports.json"


def main() -> None:
    card_snapshot = _load_snapshot("falcon-card-api-response-v1.json")
    passport_snapshot = _load_snapshot("falcon-passport-detail-api-response-v1.json")
    evidence_snapshot = _load_snapshot("falcon-evidence-open-api-response-v1.json")

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
            "borrower_contact": "Synthetic Borrower Contact",
        }
    )
    passport_response = _normalize_dynamic_audit_timestamp(
        build_falcon_passport_detail_response(
            {
                "tenant_id": "tenant-synthetic-001",
                "order_id": "falcon-order-synthetic-001",
                "user_id": "user-synthetic-001",
                "passport_id": "synthetic-passport-assignment-industrial-alpha",
            },
            synthetic_passport_path=PASSPORT_FIXTURE_PATH,
        )
    )
    evidence_response = _normalize_dynamic_audit_timestamp(
        build_falcon_evidence_open_response(
            {
                "tenant_id": "tenant-synthetic-001",
                "order_id": "falcon-order-synthetic-001",
                "user_id": "user-synthetic-001",
                "passport_id": "synthetic-passport-assignment-industrial-alpha",
                "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
            },
            synthetic_passport_path=PASSPORT_FIXTURE_PATH,
        )
    )

    assert card_snapshot["schema_version"] == FALCON_CARD_API_RESPONSE_SCHEMA_VERSION
    assert passport_snapshot["schema_version"] == FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION
    assert evidence_snapshot["schema_version"] == FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION
    assert card_response == card_snapshot
    assert passport_response == passport_snapshot
    assert evidence_response == evidence_snapshot

    serialized = json.dumps(
        {
            "card": card_snapshot,
            "passport": passport_snapshot,
            "evidence": evidence_snapshot,
        }
    ).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("falcon API envelope snapshot smoke validation passed")


def _load_snapshot(filename: str) -> dict[str, Any]:
    return json.loads((API_ENVELOPE_FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _normalize_dynamic_audit_timestamp(response: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(response))
    normalized["suggested_audit_event"]["timestamp"] = "synthetic-dynamic-timestamp"
    return normalized


if __name__ == "__main__":
    main()
