import pytest

from falcon_intel.property_library import (
    CandidateMatch,
    PropertyLibraryFilters,
    build_demo_property_library_workspace,
)


def test_property_library_returns_map_table_drawer_and_conflicts() -> None:
    workspace = build_demo_property_library_workspace()

    assert workspace["workspaceType"] == "synthetic_property_library_preview"
    assert workspace["map"]["mode"] == "map_placeholder"
    assert workspace["map"]["markerCount"] == 6
    assert workspace["summary"]["propertyCount"] == 6
    assert workspace["summary"]["candidateConflictCount"] == 3
    assert workspace["selectedPropertyDrawer"]["property"]["property_id"] == "prop-main-1220"
    assert workspace["resultsTable"][0]["linkedReports"] == ["FI-2025-144", "FI-2025-151"]


def test_property_library_filters_by_type_county_role_and_status() -> None:
    workspace = build_demo_property_library_workspace(
        PropertyLibraryFilters(
            property_type="Commercial",
            county="Montgomery County",
            comp_role="sale_comparable",
            verification_status="verified",
        )
    )

    assert workspace["summary"]["propertyCount"] == 1
    row = workspace["resultsTable"][0]
    assert row["propertyId"] == "prop-main-1220"
    assert row["reportUsageRoles"] == ["cap_rate_support", "sale_comparable"]


def test_property_library_searches_evidence_and_report_usages() -> None:
    workspace = build_demo_property_library_workspace(PropertyLibraryFilters(query="medical"))

    assert workspace["summary"]["propertyCount"] == 1
    assert workspace["resultsTable"][0]["propertyId"] == "prop-market-88"
    assert workspace["selectedPropertyDrawer"]["evidenceEvents"][0]["event_type"] == "lease_rent"


def test_property_library_date_and_size_filters_are_applied() -> None:
    workspace = build_demo_property_library_workspace(
        PropertyLibraryFilters(
            date_from="2026-01-01",
            date_to="2026-12-31",
            min_size_sf=30000,
        )
    )

    assert [row["propertyId"] for row in workspace["resultsTable"]] == [
        "prop-dixie-4100",
        "prop-countyline-730",
    ]


def test_property_library_selected_drawer_can_target_conflict_candidate() -> None:
    workspace = build_demo_property_library_workspace(
        PropertyLibraryFilters(selected_property_id="prop-riverview-517")
    )

    drawer = workspace["selectedPropertyDrawer"]
    assert drawer["property"]["address"] == "517 E Riverview Avenue"
    assert {match["conflict_type"] for match in drawer["candidateMatches"]} == {
        "same_address_conflicting_size",
        "same_sale_different_price",
        "same_comp_used_by_different_appraisers",
    }


def test_property_library_rejects_invalid_ranges() -> None:
    with pytest.raises(ValueError):
        PropertyLibraryFilters(date_from="2026-12-31", date_to="2026-01-01")

    with pytest.raises(ValueError):
        PropertyLibraryFilters(min_size_sf=10000, max_size_sf=5000)


def test_candidate_match_requires_two_properties() -> None:
    with pytest.raises(ValueError):
        CandidateMatch(
            match_id="bad-match",
            property_ids=("prop-one",),
            conflict_type="same_address_conflicting_size",
            summary="Invalid single-property match.",
            conflicting_fields={"building_size_sf": [1000]},
            confidence_score=80,
            review_status="candidate",
        )
