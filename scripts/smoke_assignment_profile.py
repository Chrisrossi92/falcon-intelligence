"""Dependency-free smoke validation for metadata-only assignment profiles."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.manifest import create_scan_manifest
from falcon_intel.profile import build_assignment_profile, save_assignment_profile
from falcon_intel.scanner import scan_metadata


def main() -> None:
    with TemporaryDirectory() as workspace:
        workspace_path = Path(workspace)
        selected_root = workspace_path / "selected"
        assignment = selected_root / "assignments" / "100-main"
        photos = assignment / "photos"
        workbooks = assignment / "workbooks"
        photos.mkdir(parents=True)
        workbooks.mkdir(parents=True)
        (assignment / "final-report.pdf").write_bytes(b"synthetic")
        (assignment / "draft-report.docx").write_bytes(b"synthetic")
        (workbooks / "analysis.xlsx").write_bytes(b"synthetic")
        (photos / "front.jpg").write_bytes(b"synthetic")

        manifest = create_scan_manifest(scan_metadata(selected_root), "Synthetic Selection")
        profile = build_assignment_profile(manifest.to_dict(), "assignments/100-main")
        payload = profile.to_dict()
        assert payload["assignment_folder"] == "assignments/100-main"
        assert payload["heuristic_label"] == "high-confidence-assignment"
        assert payload["file_groups"]["report_candidates"][0]["file_name"] == "draft-report.docx"
        assert "text" not in json.dumps(payload).lower()

        output_path = save_assignment_profile(
            profile,
            output_dir=workspace_path / "data" / "profiles",
            file_name="profile.json",
        )
        assert output_path.exists()

    print("assignment profile smoke validation passed")


if __name__ == "__main__":
    main()
