"""Dependency-free smoke validation for local metadata manifests."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.manifest import create_scan_manifest, save_scan_manifest
from falcon_intel.scanner import scan_metadata


def main() -> None:
    with TemporaryDirectory() as workspace:
        workspace_path = Path(workspace)
        selected_root = workspace_path / "selected"
        selected_root.mkdir()
        (selected_root / "synthetic.pdf").write_bytes(b"synthetic")
        (selected_root / "synthetic.jpg").write_bytes(b"synthetic")

        manifest = create_scan_manifest(scan_metadata(selected_root), "Synthetic Selection")
        payload = manifest.to_dict()
        assert "absolute_root_path" not in payload
        assert payload["file_count"] == 2
        assert payload["counts_by_extension"] == {".jpg": 1, ".pdf": 1}
        assert payload["supported_future_indexing_count"] == 1

        output_path = save_scan_manifest(
            manifest,
            output_dir=workspace_path / "data" / "manifests",
            file_name="scan.json",
        )
        saved_payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert "absolute_root_path" not in saved_payload
        assert "synthetic" in saved_payload["files"][0]["file_name"]

    print("manifest smoke validation passed")


if __name__ == "__main__":
    main()
