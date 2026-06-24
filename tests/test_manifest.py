import json
from pathlib import Path

import pytest

from falcon_intel.manifest import create_scan_manifest, save_scan_manifest
from falcon_intel.scanner import scan_metadata


def test_create_manifest_excludes_absolute_root_by_default(tmp_path: Path) -> None:
    selected_root = tmp_path / "selected"
    selected_root.mkdir()
    (selected_root / "report.pdf").write_bytes(b"synthetic")
    (selected_root / "image.jpg").write_bytes(b"synthetic")

    manifest = create_scan_manifest(scan_metadata(selected_root), "Selected Folder")
    payload = manifest.to_dict()

    assert "absolute_root_path" not in payload
    assert payload["selected_root_label"] == "Selected Folder"
    assert payload["file_count"] == 2
    assert payload["counts_by_extension"] == {".jpg": 1, ".pdf": 1}
    assert payload["supported_future_indexing_count"] == 1
    assert "text" not in json.dumps(payload).lower()


def test_create_manifest_includes_absolute_root_when_requested(tmp_path: Path) -> None:
    selected_root = tmp_path / "selected"
    selected_root.mkdir()

    manifest = create_scan_manifest(
        scan_metadata(selected_root),
        "Selected Folder",
        selected_root_path=selected_root,
        include_absolute_root_path=True,
    )

    assert manifest.to_dict()["absolute_root_path"] == str(selected_root.resolve())


def test_create_manifest_requires_explicit_opt_in_for_absolute_path(tmp_path: Path) -> None:
    selected_root = tmp_path / "selected"
    selected_root.mkdir()

    with pytest.raises(ValueError):
        create_scan_manifest(
            scan_metadata(selected_root),
            "Selected Folder",
            include_absolute_root_path=True,
        )


def test_save_manifest_requires_ignored_manifest_directory(tmp_path: Path) -> None:
    selected_root = tmp_path / "selected"
    selected_root.mkdir()
    manifest = create_scan_manifest(scan_metadata(selected_root), "Selected Folder")

    with pytest.raises(ValueError):
        save_scan_manifest(manifest, output_dir=tmp_path / "exports")


def test_save_manifest_writes_json_under_data_manifests(tmp_path: Path) -> None:
    selected_root = tmp_path / "selected"
    selected_root.mkdir()
    (selected_root / "report.docx").write_bytes(b"synthetic")
    manifest = create_scan_manifest(scan_metadata(selected_root), "Selected Folder")

    output_path = save_scan_manifest(
        manifest,
        output_dir=tmp_path / "data" / "manifests",
        file_name="scan.json",
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert output_path.name == "scan.json"
    assert payload["selected_root_label"] == "Selected Folder"
    assert payload["supported_future_indexing_count"] == 1
    assert "absolute_root_path" not in payload
