from falcon_intel.search import (
    ManifestSearchQuery,
    is_likely_report_candidate,
    search_manifest,
    summarize_results,
)


def _manifest(include_absolute_root_path: bool = False) -> dict[str, object]:
    manifest: dict[str, object] = {
        "manifest_version": "1",
        "scan_timestamp": "2026-06-24T12:00:00+00:00",
        "selected_root_label": "Synthetic Selection",
        "file_count": 3,
        "counts_by_extension": {".docx": 1, ".jpg": 1, ".pdf": 1},
        "supported_future_indexing_count": 2,
        "files": [
            {
                "file_name": "industrial-appraisal-report.pdf",
                "file_extension": ".pdf",
                "relative_path": "reports/industrial-appraisal-report.pdf",
                "file_size": 100,
                "modified_timestamp": "2026-06-20T12:00:00+00:00",
                "supported_for_future_indexing": True,
            },
            {
                "file_name": "workbook.xlsx",
                "file_extension": ".xlsx",
                "relative_path": "analysis/workbook.xlsx",
                "file_size": 50,
                "modified_timestamp": "2026-06-21T12:00:00+00:00",
                "supported_for_future_indexing": True,
            },
            {
                "file_name": "photo.jpg",
                "file_extension": ".jpg",
                "relative_path": "photos/photo.jpg",
                "file_size": 25,
                "modified_timestamp": "2026-06-22T12:00:00+00:00",
                "supported_for_future_indexing": False,
            },
        ],
    }
    if include_absolute_root_path:
        manifest["absolute_root_path"] = "C:/Synthetic/Selected"
    return manifest


def test_search_by_file_name_keyword() -> None:
    results = search_manifest(_manifest(), ManifestSearchQuery(file_name_keyword="appraisal"))

    assert len(results) == 1
    assert results[0].file_name == "industrial-appraisal-report.pdf"
    assert "absolute_root_path" not in results[0].to_dict()


def test_search_by_extension_and_supported_flag() -> None:
    results = search_manifest(
        _manifest(),
        ManifestSearchQuery(extension="xlsx", supported_for_future_indexing=True),
    )

    assert [result.relative_path for result in results] == ["analysis/workbook.xlsx"]


def test_search_by_relative_path_keyword() -> None:
    results = search_manifest(_manifest(), ManifestSearchQuery(relative_path_keyword="photos"))

    assert [result.file_name for result in results] == ["photo.jpg"]


def test_search_by_modified_date_range() -> None:
    results = search_manifest(
        _manifest(),
        ManifestSearchQuery(
            modified_from="2026-06-21T00:00:00+00:00",
            modified_to="2026-06-21T23:59:59+00:00",
        ),
    )

    assert [result.file_name for result in results] == ["workbook.xlsx"]


def test_absolute_root_path_only_returned_when_present() -> None:
    results_without_path = search_manifest(_manifest())
    results_with_path = search_manifest(_manifest(include_absolute_root_path=True))

    assert all(result.absolute_root_path is None for result in results_without_path)
    assert results_with_path[0].absolute_root_path == "C:/Synthetic/Selected"


def test_summary_helpers_use_metadata_only() -> None:
    results = search_manifest(_manifest())
    summary = summarize_results(results)

    assert summary.total_files == 3
    assert summary.supported_future_indexing_files == 2
    assert summary.top_extensions == [(".docx", 1), (".jpg", 1), (".pdf", 1)]
    assert summary.likely_report_candidates == 1
    assert is_likely_report_candidate(results[0]) is True
    assert is_likely_report_candidate(results[1]) is False
