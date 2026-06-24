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


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
API_ENVELOPE_FIXTURE_ROOT = FIXTURE_ROOT / "synthetic_api_envelopes"
PASSPORT_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_data_passports" / "data-passports.json"


def test_falcon_card_api_response_matches_v1_snapshot() -> None:
    current_response = _build_card_response()
    snapshot = _load_snapshot("falcon-card-api-response-v1.json")

    assert snapshot["schema_version"] == FALCON_CARD_API_RESPONSE_SCHEMA_VERSION
    assert current_response == snapshot


def test_falcon_passport_detail_api_response_matches_v1_snapshot() -> None:
    current_response = _normalize_dynamic_audit_timestamp(_build_passport_response())
    snapshot = _load_snapshot("falcon-passport-detail-api-response-v1.json")

    assert snapshot["schema_version"] == FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION
    assert snapshot["suggested_audit_event"]["timestamp"] == "synthetic-dynamic-timestamp"
    assert current_response == snapshot


def test_falcon_evidence_open_api_response_matches_v1_snapshot() -> None:
    current_response = _normalize_dynamic_audit_timestamp(_build_evidence_response())
    snapshot = _load_snapshot("falcon-evidence-open-api-response-v1.json")

    assert snapshot["schema_version"] == FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION
    assert snapshot["suggested_audit_event"]["timestamp"] == "synthetic-dynamic-timestamp"
    assert current_response == snapshot


def test_api_envelope_snapshots_are_synthetic_only() -> None:
    serialized = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in API_ENVELOPE_FIXTURE_ROOT.glob("*.json")
    )

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized


def _build_card_response() -> dict[str, Any]:
    return build_falcon_intelligence_card_response(
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


def _build_passport_response() -> dict[str, Any]:
    return build_falcon_passport_detail_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )


def _build_evidence_response() -> dict[str, Any]:
    return build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
            "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )


def _load_snapshot(filename: str) -> dict[str, Any]:
    return json.loads((API_ENVELOPE_FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _normalize_dynamic_audit_timestamp(response: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(response))
    normalized["suggested_audit_event"]["timestamp"] = "synthetic-dynamic-timestamp"
    return normalized
