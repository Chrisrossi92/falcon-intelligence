"""Smoke validation for the synthetic-only firm intelligence matcher."""

import json
from pathlib import Path

from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "synthetic_verified_intelligence"
    / "verified-intelligence.json"
)


def main() -> None:
    intelligence = load_synthetic_verified_intelligence(FIXTURE_PATH)
    result = match_firm_intelligence(
        FakeOrder(
            address="1000 Example Industrial Way",
            city="Sampleton",
            state="ST",
            property_type="industrial",
            building_size_sf=50000,
            client="Synthetic Lender A",
            borrower_contact="Synthetic Borrower Contact",
        ),
        intelligence,
    ).to_dict()

    groups = result["match_groups"]
    assert groups["same_subject_property"]
    assert groups["nearby_prior_assignments"]
    assert groups["same_property_type"]
    assert groups["similar_building_size"]
    assert groups["same_client"]
    assert groups["verified_sale_comps"]
    assert groups["verified_lease_comps"]
    assert groups["relevant_market_indicators"]

    serialized = json.dumps(result).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "onedrive" not in serialized

    print("synthetic intelligence matcher smoke validation passed")


if __name__ == "__main__":
    main()
