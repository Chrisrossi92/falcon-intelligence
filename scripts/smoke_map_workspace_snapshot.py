"""Smoke validation for the versioned synthetic map workspace UI snapshot."""

import json
from pathlib import Path

from falcon_intel.map_workspace import build_map_workspace_response
from falcon_intel.schema_registry import MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_ui_map_workspace"
    / "map-workspace-response-v1.json"
)


def main() -> None:
    current_response = build_map_workspace_response(
        selected_record_id="synthetic-map-sale-comp-001",
    ).to_dict()
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert snapshot["schema_version"] == MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION
    assert current_response == snapshot
    assert len(snapshot["table_rows"]) == len(snapshot["map_pins"]) == 8
    assert snapshot["selected_record"]["id"] == "synthetic-map-sale-comp-001"

    serialized = json.dumps(snapshot).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized
    assert "google maps" not in serialized

    print("map workspace snapshot smoke validation passed")


if __name__ == "__main__":
    main()
