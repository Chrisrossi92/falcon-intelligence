import json
from pathlib import Path

from falcon_intel.discovery import discover_assignments
from falcon_intel.manifest import create_scan_manifest
from falcon_intel.profile import build_assignment_profile
from falcon_intel.scanner import scan_metadata
from falcon_intel.search import ManifestSearchQuery, search_manifest, summarize_results


FIXTURE_ROOT = Path(__file__).parent / "fixtures"
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


def test_synthetic_fixture_manifest_exercises_metadata_workflows() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    search_results = search_manifest(
        manifest,
        ManifestSearchQuery(file_name_keyword="appraisal", supported_for_future_indexing=True),
    )
    assert len(search_results) == 5
    assert all(result.absolute_root_path is None for result in search_results)

    summary = summarize_results(search_manifest(manifest))
    assert summary.total_files == 29
    assert summary.supported_future_indexing_files == 19
    assert summary.likely_report_candidates == 11

    candidates = discover_assignments(manifest)
    by_folder = {candidate.assignment_folder: candidate for candidate in candidates}
    assert set(by_folder) == EXPECTED_ASSIGNMENTS
    assert by_folder["assignments/synthetic-wip-foxtrot"].heuristic == "DOCX + XLSX = Work in progress"
    assert by_folder["assignments/synthetic-lease-heavy-echo"].excel_count == 2

    for assignment_folder in EXPECTED_ASSIGNMENTS:
        profile = build_assignment_profile(manifest, assignment_folder)
        assert profile.assignment_folder == assignment_folder
        assert profile.to_dict() == _load_profile_fixture(assignment_folder)


def test_synthetic_fixture_tree_can_be_scanned_without_source_data() -> None:
    manifest = create_scan_manifest(
        [
            record
            for record in scan_metadata(SAMPLE_ROOT)
            if record.relative_path != "README.md"
        ],
        "Synthetic Sample Intelligence Fixtures",
    ).to_dict()
    committed_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert "absolute_root_path" not in manifest
    assert manifest["selected_root_label"] == committed_manifest["selected_root_label"]
    assert manifest["file_count"] == committed_manifest["file_count"]
    assert manifest["counts_by_extension"] == committed_manifest["counts_by_extension"]
    assert {
        file_record["relative_path"]
        for file_record in manifest["files"]
    } == {
        file_record["relative_path"]
        for file_record in committed_manifest["files"]
    }


def test_synthetic_fixtures_do_not_contain_known_real_data_markers() -> None:
    blocked_terms = {
        "continental",
        "onedrive",
        "report number",
        "client",
    }

    for path in FIXTURE_ROOT.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8").lower()
            assert not any(term in text for term in blocked_terms), path


def _load_profile_fixture(assignment_folder: str) -> dict[str, object]:
    profile_name = f"{assignment_folder.split('/')[-1]}-profile.json"
    return json.loads((PROFILE_DIR / profile_name).read_text(encoding="utf-8"))
