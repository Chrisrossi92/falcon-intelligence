import json
from pathlib import Path
from typing import Any

from falcon_intel.falcon_api_contract import build_falcon_intelligence_card_response
from falcon_intel.falcon_evidence_contract import build_falcon_evidence_open_response
from falcon_intel.falcon_passport_contract import build_falcon_passport_detail_response


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
PASSPORT_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_data_passports" / "data-passports.json"


def test_card_boundary_respects_internal_and_client_roles() -> None:
    for role in ("owner", "admin", "appraiser", "reviewer", "trainee"):
        response = build_falcon_intelligence_card_response(
            {
                **_order_payload(),
                "actor_role": role,
            }
        )

        assert response["status"] == "ok"
        assert response["card"]["schema_version"] == "1"

    denied_response = build_falcon_intelligence_card_response(
        {
            **_order_payload(),
            "actor_role": "client",
        }
    )

    assert denied_response == {
        "status": "permission_denied",
        "order_id": "falcon-order-synthetic-001",
        "tenant_id": "tenant-synthetic-001",
        "schema_version": "1",
        "reason_code": "denied_client_role",
        "reason_label": "Client role cannot access internal Falcon Intelligence.",
    }


def test_passport_boundary_respects_detail_role_policy() -> None:
    for role in ("owner", "admin", "appraiser", "reviewer"):
        response = build_falcon_passport_detail_response(
            {
                **_passport_request(),
                "actor_role": role,
            },
            synthetic_passport_path=PASSPORT_FIXTURE_PATH,
        )

        assert response["status"] == "ok"
        assert response["passport"]["passport_id"] == "synthetic-passport-assignment-industrial-alpha"

    trainee_response = build_falcon_passport_detail_response(
        {
            **_passport_request(),
            "actor_role": "trainee",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    client_response = build_falcon_passport_detail_response(
        {
            **_passport_request(),
            "actor_role": "client",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert trainee_response["status"] == "permission_denied"
    assert trainee_response["reason_code"] == "denied_trainee_restricted"
    assert client_response["status"] == "permission_denied"
    assert client_response["reason_code"] == "denied_client_role"


def test_evidence_boundary_respects_internal_and_disabled_access_levels(tmp_path: Path) -> None:
    for role in ("owner", "admin", "appraiser", "reviewer"):
        response = build_falcon_evidence_open_response(
            {
                **_evidence_request(),
                "actor_role": role,
            },
            synthetic_passport_path=PASSPORT_FIXTURE_PATH,
        )

        assert response["status"] == "ok"
        assert response["evidence_summary"]["access_level"] == "internal_only"

    trainee_response = build_falcon_evidence_open_response(
        {
            **_evidence_request(),
            "actor_role": "trainee",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    client_response = build_falcon_evidence_open_response(
        {
            **_evidence_request(),
            "actor_role": "client",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    disabled_response = build_falcon_evidence_open_response(
        {
            **_evidence_request(),
            "actor_role": "owner",
        },
        synthetic_passport_path=_passport_fixture_with_access_level(tmp_path, "disabled"),
    )

    assert trainee_response["status"] == "permission_denied"
    assert trainee_response["reason_code"] == "denied_trainee_restricted"
    assert client_response["status"] == "permission_denied"
    assert client_response["reason_code"] == "denied_client_role"
    assert disabled_response["status"] == "permission_denied"
    assert disabled_response["reason_code"] == "denied_disabled_evidence"


def test_evidence_boundary_respects_owner_admin_only_access_level(tmp_path: Path) -> None:
    fixture_path = _passport_fixture_with_access_level(tmp_path, "owner_admin_only")

    for role in ("owner", "admin"):
        response = build_falcon_evidence_open_response(
            {
                **_evidence_request(),
                "actor_role": role,
            },
            synthetic_passport_path=fixture_path,
        )

        assert response["status"] == "ok"
        assert response["evidence_summary"]["access_level"] == "owner_admin_only"

    for role in ("appraiser", "reviewer", "trainee", "client"):
        response = build_falcon_evidence_open_response(
            {
                **_evidence_request(),
                "actor_role": role,
            },
            synthetic_passport_path=fixture_path,
        )

        assert response["status"] == "permission_denied"

    assert build_falcon_evidence_open_response(
        {
            **_evidence_request(),
            "actor_role": "appraiser",
        },
        synthetic_passport_path=fixture_path,
    )["reason_code"] == "denied_admin_required"


def test_evidence_boundary_documents_appraiser_reviewer_only_policy(tmp_path: Path) -> None:
    fixture_path = _passport_fixture_with_access_level(tmp_path, "appraiser_reviewer_only")

    for role in ("owner", "admin", "appraiser", "reviewer"):
        response = build_falcon_evidence_open_response(
            {
                **_evidence_request(),
                "actor_role": role,
            },
            synthetic_passport_path=fixture_path,
        )

        assert response["status"] == "ok"
        assert response["evidence_summary"]["access_level"] == "appraiser_reviewer_only"

    for role in ("trainee", "client"):
        response = build_falcon_evidence_open_response(
            {
                **_evidence_request(),
                "actor_role": role,
            },
            synthetic_passport_path=fixture_path,
        )

        assert response["status"] == "permission_denied"


def test_permission_denied_shape_is_stable() -> None:
    response = build_falcon_evidence_open_response(
        {
            **_evidence_request(),
            "actor_role": "client",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response == {
        "status": "permission_denied",
        "tenant_id": "tenant-synthetic-001",
        "order_id": "falcon-order-synthetic-001",
        "user_id": "user-synthetic-001",
        "passport_id": "synthetic-passport-assignment-industrial-alpha",
        "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
        "schema_version": "1",
        "reason_code": "denied_client_role",
        "reason_label": "Client role cannot access internal Falcon Intelligence.",
    }


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
    target = payload["passports"][0]["evidence_links"][0]
    assert target["evidence_id"] == "synthetic-evidence-assignment-industrial-alpha"
    target["access_level"] = access_level
    fixture_path = tmp_path / f"synthetic-passports-{access_level}.json"
    fixture_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fixture_path
