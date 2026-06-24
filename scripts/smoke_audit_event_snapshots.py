"""Smoke validation for synthetic audit event envelope snapshots."""

import json
from pathlib import Path
from typing import Any

from falcon_intel.historical_comp import (
    HistoricalCompReasonCode,
    build_historical_comp_justification,
)
from falcon_intel.synthetic_workflow import run_synthetic_intelligence_workflow


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_EVENT_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "synthetic_audit_events"


def main() -> None:
    workflow = run_synthetic_intelligence_workflow(
        {
            "order_id": "falcon-order-synthetic-001",
            "tenant_id": "tenant-synthetic-001",
            "address": "1000 Example Industrial Way",
            "city": "Sampleton",
            "state": "ST",
            "property_type": "industrial",
            "building_size_sf": 50000,
            "client": "Synthetic Lender A",
            "borrower_contact": "Synthetic Borrower Contact",
        },
        user_id="user-synthetic-001",
        role="appraiser",
    ).to_dict()
    card_event, passport_event, evidence_event = workflow["suggested_audit_events"]
    historical_event = build_historical_comp_justification(
        comp_id="synthetic-sale-industrial-1",
        comp_date="2025-12-01",
        reason_code=HistoricalCompReasonCode.BENCHMARK_SALE.value,
        tenant_id="tenant-synthetic-001",
        order_id="falcon-order-synthetic-001",
        user_id="user-synthetic-001",
    ).to_dict()["suggested_audit_event"]

    assert _normalize_timestamp(card_event) == _load_snapshot("card-viewed-audit-event-v1.json")
    assert _normalize_timestamp(passport_event) == _load_snapshot("passport-detail-opened-audit-event-v1.json")
    assert _normalize_timestamp(evidence_event) == _load_snapshot("evidence-opened-audit-event-v1.json")
    assert _normalize_timestamp(historical_event) == _load_snapshot(
        "historical-comp-justification-audit-event-v1.json"
    )

    serialized = json.dumps(
        {
            "card": card_event,
            "passport": passport_event,
            "evidence": evidence_event,
            "historical": historical_event,
        }
    ).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized

    print("audit event snapshot smoke validation passed")


def _load_snapshot(filename: str) -> dict[str, Any]:
    return json.loads((AUDIT_EVENT_FIXTURE_ROOT / filename).read_text(encoding="utf-8"))


def _normalize_timestamp(event: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(event))
    normalized["timestamp"] = "synthetic-dynamic-timestamp"
    return normalized


if __name__ == "__main__":
    main()
