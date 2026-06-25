import json

import pytest

from falcon_intel.report_registry import (
    ReportField,
    approve_report_fields,
    build_demo_subject_profile,
    lock_report_fields,
)


def test_demo_subject_profile_groups_required_appraiser_sections() -> None:
    profile = build_demo_subject_profile()
    payload = profile.to_dict()

    assert payload["subject"] == "517 E Riverview Avenue"
    assert [section["title"] for section in payload["sections"]] == [
        "Assignment Summary",
        "Current Ownership / Transaction",
        "Property Identification",
        "Site Data",
        "Improvement Data",
        "Zoning",
        "Assessment / Tax Data",
        "Inspection / Photo Observations",
        "Open Verification Items",
        "Narrative Themes",
    ]
    assert payload["readiness"]["missingCount"] == 3
    assert payload["readiness"]["reportMergeReadiness"] == "blocked"
    assert "517 E Riverview Avenue" in json.dumps(payload)


def test_report_fields_require_dot_notation() -> None:
    with pytest.raises(ValueError):
        ReportField(
            key="subject",
            label="Subject",
            value="517 E Riverview Avenue",
            source="Synthetic",
            confidence=90,
            status="approved",
            notes="Invalid key for test.",
            used_in_report_count=1,
        )


def test_approving_and_locking_fields_updates_merge_readiness() -> None:
    profile = build_demo_subject_profile()
    profile = approve_report_fields(
        profile,
        (
            "assignment.property_rights",
            "subject.county",
            "site.size_acres",
            "site.flood_zone",
            "improvements.gba_sf",
            "improvements.year_built",
            "improvements.condition",
            "zoning.code",
            "ownership.owner_name",
            "transaction.purchase_price",
            "occupancy.status",
            "occupancy.current_user",
        ),
    )
    profile = lock_report_fields(profile, ("transaction.purchase_price",))
    readiness = profile.to_dict()["readiness"]

    assert profile.registry["transaction.purchase_price"].status == "locked"
    assert readiness["reportMergeReadiness"] == "nearly_ready"
    assert readiness["lockedCount"] == 2


def test_missing_fields_cannot_be_approved() -> None:
    profile = build_demo_subject_profile()

    with pytest.raises(ValueError):
        approve_report_fields(profile, ("subject.parcel_number",))


def test_unknown_field_action_is_rejected() -> None:
    profile = build_demo_subject_profile()

    with pytest.raises(ValueError):
        lock_report_fields(profile, ("subject.unknown",))
