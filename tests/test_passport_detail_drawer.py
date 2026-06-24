import json
from pathlib import Path

from falcon_intel.data_passport_lookup import lookup_data_passport_detail
from falcon_intel.passport_detail_drawer import build_passport_detail_drawer


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
PASSPORT_FIXTURE_PATH = FIXTURE_ROOT / "synthetic_data_passports" / "data-passports.json"
DRAWER_SNAPSHOT_PATH = FIXTURE_ROOT / "synthetic_ui_passports" / "passport-detail-drawer-v1.json"


def test_passport_detail_drawer_matches_v1_snapshot() -> None:
    current_drawer = _build_snapshot_drawer()
    snapshot = json.loads(DRAWER_SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert snapshot["schema_version"] == "1"
    assert current_drawer == snapshot


def test_passport_detail_drawer_schema_contains_ui_sections() -> None:
    drawer = _build_snapshot_drawer()

    assert drawer["passport_identity"] == {
        "assignment_id": "synthetic-assignment-industrial-alpha",
        "fact_id": "synthetic-fact-assignment-industrial-alpha-building-size",
        "passport_id": "synthetic-passport-assignment-industrial-alpha",
        "tenant_id": "tenant-synthetic-001",
    }
    assert drawer["fact_summary"]["fact_type"] == "assignment_summary"
    assert drawer["verification_review_summary"]["verification_status"] == "verified"
    assert set(drawer["confidence_dimensions"]) == {
        "extraction_confidence",
        "source_quality",
        "source_agreement",
        "freshness",
        "reviewer_approval",
        "historical_consistency",
    }
    assert drawer["evidence_links_summary"] == [
        {
            "access_level": "internal_only",
            "display_label": "Synthetic industrial assignment source metadata",
            "evidence_id": "synthetic-evidence-assignment-industrial-alpha",
            "has_future_anchor": False,
            "source_document_type": "source_report",
            "status": "placeholder",
        }
    ]
    assert drawer["audit_event_ids"] == [
        "synthetic-audit-assignment-industrial-alpha-viewed",
        "synthetic-audit-assignment-industrial-alpha-verified",
    ]
    assert drawer["searchable_status"] == "searchable"
    assert {warning["code"] for warning in drawer["warnings"]} == {
        "evidence_placeholder_only",
        "synthetic_preview_only",
    }


def test_passport_detail_drawer_snapshot_is_synthetic_only() -> None:
    serialized = DRAWER_SNAPSHOT_PATH.read_text(encoding="utf-8").lower()

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized


def _build_snapshot_drawer() -> dict[str, object]:
    response = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id="synthetic-passport-assignment-industrial-alpha",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()
    assert response["status"] == "found"
    return build_passport_detail_drawer(response["passport"]).to_dict()
