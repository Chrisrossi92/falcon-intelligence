import json

import pytest

from falcon_intel.historical_comp import (
    HISTORICAL_COMP_REASON_CODES,
    HistoricalCompReasonCode,
    build_historical_comp_justification,
)


BASE_CONTEXT = {
    "comp_id": "synthetic-sale-industrial-1",
    "comp_date": "2025-12-01",
    "tenant_id": "tenant-synthetic-001",
    "order_id": "falcon-order-synthetic-001",
    "user_id": "user-synthetic-001",
}


def test_reason_codes_are_stable() -> None:
    assert list(HISTORICAL_COMP_REASON_CODES) == [
        "limited_market_activity",
        "unique_property_characteristics",
        "best_available_comparable",
        "benchmark_sale",
        "paired_sale_support",
        "other",
    ]


def test_builds_historical_comp_justification_payload() -> None:
    result = build_historical_comp_justification(
        **BASE_CONTEXT,
        reason_code=HistoricalCompReasonCode.BENCHMARK_SALE.value,
    ).to_dict()

    assert result["warning_code"] == "stale"
    assert result["justification_record"] == {
        "comp_id": "synthetic-sale-industrial-1",
        "comp_date": "2025-12-01",
        "reason_code": "benchmark_sale",
        "reason_label": "Benchmark sale",
        "custom_explanation": None,
        "tenant_id": "tenant-synthetic-001",
        "order_id": "falcon-order-synthetic-001",
        "user_id": "user-synthetic-001",
    }
    assert result["reusable_narrative"] == (
        "Historical comparable synthetic-sale-industrial-1, dated 2025-12-01, "
        "was retained for consideration because it provides benchmark sale context for the market."
    )
    assert result["suggested_audit_event"]["event_code"] == "wrote_justification"
    assert result["suggested_audit_event"]["match_id"] == "synthetic-sale-industrial-1"
    assert result["suggested_audit_event"]["metadata"]["reason_code"] == "benchmark_sale"
    assert result["suggested_audit_event"]["metadata"]["warning_code"] == "stale"


def test_other_reason_requires_and_includes_custom_explanation() -> None:
    result = build_historical_comp_justification(
        **BASE_CONTEXT,
        reason_code=HistoricalCompReasonCode.OTHER.value,
        custom_explanation="Synthetic appraiser note for local validation.",
    ).to_dict()

    assert result["justification_record"]["reason_code"] == "other"
    assert "Synthetic appraiser note" in result["reusable_narrative"]
    assert result["suggested_audit_event"]["metadata"]["justification"] == result["reusable_narrative"]


def test_validates_required_fields_and_reason_code() -> None:
    with pytest.raises(ValueError, match="comp_id"):
        build_historical_comp_justification(
            **{**BASE_CONTEXT, "comp_id": ""},
            reason_code=HistoricalCompReasonCode.BENCHMARK_SALE.value,
        )

    with pytest.raises(ValueError, match="Unsupported"):
        build_historical_comp_justification(
            **BASE_CONTEXT,
            reason_code="unsupported_reason",
        )

    with pytest.raises(ValueError, match="custom_explanation"):
        build_historical_comp_justification(
            **BASE_CONTEXT,
            reason_code=HistoricalCompReasonCode.OTHER.value,
        )


def test_historical_comp_payload_contains_no_source_content_fields() -> None:
    result = build_historical_comp_justification(
        **BASE_CONTEXT,
        reason_code=HistoricalCompReasonCode.BEST_AVAILABLE_COMPARABLE.value,
    ).to_dict()
    serialized = json.dumps(result).lower()

    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized
