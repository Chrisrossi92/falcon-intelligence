from falcon_intel.discovery import discover_assignments


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
        "file_count": 9,
        "counts_by_extension": {},
        "supported_future_indexing_count": 6,
        "files": [
            _record("final-report.pdf", ".pdf", "assignments/100-main/final-report.pdf"),
            _record("draft-report.docx", ".docx", "assignments/100-main/draft-report.docx"),
            _record("front.jpg", ".jpg", "assignments/100-main/photos/front.jpg"),
            _record("site-map.png", ".png", "assignments/100-main/maps/site-map.png"),
            _record("archive.pdf", ".pdf", "archive/200-oak/archive.pdf"),
            _record("draft.docx", ".docx", "active/300-pine/draft.docx"),
            _record("analysis.xlsx", ".xlsx", "active/300-pine/analysis.xlsx"),
            _record("photo-a.jpg", ".jpg", "media/400-elm/photos/photo-a.jpg"),
            _record("photo-b.jpg", ".jpg", "media/400-elm/photos/photo-b.jpg"),
        ],
    }


def test_discovers_assignment_folders_from_metadata_only() -> None:
    candidates = discover_assignments(_manifest())
    by_folder = {candidate.assignment_folder: candidate for candidate in candidates}

    complete = by_folder["assignments/100-main"]
    assert complete.pdf_count == 1
    assert complete.word_count == 1
    assert complete.photo_count == 1
    assert complete.map_image_count == 1
    assert complete.confidence_label == "high"
    assert complete.estimated_completeness_score == 85


def test_identifies_archived_report() -> None:
    candidate = {item.assignment_folder: item for item in discover_assignments(_manifest())}["archive/200-oak"]

    assert candidate.pdf_count == 1
    assert candidate.heuristic == "PDF only = Archived report"
    assert candidate.confidence_label == "medium"


def test_identifies_work_in_progress() -> None:
    candidate = {item.assignment_folder: item for item in discover_assignments(_manifest())}["active/300-pine"]

    assert candidate.word_count == 1
    assert candidate.excel_count == 1
    assert candidate.heuristic == "DOCX + XLSX = Work in progress"


def test_identifies_media_folder() -> None:
    candidate = {item.assignment_folder: item for item in discover_assignments(_manifest())}["media/400-elm"]

    assert candidate.photo_count == 2
    assert candidate.heuristic == "Images only = Media folder"
    assert candidate.confidence_label == "low"
