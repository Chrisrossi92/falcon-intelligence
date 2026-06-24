import json
from pathlib import Path
from typing import Any

from falcon_intel.historical_comp import (
    HistoricalCompReasonCode,
    build_historical_comp_justification,
)
from falcon_intel.schema_registry import (
    AUDIT_EVENT_ENVELOPE_SCHEMA_VERSION,
    SchemaName,
    get_schema_registry_entry,
)
from falcon_intel.synthetic_workflow import run_synthetic_intelligence_workflow


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
AUDIT_EVENT_FIXTURE_ROOT = FIXTURE_ROOT / "synthetic_audit_events"


ORDER_PAYLOAD = {
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


def test_workflow_audit_events_match_v1_snapshots() -> None:
    events = _workflow_audit_events()

    assert _normalize_timestamp(events[0]) == _load_snapshot("card-viewed-audit-event-v1.json")
    assert _normalize_timestamp(events[1]) == _load_snapshot("passport-detail-opened-audit-event-v1.json")
    assert _normalize_timestamp(events[2]) == _load_snapshot("evidence-opened-audit-event-v1.json")


def test_historical_comp_audit_event_matches_v1_snapshot() -> None:
    event = build_historical_comp_justification(
        comp_id="synthetic-sale-industrial-1",
        comp_date="2025-12-01",
        reason_code=HistoricalCompReasonCode.BENCHMARK_SALE.value,
        tenant_id="tenant-synthetic-001",
        order_id="falcon-order-synthetic-001",
        user_id="user-synthetic-001",
    ).to_dict()["suggested_audit_event"]

    assert _normalize_timestamp(event) == _load_snapshot(
        "historical-comp-justification-audit-event-v1.json"
    )


def test_audit_event_schema_registry_points_to_snapshot_directory() -> None:
    entry = get_schema_registry_entry(SchemaName.AUDIT_EVENT_ENVELOPE)

    assert entry.current_version == AUDIT_EVENT_ENVELOPE_SCHEMA_VERSION
    assert entry.fixture_snapshot_path == "tests/fixtures/synthetic_audit_events/"
    assert AUDIT_EVENT_FIXTURE_ROOT.exists()


def test_audit_event_snapshots_are_synthetic_only() -> None:
    serialized = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in AUDIT_EVENT_FIXTURE_ROOT.glob("*.json")
    )

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized


def _workflow_audit_events() -> list[dict[str, Any]]:
    return run_synthetic_intelligence_workflow(
        ORDER_PAYLOAD,
        user_id="user-synthetic-001",
        role="appraiser",
    ).to_dict()["suggested_audit_events"]


def _load_snapshot(filename: str) -> dict[str, Any]:
    return json.loads((AUDIT_EVENT_FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _normalize_timestamp(event: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(event))
    normalized["timestamp"] = "synthetic-dynamic-timestamp"
    return normalized
