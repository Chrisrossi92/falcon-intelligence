"""Smoke validation for the synthetic passport detail drawer UI snapshot."""

import json
from pathlib import Path

from falcon_intel.data_passport_lookup import lookup_data_passport_detail
from falcon_intel.passport_detail_drawer import build_passport_detail_drawer


REPO_ROOT = Path(__file__).resolve().parents[1]
PASSPORT_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_data_passports"
    / "data-passports.json"
)
DRAWER_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_ui_passports"
    / "passport-detail-drawer-v1.json"
)


def main() -> None:
    response = lookup_data_passport_detail(
        tenant_id="tenant-synthetic-001",
        passport_id="synthetic-passport-assignment-industrial-alpha",
        fixture_path=PASSPORT_FIXTURE_PATH,
    ).to_dict()
    assert response["status"] == "found"

    drawer = build_passport_detail_drawer(response["passport"]).to_dict()
    snapshot = json.loads(DRAWER_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert drawer == snapshot
    assert drawer["schema_version"] == "1"
    assert drawer["evidence_links_summary"][0]["status"] == "placeholder"

    serialized = json.dumps(drawer).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("passport detail drawer snapshot smoke validation passed")


if __name__ == "__main__":
    main()
