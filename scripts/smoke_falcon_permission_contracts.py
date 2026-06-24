"""Smoke validation for permission-aware Falcon contract boundaries."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from falcon_intel.falcon_api_contract import build_falcon_intelligence_card_response
from falcon_intel.falcon_evidence_contract import build_falcon_evidence_open_response
from falcon_intel.falcon_passport_contract import build_falcon_passport_detail_response


REPO_ROOT = Path(__file__).resolve().parents[1]
PASSPORT_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_data_passports"
    / "data-passports.json"
)


def main() -> None:
    card_response = build_falcon_intelligence_card_response(
        {
            **_order_payload(),
            "actor_role": "appraiser",
        }
    )
    denied_card_response = build_falcon_intelligence_card_response(
        {
            **_order_payload(),
            "actor_role": "client",
        }
    )
    passport_response = build_falcon_passport_detail_response(
        {
            **_passport_request(),
            "actor_role": "reviewer",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    denied_passport_response = build_falcon_passport_detail_response(
        {
            **_passport_request(),
            "actor_role": "trainee",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert card_response["status"] == "ok"
    assert denied_card_response["status"] == "permission_denied"
    assert denied_card_response["reason_code"] == "denied_client_role"
    assert passport_response["status"] == "ok"
    assert denied_passport_response["status"] == "permission_denied"
    assert denied_passport_response["reason_code"] == "denied_trainee_restricted"

    with TemporaryDirectory() as tmp_dir:
        owner_admin_fixture = _passport_fixture_with_access_level(Path(tmp_dir), "owner_admin_only")
        denied_evidence_response = build_falcon_evidence_open_response(
            {
                **_evidence_request(),
                "actor_role": "appraiser",
            },
            synthetic_passport_path=owner_admin_fixture,
        )
        allowed_evidence_response = build_falcon_evidence_open_response(
            {
                **_evidence_request(),
                "actor_role": "owner",
            },
            synthetic_passport_path=owner_admin_fixture,
        )

    assert denied_evidence_response["status"] == "permission_denied"
    assert denied_evidence_response["reason_code"] == "denied_admin_required"
    assert allowed_evidence_response["status"] == "ok"
    assert allowed_evidence_response["evidence_summary"]["access_level"] == "owner_admin_only"

    serialized = json.dumps(
        {
            "card": card_response,
            "passport": passport_response,
            "evidence": allowed_evidence_response,
        }
    ).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("falcon permission contract smoke validation passed")


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
        "borrower_contact": "Synthetic Borrower Contact",
    }


def _passport_request() -> dict[str, object]:
    return {
        "tenant_id": "tenant-synthetic-001",
        "order_id": "falcon-order-synthetic-001",
        "user_id": "user-synthetic-001",
        "passport_id": "synthetic-passport-assignment-industrial-alpha",
    }


def _evidence_request() -> dict[str, object]:
    return {
        **_passport_request(),
        "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
    }


def _passport_fixture_with_access_level(tmp_path: Path, access_level: str) -> Path:
    payload: dict[str, Any] = json.loads(PASSPORT_FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["passports"][0]["evidence_links"][0]["access_level"] = access_level
    fixture_path = tmp_path / f"synthetic-passports-{access_level}.json"
    fixture_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fixture_path


if __name__ == "__main__":
    main()
