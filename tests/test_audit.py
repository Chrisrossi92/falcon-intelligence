import json

import pytest

from falcon_intel.audit import (
    build_card_viewed_event,
    build_evidence_opened_event,
    build_historical_comp_justification_event,
    build_match_audit_event,
    build_match_rejected_event,
    build_match_selected_event,
)
from falcon_intel.match_policy import AuditEventCode


BASE_CONTEXT = {
    "tenant_id": "tenant-synthetic-001",
    "order_id": "falcon-order-synthetic-001",
    "user_id": "user-synthetic-001",
}
MATCH_ID = "synthetic-sale-industrial-1"
TIMESTAMP = "2026-06-24T12:00:00+00:00"


def test_builds_card_viewed_event_without_match_id() -> None:
    event = build_card_viewed_event(
        **BASE_CONTEXT,
        timestamp=TIMESTAMP,
        metadata={"schema_version": "1"},
    ).to_dict()

    assert event == {
        "event_code": "viewed_match",
        "tenant_id": "tenant-synthetic-001",
        "order_id": "falcon-order-synthetic-001",
        "user_id": "user-synthetic-001",
        "timestamp": TIMESTAMP,
        "metadata": {"schema_version": "1"},
    }


def test_builds_match_specific_audit_events() -> None:
    events = [
        build_evidence_opened_event(
            **BASE_CONTEXT,
            match_id=MATCH_ID,
            timestamp=TIMESTAMP,
            metadata={"source_type": "sale_comp"},
        ),
        build_match_selected_event(
            **BASE_CONTEXT,
            match_id=MATCH_ID,
            timestamp=TIMESTAMP,
            metadata={"category_code": "verified_sale_comps"},
        ),
        build_match_rejected_event(
            **BASE_CONTEXT,
            match_id=MATCH_ID,
            timestamp=TIMESTAMP,
            metadata={"reason": "not comparable"},
        ),
    ]

    assert [event.event_code for event in events] == [
        "opened_evidence",
        "selected_comp_fact",
        "rejected_match",
    ]
    assert all(event.match_id == MATCH_ID for event in events)


def test_builds_historical_comp_justification_event() -> None:
    event = build_historical_comp_justification_event(
        **BASE_CONTEXT,
        match_id=MATCH_ID,
        justification="Synthetic historical comp remains relevant due to similar size.",
        timestamp=TIMESTAMP,
        metadata={"warning_code": "stale"},
    ).to_dict()

    assert event["event_code"] == "wrote_justification"
    assert event["match_id"] == MATCH_ID
    assert event["metadata"] == {
        "justification": "Synthetic historical comp remains relevant due to similar size.",
        "warning_code": "stale",
    }


def test_validates_required_fields_and_match_id() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        build_card_viewed_event(
            tenant_id="",
            order_id="falcon-order-synthetic-001",
            user_id="user-synthetic-001",
        )

    with pytest.raises(ValueError, match="match_id"):
        build_match_selected_event(
            **BASE_CONTEXT,
            match_id="",
        )


def test_rejects_unknown_audit_event_code() -> None:
    with pytest.raises(ValueError):
        build_match_audit_event(
            "unknown_event",
            **BASE_CONTEXT,
        )


def test_uses_stable_audit_event_codes_and_no_source_content_fields() -> None:
    event = build_match_audit_event(
        AuditEventCode.OPENED_EVIDENCE,
        **BASE_CONTEXT,
        match_id=MATCH_ID,
        timestamp=TIMESTAMP,
    ).to_dict()

    assert event["event_code"] == AuditEventCode.OPENED_EVIDENCE.value
    serialized = json.dumps(event).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized
