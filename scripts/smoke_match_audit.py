"""Smoke validation for local synthetic match audit event builders."""

import json

from falcon_intel.audit import (
    build_card_viewed_event,
    build_evidence_opened_event,
    build_historical_comp_justification_event,
    build_match_rejected_event,
    build_match_selected_event,
)


def main() -> None:
    context = {
        "tenant_id": "tenant-synthetic-001",
        "order_id": "falcon-order-synthetic-001",
        "user_id": "user-synthetic-001",
    }
    match_id = "synthetic-sale-industrial-1"
    events = [
        build_card_viewed_event(**context, metadata={"schema_version": "1"}),
        build_evidence_opened_event(**context, match_id=match_id),
        build_match_selected_event(**context, match_id=match_id),
        build_match_rejected_event(**context, match_id=match_id),
        build_historical_comp_justification_event(
            **context,
            match_id=match_id,
            justification="Synthetic justification for local smoke validation.",
        ),
    ]

    payload = [event.to_dict() for event in events]
    assert [event["event_code"] for event in payload] == [
        "viewed_match",
        "opened_evidence",
        "selected_comp_fact",
        "rejected_match",
        "wrote_justification",
    ]
    assert payload[0].get("match_id") is None
    assert all(event["tenant_id"] == context["tenant_id"] for event in payload)

    serialized = json.dumps(payload).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized

    print("match audit smoke validation passed")


if __name__ == "__main__":
    main()
