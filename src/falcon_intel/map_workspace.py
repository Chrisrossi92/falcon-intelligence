"""Synthetic/local contract for a future Falcon Intelligence Map Workspace."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from falcon_intel.schema_registry import MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION


DEFAULT_SYNTHETIC_MAP_WORKSPACE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "synthetic_map_workspace"
    / "map-records.json"
)


@dataclass(frozen=True)
class SyntheticMapRecord:
    """One synthetic record that can appear in the table and map."""

    id: str
    record_type: str
    display_label: str
    address: str
    city: str
    state: str
    latitude: float
    longitude: float
    property_type: str
    status: str
    verification_status: str
    confidence_summary: str
    passport_id: str | None = None
    evidence_link_count: int | None = None
    stale_flag: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MapWorkspaceFilters:
    """Supported synthetic map workspace filters."""

    property_type: str | None = None
    record_type: str | None = None
    status: str | None = None
    verification_status: str | None = None
    stale_flag: bool | None = None
    city: str | None = None
    state: str | None = None


@dataclass(frozen=True)
class MapWorkspaceResponse:
    """UI-facing synthetic map workspace payload."""

    schema_version: str
    table_rows: list[dict[str, Any]]
    map_pins: list[dict[str, Any]]
    selected_record: dict[str, Any] | None
    result_counts: dict[str, Any]
    available_filters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_synthetic_map_records(
    fixture_path: str | Path = DEFAULT_SYNTHETIC_MAP_WORKSPACE_PATH,
) -> list[SyntheticMapRecord]:
    """Load synthetic map records from the committed fixture."""

    payload = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    if payload.get("fixture_kind") != "synthetic_map_workspace_records":
        raise ValueError("Map workspace requires synthetic map workspace records.")
    return [SyntheticMapRecord(**record) for record in payload.get("records", [])]


def filter_map_records(
    records: list[SyntheticMapRecord],
    filters: MapWorkspaceFilters | dict[str, Any] | None = None,
) -> list[SyntheticMapRecord]:
    """Filter synthetic map records by table/map filter state."""

    active_filters = _coerce_filters(filters)
    return [
        record
        for record in records
        if _matches_optional(record.property_type, active_filters.property_type)
        and _matches_optional(record.record_type, active_filters.record_type)
        and _matches_optional(record.status, active_filters.status)
        and _matches_optional(record.verification_status, active_filters.verification_status)
        and _matches_optional(record.city, active_filters.city)
        and _matches_optional(record.state, active_filters.state)
        and (
            active_filters.stale_flag is None
            or bool(record.stale_flag) is active_filters.stale_flag
        )
    ]


def build_map_workspace_response(
    records: list[SyntheticMapRecord] | None = None,
    *,
    filters: MapWorkspaceFilters | dict[str, Any] | None = None,
    selected_record_id: str | None = None,
    fixture_path: str | Path = DEFAULT_SYNTHETIC_MAP_WORKSPACE_PATH,
) -> MapWorkspaceResponse:
    """Serialize filtered synthetic map records for a future table/map UI."""

    source_records = records if records is not None else load_synthetic_map_records(fixture_path)
    filtered_records = filter_map_records(source_records, filters)
    selected_record = _select_record(filtered_records, selected_record_id)

    return MapWorkspaceResponse(
        schema_version=MAP_WORKSPACE_RESPONSE_SCHEMA_VERSION,
        table_rows=[_table_row(record, selected_record_id) for record in filtered_records],
        map_pins=[_map_pin(record, selected_record_id) for record in filtered_records],
        selected_record=(
            _selected_record(selected_record)
            if selected_record is not None
            else None
        ),
        result_counts=_result_counts(source_records, filtered_records),
        available_filters=_available_filters(source_records),
    )


def _coerce_filters(filters: MapWorkspaceFilters | dict[str, Any] | None) -> MapWorkspaceFilters:
    if filters is None:
        return MapWorkspaceFilters()
    if isinstance(filters, MapWorkspaceFilters):
        return filters
    return MapWorkspaceFilters(**filters)


def _matches_optional(value: str, expected: str | None) -> bool:
    return expected is None or value.lower() == expected.lower()


def _table_row(record: SyntheticMapRecord, selected_record_id: str | None) -> dict[str, Any]:
    payload = record.to_dict()
    payload["is_selected"] = record.id == selected_record_id
    return payload


def _map_pin(record: SyntheticMapRecord, selected_record_id: str | None) -> dict[str, Any]:
    return {
        "id": record.id,
        "record_type": record.record_type,
        "display_label": record.display_label,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "property_type": record.property_type,
        "status": record.status,
        "verification_status": record.verification_status,
        "stale_flag": bool(record.stale_flag),
        "is_selected": record.id == selected_record_id,
    }


def _selected_record(records: SyntheticMapRecord) -> dict[str, Any]:
    return records.to_dict()


def _select_record(
    records: list[SyntheticMapRecord],
    selected_record_id: str | None,
) -> SyntheticMapRecord | None:
    if selected_record_id is None:
        return None
    for record in records:
        if record.id == selected_record_id:
            return record
    return None


def _result_counts(
    source_records: list[SyntheticMapRecord],
    filtered_records: list[SyntheticMapRecord],
) -> dict[str, Any]:
    return {
        "total_records": len(source_records),
        "filtered_records": len(filtered_records),
        "map_pins": len(filtered_records),
        "stale_records": sum(1 for record in filtered_records if record.stale_flag),
        "by_record_type": _count_by(filtered_records, "record_type"),
    }


def _available_filters(records: list[SyntheticMapRecord]) -> dict[str, Any]:
    return {
        "property_type": _unique(records, "property_type"),
        "record_type": _unique(records, "record_type"),
        "status": _unique(records, "status"),
        "verification_status": _unique(records, "verification_status"),
        "city": _unique(records, "city"),
        "state": _unique(records, "state"),
        "stale_flag": [False, True],
    }


def _unique(records: list[SyntheticMapRecord], field_name: str) -> list[str]:
    return sorted({str(getattr(record, field_name)) for record in records})


def _count_by(records: list[SyntheticMapRecord], field_name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(getattr(record, field_name))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
