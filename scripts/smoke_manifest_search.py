"""Dependency-free smoke validation for metadata-only manifest search."""

from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.manifest import create_scan_manifest, save_scan_manifest
from falcon_intel.scanner import scan_metadata
from falcon_intel.search import (
    ManifestSearchQuery,
    search_manifest_files,
    summarize_results,
)


def main() -> None:
    with TemporaryDirectory() as workspace:
        workspace_path = Path(workspace)
        selected_root = workspace_path / "selected"
        reports = selected_root / "reports"
        reports.mkdir(parents=True)
        (reports / "synthetic-report.pdf").write_bytes(b"synthetic")
        (selected_root / "photo.jpg").write_bytes(b"synthetic")

        manifest = create_scan_manifest(scan_metadata(selected_root), "Synthetic Selection")
        manifest_path = save_scan_manifest(
            manifest,
            output_dir=workspace_path / "data" / "manifests",
            file_name="scan.json",
        )

        results = search_manifest_files(
            [manifest_path],
            ManifestSearchQuery(file_name_keyword="report", extension=".pdf"),
        )
        assert len(results) == 1
        assert results[0].relative_path == "reports/synthetic-report.pdf"
        assert results[0].absolute_root_path is None

        summary = summarize_results(search_manifest_files([manifest_path]))
        assert summary.total_files == 2
        assert summary.supported_future_indexing_files == 1
        assert summary.likely_report_candidates == 1

    print("manifest search smoke validation passed")


if __name__ == "__main__":
    main()
