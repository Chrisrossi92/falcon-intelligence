import builtins
from pathlib import Path

import pytest

from falcon_intel.scanner import scan_metadata


def test_scan_metadata_requires_existing_root(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        scan_metadata(missing_root)


def test_scan_metadata_returns_metadata_only(tmp_path: Path) -> None:
    reports = tmp_path / "selected"
    nested = reports / "nested"
    nested.mkdir(parents=True)
    pdf_path = nested / "report.pdf"
    pdf_path.write_bytes(b"synthetic")
    image_path = reports / "photo.jpg"
    image_path.write_bytes(b"synthetic")

    results = scan_metadata(reports)

    assert [item.relative_path for item in results] == ["nested/report.pdf", "photo.jpg"]
    pdf_metadata = results[0]
    assert pdf_metadata.file_name == "report.pdf"
    assert pdf_metadata.file_extension == ".pdf"
    assert pdf_metadata.file_size == len(b"synthetic")
    assert pdf_metadata.supported_for_future_indexing is True
    assert not hasattr(pdf_metadata, "text")
    assert results[1].supported_for_future_indexing is False


def test_scan_metadata_does_not_open_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    selected_root = tmp_path / "selected"
    selected_root.mkdir()
    (selected_root / "report.docx").write_bytes(b"synthetic")

    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("scanner must not open file contents")

    monkeypatch.setattr(builtins, "open", fail_open)

    results = scan_metadata(selected_root)

    assert results[0].file_name == "report.docx"


def test_scan_metadata_skips_symlinks(tmp_path: Path) -> None:
    selected_root = tmp_path / "selected"
    selected_root.mkdir()
    target = tmp_path / "outside.pdf"
    target.write_bytes(b"synthetic")
    link = selected_root / "outside.pdf"

    try:
        link.symlink_to(target)
    except OSError:
        return

    assert scan_metadata(selected_root) == []
