import contextlib
import io
import json

import pytest

from falcon_intel.cli import main


def test_intelligence_card_cli_outputs_synthetic_card_preview() -> None:
    payload = _run_card_command(
        [
            "--address",
            "1000 Example Industrial Way",
            "--city",
            "Sampleton",
            "--state",
            "ST",
            "--property-type",
            "industrial",
            "--building-size-sf",
            "50000",
            "--client",
            "Synthetic Lender A",
        ]
    )

    assert payload["schema_version"] == "1"
    assert payload["headline"].startswith("Firm Intelligence Found")
    assert payload["confidence_provenance_summary"]["source_fixture_kind"] == "synthetic_verified_intelligence"
    assert payload["confidence_provenance_summary"]["synthetic_fixture_only"] is True
    assert payload["order_summary"]["client"] == "Synthetic Lender A"
    group_counts = {
        group["group"]: group["count"]
        for group in payload["match_group_summaries"]
    }
    assert group_counts["same_subject_property"] == 1
    assert group_counts["verified_sale_comps"] == 2
    assert payload["match_group_summaries"][0]["category_code"] == "same_subject_property"

    subject_match = payload["top_match_cards"][0]
    assert subject_match["category_code"] == "same_subject_property"
    assert subject_match["source_id"] == "synthetic-assignment-industrial-alpha"
    assert subject_match["score"] == 100
    assert "Exact synthetic address" in subject_match["explanation"]
    assert subject_match["passport_id"] == "synthetic-passport-assignment-industrial-alpha"
    assert subject_match["verification_status"] == "verified"
    assert subject_match["evidence_link_count"] == 1
    assert subject_match["searchable_status"] == "searchable"
    assert "evidence_links" not in subject_match
    assert subject_match["provenance"] == {
        "record_type": "assignment",
        "source_id": "synthetic-assignment-industrial-alpha",
        "synthetic_fixture": True,
        "verification_status": "verified",
    }

    sale_match = [
        match_card
        for match_card in payload["top_match_cards"]
        if match_card["group"] == "verified_sale_comps"
    ][0]
    assert sale_match["score"] == 95
    assert sale_match["category_code"] == "verified_sale_comps"
    assert "Verified synthetic sale comparable" in sale_match["explanation"]
    assert sale_match["provenance"]["verification_status"] == "verified"
    assert "synthetic_preview_only" in {warning["code"] for warning in payload["warnings"]}

    serialized = json.dumps(payload).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized
    assert "absolute_path" not in serialized
    assert "onedrive" not in serialized


def test_intelligence_card_cli_requires_positive_building_size() -> None:
    with pytest.raises(ValueError, match="building-size"):
        _run_card_command(
            [
                "--address",
                "1000 Example Industrial Way",
                "--city",
                "Sampleton",
                "--state",
                "ST",
                "--property-type",
                "industrial",
                "--building-size-sf",
                "0",
                "--client",
                "Synthetic Lender A",
            ]
        )


def _run_card_command(args: list[str]) -> dict[str, object]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        assert main(["intelligence-card", *args]) == 0
    return json.loads(buffer.getvalue())
