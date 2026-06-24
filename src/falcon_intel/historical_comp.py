"""Synthetic/local model for historical comparable justification prompts."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from falcon_intel.audit import build_historical_comp_justification_event
from falcon_intel.match_policy import AuditEventCode, WarningCode


class HistoricalCompReasonCode(StrEnum):
    """Stable reason code constants for historical comparable justification."""

    LIMITED_MARKET_ACTIVITY = "limited_market_activity"
    UNIQUE_PROPERTY_CHARACTERISTICS = "unique_property_characteristics"
    BEST_AVAILABLE_COMPARABLE = "best_available_comparable"
    BENCHMARK_SALE = "benchmark_sale"
    PAIRED_SALE_SUPPORT = "paired_sale_support"
    OTHER = "other"


HISTORICAL_COMP_REASON_CODES = tuple(reason.value for reason in HistoricalCompReasonCode)

REASON_LABELS = {
    HistoricalCompReasonCode.LIMITED_MARKET_ACTIVITY: "Limited market activity",
    HistoricalCompReasonCode.UNIQUE_PROPERTY_CHARACTERISTICS: "Unique property characteristics",
    HistoricalCompReasonCode.BEST_AVAILABLE_COMPARABLE: "Best available comparable",
    HistoricalCompReasonCode.BENCHMARK_SALE: "Benchmark sale",
    HistoricalCompReasonCode.PAIRED_SALE_SUPPORT: "Paired sale support",
    HistoricalCompReasonCode.OTHER: "Other",
}

REASON_NARRATIVE_FRAGMENTS = {
    HistoricalCompReasonCode.LIMITED_MARKET_ACTIVITY: "market activity was limited for comparable properties",
    HistoricalCompReasonCode.UNIQUE_PROPERTY_CHARACTERISTICS: "the subject has unique characteristics that limit directly comparable alternatives",
    HistoricalCompReasonCode.BEST_AVAILABLE_COMPARABLE: "it represents the best available comparable evidence after review",
    HistoricalCompReasonCode.BENCHMARK_SALE: "it provides benchmark sale context for the market",
    HistoricalCompReasonCode.PAIRED_SALE_SUPPORT: "it supports paired-sale analysis for a relevant comparison point",
    HistoricalCompReasonCode.OTHER: "the appraiser provided a specific professional rationale",
}


@dataclass(frozen=True)
class HistoricalCompJustificationRecord:
    """Structured local justification record for a historical comparable."""

    comp_id: str
    comp_date: str
    reason_code: str
    reason_label: str
    custom_explanation: str | None
    tenant_id: str
    order_id: str
    user_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HistoricalCompJustificationResult:
    """Complete local justification payload for future UI/API use."""

    justification_record: HistoricalCompJustificationRecord
    warning_code: str
    reusable_narrative: str
    suggested_audit_event: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["justification_record"] = self.justification_record.to_dict()
        return payload


def build_historical_comp_justification(
    *,
    comp_id: str,
    comp_date: str,
    reason_code: str,
    tenant_id: str,
    order_id: str,
    user_id: str,
    custom_explanation: str | None = None,
) -> HistoricalCompJustificationResult:
    """Build a synthetic/local historical comparable justification payload."""

    _require_non_empty("comp_id", comp_id)
    _require_non_empty("comp_date", comp_date)
    _require_non_empty("tenant_id", tenant_id)
    _require_non_empty("order_id", order_id)
    _require_non_empty("user_id", user_id)
    active_reason = _validate_reason_code(reason_code)
    if active_reason == HistoricalCompReasonCode.OTHER:
        _require_non_empty("custom_explanation", custom_explanation)

    record = HistoricalCompJustificationRecord(
        comp_id=comp_id,
        comp_date=comp_date,
        reason_code=active_reason.value,
        reason_label=REASON_LABELS[active_reason],
        custom_explanation=custom_explanation,
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
    )
    narrative = _narrative(record)
    audit_event = build_historical_comp_justification_event(
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        match_id=comp_id,
        justification=narrative,
        metadata={
            "comp_date": comp_date,
            "reason_code": active_reason.value,
            "warning_code": WarningCode.STALE_MATCH.value,
            "audit_reason": AuditEventCode.WROTE_JUSTIFICATION.value,
        },
    ).to_dict()

    return HistoricalCompJustificationResult(
        justification_record=record,
        warning_code=WarningCode.STALE_MATCH.value,
        reusable_narrative=narrative,
        suggested_audit_event=audit_event,
    )


def _validate_reason_code(reason_code: str) -> HistoricalCompReasonCode:
    try:
        return HistoricalCompReasonCode(reason_code)
    except ValueError as error:
        raise ValueError(f"Unsupported historical comparable reason code: {reason_code}")


def _narrative(record: HistoricalCompJustificationRecord) -> str:
    narrative = (
        f"Historical comparable {record.comp_id}, dated {record.comp_date}, "
        f"was retained for consideration because "
        f"{REASON_NARRATIVE_FRAGMENTS[HistoricalCompReasonCode(record.reason_code)]}."
    )
    if record.custom_explanation:
        narrative = f"{narrative} Appraiser rationale: {record.custom_explanation.strip()}"
    return narrative


def _require_non_empty(field_name: str, value: str | None) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")
