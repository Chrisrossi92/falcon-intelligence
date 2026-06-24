"""Smoke validation for the local Falcon evidence-open API/RPC contract boundary."""

import json
from pathlib import Path

from falcon_intel.data_passport_lookup import lookup_data_passport_detail
from falcon_intel.falcon_evidence_contract import build_falcon_evidence_open_response
from falcon_intel.passport_detail_drawer import build_passport_detail_drawer
from falcon_intel.schema_registry import FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION


REPO_ROOT = Path(__file__).resolve().parents[1]
PASSPORT_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_data_passports"
    / "data-passports.json"
)


def main() -> None:
    lookup = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id="synthetic-passport-assignment-industrial-alpha",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()
    assert lookup["status"] == "found"
    drawer = build_passport_detail_drawer(lookup["passport"]).to_dict()
    evidence_id = drawer["evidence_links_summary"][0]["evidence_id"]

    response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": drawer["passport_identity"]["passport_id"],
            "evidence_id": evidence_id,
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    assert response["status"] == "ok"
    assert response["schema_version"] == FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION
    assert response["evidence_summary"]["evidence_id"] == evidence_id
    assert response["suggested_audit_event"]["event_code"] == "opened_evidence"
    assert response["suggested_audit_event"]["metadata"]["detail_type"] == "evidence_link"

    missing_response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": drawer["passport_identity"]["passport_id"],
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    assert missing_response["status"] == "missing_required_input"

    wrong_evidence_response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": drawer["passport_identity"]["passport_id"],
            "evidence_id": "synthetic-evidence-missing",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    assert wrong_evidence_response["status"] == "evidence_not_found"

    serialized = json.dumps(response).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("falcon evidence-open contract smoke validation passed")


if __name__ == "__main__":
    main()
