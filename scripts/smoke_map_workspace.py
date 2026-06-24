"""Smoke validation for the synthetic Falcon Intelligence Map Workspace contract."""

import json

from falcon_intel.map_workspace import (
    build_map_workspace_response,
    filter_map_records,
    load_synthetic_map_records,
)
from falcon_intel.schema_registry import MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION


def main() -> None:
    records = load_synthetic_map_records()
    assert {record.record_type for record in records} == {
        "active_order",
        "completed_assignment",
        "current_subject",
        "historical_comp",
        "lease_comp",
        "sale_comp",
    }

    filtered = filter_map_records(
        records,
        {
            "property_type": "industrial",
            "verification_status": "verified",
        },
    )
    assert len(filtered) == 4

    response = build_map_workspace_response(
        records,
        filters={"property_type": "industrial"},
        selected_record_id="synthetic-map-sale-comp-001",
    ).to_dict()
    assert response["schema_version"] == MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION
    assert len(response["table_rows"]) == len(response["map_pins"]) == 5
    assert response["selected_record"]["id"] == "synthetic-map-sale-comp-001"
    assert response["result_counts"]["total_records"] == 6
    assert response["result_counts"]["filtered_records"] == 5

    serialized = json.dumps(response).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized
    assert "google maps" not in serialized

    print("map workspace smoke validation passed")


if __name__ == "__main__":
    main()
