import json
from pathlib import Path

from falcon_intel.falcon_evidence_contract import build_falcon_evidence_open_response
from falcon_intel.passport_detail_drawer import build_passport_detail_drawer
from falcon_intel.data_passport_lookup import lookup_data_passport_detail
from falcon_intel.schema_registry import FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
PASSPORT_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_data_passports" / "data-passports.json"


def test_evidence_link_from_drawer_resolves_through_falcon_boundary() -> None:
    drawer = _build_drawer()
    evidence = drawer["evidence_links_summary"][0]

    response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": drawer["passport_identity"]["passport_id"],
            "evidence_id": evidence["evidence_id"],
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response["status"] == "ok"
    assert response["schema_version"] == FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION
    assert response["evidence_summary"] == {
        "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
        "source_document_id": "synthetic-source-report-industrial-alpha",
        "source_document_type": "source_report",
        "display_label": "Synthetic industrial assignment source metadata",
        "access_level": "internal_only",
        "status": "placeholder",
        "has_future_anchor": False,
    }
    assert response["suggested_audit_event"]["event_code"] == "opened_evidence"
    assert response["suggested_audit_event"]["match_id"] == "synthetic-passport-assignment-industrial-alpha"
    assert response["suggested_audit_event"]["metadata"] == {
        "detail_type": "evidence_link",
        "passport_id": "synthetic-passport-assignment-industrial-alpha",
        "fact_id": "synthetic-fact-assignment-industrial-alpha-building-size",
        "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
        "source_document_type": "source_report",
        "access_level": "internal_only",
        "status": "placeholder",
    }


def test_evidence_open_contract_validates_missing_required_input() -> None:
    response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response == {
        "status": "missing_required_input",
        "tenant_id": "tenant-synthetic-001",
        "order_id": "falcon-order-synthetic-001",
        "user_id": None,
        "passport_id": "synthetic-passport-assignment-industrial-alpha",
        "evidence_id": None,
        "schema_version": FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION,
        "error": {
            "code": "missing_required_input",
            "message": "Falcon evidence-open payload is missing required fields.",
            "missing_fields": ["user_id", "evidence_id"],
        },
    }


def test_evidence_open_contract_enforces_tenant_scope_as_not_found() -> None:
    response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-other",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
            "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response["status"] == "not_found"
    assert "evidence_summary" not in response
    assert "suggested_audit_event" not in response


def test_evidence_open_contract_rejects_evidence_not_on_passport() -> None:
    response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
            "evidence_id": "synthetic-evidence-sale-industrial-1",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )

    assert response["status"] == "evidence_not_found"
    assert "evidence_summary" not in response
    assert "suggested_audit_event" not in response


def test_evidence_open_contract_output_is_synthetic_only() -> None:
    response = build_falcon_evidence_open_response(
        {
            "tenant_id": "tenant-synthetic-001",
            "order_id": "falcon-order-synthetic-001",
            "user_id": "user-synthetic-001",
            "passport_id": "synthetic-passport-assignment-industrial-alpha",
            "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
        },
        synthetic_passport_path=PASSPORT_FIXTURE_PATH,
    )
    serialized = json.dumps(response).lower()

    assert response["status"] == "ok"
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized


def _build_drawer() -> dict[str, object]:
    lookup = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id="synthetic-passport-assignment-industrial-alpha",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()
    assert lookup["status"] == "found"
    return build_passport_detail_drawer(lookup["passport"]).to_dict()
