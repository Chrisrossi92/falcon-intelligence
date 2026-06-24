"""Smoke validation for the synthetic Firm Intelligence Found card CLI."""

import contextlib
import io
import json

from falcon_intel.cli import main


def main_smoke() -> None:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        assert main(
            [
                "intelligence-card",
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
        ) == 0

    payload = json.loads(buffer.getvalue())
    assert payload["schema_version"] == "1"
    assert payload["headline"].startswith("Firm Intelligence Found")
    assert payload["confidence_provenance_summary"]["synthetic_fixture_only"] is True
    group_counts = {
        group["group"]: group["count"]
        for group in payload["match_group_summaries"]
    }
    assert group_counts["same_subject_property"] == 1
    assert payload["top_match_cards"][0]["score"] == 100
    assert payload["top_match_cards"][0]["provenance"]["verification_status"] == "verified"
    assert "synthetic_preview_only" in {warning["code"] for warning in payload["warnings"]}

    serialized = json.dumps(payload).lower()
    assert "report_text" not in serialized
    assert "source_file_path" not in serialized

    print("synthetic intelligence card CLI smoke validation passed")


if __name__ == "__main__":
    main_smoke()
