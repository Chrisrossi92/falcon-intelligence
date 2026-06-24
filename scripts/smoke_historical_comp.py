"""Smoke validation for historical comparable justification payloads."""

import json

from falcon_intel.historical_comp import (
    HistoricalCompReasonCode,
    build_historical_comp_justification,
)


def main() -> None:
    result = build_historical_comp_justification(
        comp_id="synthetic-sale-industrial-1",
        comp_date="2025-12-01",
        reason_code=HistoricalCompReasonCode.BENCHMARK_SALE.value,
        tenant_id="tenant-synthetic-001",
        order_id="falcon-order-synthetic-001",
        user_id="user-synthetic-001",
    ).to_dict()

    assert result["warning_code"] == "stale"
    assert result["justification_record"]["reason_code"] == "benchmark_sale"
    assert result["suggested_audit_event"]["event_code"] == "wrote_justification"
    assert "benchmark sale context" in result["reusable_narrative"]

    serialized = json.dumps(result).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized

    print("historical comp justification smoke validation passed")


if __name__ == "__main__":
    main()
