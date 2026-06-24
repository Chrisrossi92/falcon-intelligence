import json
from pathlib import Path

from falcon_intel.map_workspace import (
    MapWorkspaceFilters,
    build_map_workspace_response,
    filter_map_records,
    load_synthetic_map_records,
)
from falcon_intel.schema_registry import MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "synthetic_map_workspace"
    / "map-records.json"
)


def test_synthetic_map_fixture_covers_required_record_types() -> None:
    records = load_synthetic_map_records(FIXTURE_PATH)

    assert {record.record_type for record in records} == {
        "active_order",
        "completed_assignment",
        "sale_comp",
        "lease_comp",
        "historical_comp",
        "current_subject",
    }
    assert len(records) == 6
    assert all(record.latitude and record.longitude for record in records)


def test_filter_map_records_supports_required_filters() -> None:
    records = load_synthetic_map_records(FIXTURE_PATH)

    industrial = filter_map_records(records, MapWorkspaceFilters(property_type="industrial"))
    stale = filter_map_records(records, {"stale_flag": True})
    sampleton_verified = filter_map_records(
        records,
        {
            "city": "Sampleton",
            "state": "ST",
            "verification_status": "verified",
        },
    )
    sale_comps = filter_map_records(
        records,
        {
            "record_type": "sale_comp",
            "status": "verified_comp",
        },
    )

    assert len(industrial) == 5
    assert [record.id for record in stale] == ["synthetic-map-historical-comp-001"]
    assert len(sampleton_verified) == 4
    assert [record.id for record in sale_comps] == ["synthetic-map-sale-comp-001"]


def test_map_workspace_response_syncs_table_rows_and_map_pins() -> None:
    response = build_map_workspace_response(
        fixture_path=FIXTURE_PATH,
        filters={"property_type": "industrial"},
        selected_record_id="synthetic-map-sale-comp-001",
    ).to_dict()

    assert response["schema_version"] == MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION
    assert len(response["table_rows"]) == 5
    assert len(response["map_pins"]) == 5
    assert {row["id"] for row in response["table_rows"]} == {
        pin["id"] for pin in response["map_pins"]
    }
    assert response["selected_record"]["id"] == "synthetic-map-sale-comp-001"
    assert [
        row["id"]
        for row in response["table_rows"]
        if row["is_selected"]
    ] == ["synthetic-map-sale-comp-001"]
    assert [
        pin["id"]
        for pin in response["map_pins"]
        if pin["is_selected"]
    ] == ["synthetic-map-sale-comp-001"]


def test_map_workspace_response_includes_counts_and_available_filters() -> None:
    response = build_map_workspace_response(
        fixture_path=FIXTURE_PATH,
        filters={"record_type": "historical_comp", "stale_flag": True},
    ).to_dict()

    assert response["result_counts"] == {
        "total_records": 6,
        "filtered_records": 1,
        "map_pins": 1,
        "stale_records": 1,
        "by_record_type": {"historical_comp": 1},
    }
    assert "industrial" in response["available_filters"]["property_type"]
    assert "office" in response["available_filters"]["property_type"]
    assert response["available_filters"]["stale_flag"] == [False, True]


def test_map_workspace_payload_is_synthetic_only() -> None:
    response = build_map_workspace_response(fixture_path=FIXTURE_PATH).to_dict()
    serialized = json.dumps(response).lower()

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized
    assert "google maps" not in serialized
