import json
from pathlib import Path

import pytest

from falcon_intel.profile import build_assignment_profile, save_assignment_profile


def _record(file_name: str, extension: str, relative_path: str) -> dict[str, object]:
    return {
        "file_name": file_name,
        "file_extension": extension,
        "relative_path": relative_path,
        "file_size": 10,
        "modified_timestamp": "2026-06-24T12:00:00+00:00",
        "supported_for_future_indexing": extension in {".pdf", ".docx", ".xlsx", ".xls", ".txt"},
    }


def _manifest() -> dict[str, object]:
    return {
        "manifest_version": "1",
        "scan_timestamp": "2026-06-24T12:00:00+00:00",
        "selected_root_label": "Synthetic Selection",
        "file_count": 5,
        "counts_by_extension": {},
        "supported_future_indexing_count": 3,
        "files": [
            _record("final-report.pdf", ".pdf", "assignments/100-main/final-report.pdf"),
            _record("draft-report.docx", ".docx", "assignments/100-main/draft-report.docx"),
            _record("analysis.xlsx", ".xlsx", "assignments/100-main/workbooks/analysis.xlsx"),
            _record("front.jpg", ".jpg", "assignments/100-main/photos/front.jpg"),
            _record("notes.msg", ".msg", "assignments/100-main/notes.msg"),
        ],
    }


def test_build_assignment_profile_groups_metadata_only() -> None:
    profile = build_assignment_profile(_manifest(), "assignments/100-main")
    payload = profile.to_dict()

    assert payload["assignment_folder"] == "assignments/100-main"
    assert payload["heuristic_label"] == "high-confidence-assignment"
    assert payload["completeness_score"] == 100
    assert payload["counts_by_document_type"]["total_files"] == 5
    assert payload["counts_by_document_type"]["pdf"] == 1
    assert payload["counts_by_document_type"]["word"] == 1
    assert payload["counts_by_document_type"]["excel"] == 1
    assert [item["file_name"] for item in payload["file_groups"]["report_candidates"]] == ["draft-report.docx"]
    assert [item["file_name"] for item in payload["file_groups"]["pdf_source_document_candidates"]] == ["final-report.pdf"]
    assert [item["file_name"] for item in payload["file_groups"]["excel_workbook_candidates"]] == ["analysis.xlsx"]
    assert [item["file_name"] for item in payload["file_groups"]["photo_media_candidates"]] == ["front.jpg"]
    assert [item["file_name"] for item in payload["file_groups"]["other_files"]] == ["notes.msg"]
    assert "text" not in json.dumps(payload).lower()


def test_build_assignment_profile_rejects_unknown_folder() -> None:
    with pytest.raises(ValueError):
        build_assignment_profile(_manifest(), "missing")


def test_save_profile_requires_ignored_profile_directory(tmp_path: Path) -> None:
    profile = build_assignment_profile(_manifest(), "assignments/100-main")

    with pytest.raises(ValueError):
        save_assignment_profile(profile, output_dir=tmp_path / "exports")


def test_save_profile_writes_json_under_data_profiles(tmp_path: Path) -> None:
    profile = build_assignment_profile(_manifest(), "assignments/100-main")

    output_path = save_assignment_profile(
        profile,
        output_dir=tmp_path / "data" / "profiles",
        file_name="profile.json",
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_path.name == "profile.json"
    assert payload["assignment_folder"] == "assignments/100-main"
