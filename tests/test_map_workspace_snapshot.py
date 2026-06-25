import json
from pathlib import Path

from falcon_intel.map_workspace import build_map_workspace_response
from falcon_intel.schema_registry import MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION


SNAPSHOT_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "synthetic_ui_map_workspace"
    / "map-workspace-response-v1.json"
)


def test_map_workspace_response_matches_v1_snapshot() -> None:
    current_response = build_map_workspace_response(
        selected_record_id="synthetic-map-sale-comp-001",
    ).to_dict()
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert snapshot["schema_version"] == MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION
    assert current_response == snapshot


def test_map_workspace_snapshot_is_synthetic_only() -> None:
    serialized = SNAPSHOT_PATH.read_text(encoding="utf-8").lower()

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized
    assert "google maps" not in serialized
