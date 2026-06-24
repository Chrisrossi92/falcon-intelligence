"""Local in-memory audit event builder for future Falcon interactions."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from falcon_intel.match_policy import AuditEventCode


MATCH_REQUIRED_EVENTS = {
    AuditEventCode.OPENED_EVIDENCE,
    AuditEventCode.SELECTED_COMP_FACT,
    AuditEventCode.REJECTED_MATCH,
    AuditEventCode.WROTE_JUSTIFICATION,
}


@dataclass(frozen=True)
class MatchAuditEvent:
    """Synthetic/local audit event object with no persistence side effects."""

    event_code: str
    tenant_id: str
    order_id: str
    user_id: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)
    match_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.match_id is None:
            payload.pop("match_id")
        return payload


def build_card_viewed_event(
    *,
    tenant_id: str,
    order_id: str,
    user_id: str,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> MatchAuditEvent:
    """Build an audit event for viewing the Firm Intelligence card."""

    return build_match_audit_event(
        AuditEventCode.VIEWED_MATCH,
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        metadata=metadata,
        timestamp=timestamp,
    )


def build_evidence_opened_event(
    *,
    tenant_id: str,
    order_id: str,
    user_id: str,
    match_id: str,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> MatchAuditEvent:
    """Build an audit event for opening evidence or provenance details."""

    return build_match_audit_event(
        AuditEventCode.OPENED_EVIDENCE,
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        match_id=match_id,
        metadata=metadata,
        timestamp=timestamp,
    )


def build_match_selected_event(
    *,
    tenant_id: str,
    order_id: str,
    user_id: str,
    match_id: str,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> MatchAuditEvent:
    """Build an audit event for selecting a comp, fact, or indicator."""

    return build_match_audit_event(
        AuditEventCode.SELECTED_COMP_FACT,
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        match_id=match_id,
        metadata=metadata,
        timestamp=timestamp,
    )


def build_match_rejected_event(
    *,
    tenant_id: str,
    order_id: str,
    user_id: str,
    match_id: str,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> MatchAuditEvent:
    """Build an audit event for marking a match not relevant."""

    return build_match_audit_event(
        AuditEventCode.REJECTED_MATCH,
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        match_id=match_id,
        metadata=metadata,
        timestamp=timestamp,
    )


def build_historical_comp_justification_event(
    *,
    tenant_id: str,
    order_id: str,
    user_id: str,
    match_id: str,
    justification: str,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> MatchAuditEvent:
    """Build an audit event for historical comp justification."""

    active_metadata = dict(metadata or {})
    active_metadata["justification"] = justification
    return build_match_audit_event(
        AuditEventCode.WROTE_JUSTIFICATION,
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        match_id=match_id,
        metadata=active_metadata,
        timestamp=timestamp,
    )


def build_match_audit_event(
    event_code: AuditEventCode | str,
    *,
    tenant_id: str,
    order_id: str,
    user_id: str,
    match_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> MatchAuditEvent:
    """Build one validated local audit event object."""

    active_code = AuditEventCode(event_code)
    _require_non_empty("tenant_id", tenant_id)
    _require_non_empty("order_id", order_id)
    _require_non_empty("user_id", user_id)
    if active_code in MATCH_REQUIRED_EVENTS:
        _require_non_empty("match_id", match_id)

    return MatchAuditEvent(
        event_code=active_code.value,
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        match_id=match_id,
        timestamp=timestamp or datetime.now(UTC).isoformat(),
        metadata=dict(metadata or {}),
    )


def _require_non_empty(field_name: str, value: str | None) -> None:
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")
