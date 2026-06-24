"""Dependency-free smoke validation for metadata-only assignment discovery."""

from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.discovery import discover_assignments
from falcon_intel.manifest import create_scan_manifest
from falcon_intel.scanner import scan_metadata


def main() -> None:
    with TemporaryDirectory() as workspace:
        selected_root = Path(workspace) / "selected"
        assignment = selected_root / "assignments" / "100-main"
        photos = assignment / "photos"
        maps = assignment / "maps"
        photos.mkdir(parents=True)
        maps.mkdir(parents=True)
        (assignment / "final-report.pdf").write_bytes(b"synthetic")
        (assignment / "draft-report.docx").write_bytes(b"synthetic")
        (photos / "front.jpg").write_bytes(b"synthetic")
        (maps / "site-map.png").write_bytes(b"synthetic")

        manifest = create_scan_manifest(scan_metadata(selected_root), "Synthetic Selection")
        candidates = discover_assignments(manifest.to_dict())
        assert len(candidates) == 1
        assert candidates[0].assignment_folder == "assignments/100-main"
        assert candidates[0].confidence_label == "high"
        assert candidates[0].document_count == 2
        assert candidates[0].photo_count == 1
        assert candidates[0].map_image_count == 1

    print("assignment discovery smoke validation passed")


if __name__ == "__main__":
    main()
