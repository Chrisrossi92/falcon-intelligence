"""Smoke validation for committed synthetic sample intelligence fixtures."""

import json
from pathlib import Path

from falcon_intel.discovery import discover_assignments
from falcon_intel.manifest import create_scan_manifest
from falcon_intel.profile import build_assignment_profile
from falcon_intel.scanner import scan_metadata
from falcon_intel.search import ManifestSearchQuery, search_manifest, summarize_results


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures"
SAMPLE_ROOT = FIXTURE_ROOT / "synthetic_sample_data"
MANIFEST_PATH = FIXTURE_ROOT / "synthetic_manifests" / "synthetic-sample-intelligence-manifest.json"
PROFILE_DIR = FIXTURE_ROOT / "synthetic_profiles"
EXPECTED_ASSIGNMENTS = {
    "assignments/synthetic-industrial-flex-alpha",
    "assignments/synthetic-retail-plaza-bravo",
    "assignments/synthetic-office-suite-charlie",
    "assignments/synthetic-purchase-delta",
    "assignments/synthetic-lease-heavy-echo",
    "assignments/synthetic-wip-foxtrot",
}


def main() -> None:
    scanned_records = [
        record
        for record in scan_metadata(SAMPLE_ROOT)
        if record.relative_path != "README.md"
    ]
    scanned_manifest = create_scan_manifest(scanned_records, "Synthetic Sample Intelligence Fixtures").to_dict()
    fixture_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert "absolute_root_path" not in scanned_manifest
    assert scanned_manifest["file_count"] == fixture_manifest["file_count"] == 29
    assert scanned_manifest["counts_by_extension"] == fixture_manifest["counts_by_extension"]

    search_results = search_manifest(
        fixture_manifest,
        ManifestSearchQuery(file_name_keyword="appraisal", supported_for_future_indexing=True),
    )
    assert len(search_results) == 5
    assert all(result.absolute_root_path is None for result in search_results)

    summary = summarize_results(search_manifest(fixture_manifest))
    assert summary.total_files == 29
    assert summary.supported_future_indexing_files == 19
    assert summary.likely_report_candidates == 11

    candidates = discover_assignments(fixture_manifest)
    by_folder = {candidate.assignment_folder: candidate for candidate in candidates}
    assert set(by_folder) == EXPECTED_ASSIGNMENTS
    assert by_folder["assignments/synthetic-wip-foxtrot"].heuristic == "DOCX + XLSX = Work in progress"
    assert by_folder["assignments/synthetic-lease-heavy-echo"].excel_count == 2

    for assignment_folder in EXPECTED_ASSIGNMENTS:
        profile = build_assignment_profile(fixture_manifest, assignment_folder).to_dict()
        profile_name = f"{assignment_folder.split('/')[-1]}-profile.json"
        fixture_profile = json.loads((PROFILE_DIR / profile_name).read_text(encoding="utf-8"))
        assert profile == fixture_profile

    serialized_fixtures = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in FIXTURE_ROOT.rglob("*")
        if path.is_file()
    )
    for blocked_term in {"continental", "onedrive", "report number", "client"}:
        assert blocked_term not in serialized_fixtures

    print("synthetic fixture workflow smoke validation passed")


if __name__ == "__main__":
    main()
