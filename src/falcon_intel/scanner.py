"""Metadata-only folder scanner for user-selected roots."""

from dataclasses import dataclass
from datetime import UTC, datetime
import os
from pathlib import Path
from typing import Iterable


SUPPORTED_FUTURE_INDEXING_SUFFIXES = {
    ".docx",
    ".pdf",
    ".txt",
    ".xls",
    ".xlsx",
}


@dataclass(frozen=True)
class FileMetadata:
    """Filesystem metadata collected without reading file contents."""

    file_name: str
    file_extension: str
    relative_path: str
    file_size: int
    modified_timestamp: str
    supported_for_future_indexing: bool


def scan_metadata(root_folder: str | Path) -> list[FileMetadata]:
    """Scan a user-selected folder and return file metadata only."""

    root_path = Path(root_folder)
    if not str(root_path):
        raise ValueError("An explicit root folder is required.")
    if root_path.is_symlink():
        raise ValueError("Root folder cannot be a symlink.")

    resolved_root = root_path.resolve(strict=True)
    if not resolved_root.is_dir():
        raise ValueError("Root folder must be an existing directory.")

    return sorted(
        _iter_metadata(resolved_root, resolved_root),
        key=lambda item: item.relative_path.lower(),
    )


def _iter_metadata(current_folder: Path, root_folder: Path) -> Iterable[FileMetadata]:
    with os.scandir(current_folder) as entries:
        for entry in entries:
            if entry.is_symlink():
                continue

            child = Path(entry.path)
            if entry.is_dir(follow_symlinks=False):
                yield from _iter_metadata(child, root_folder)
                continue

            if not entry.is_file(follow_symlinks=False):
                continue

            child.relative_to(root_folder)
            stats = entry.stat(follow_symlinks=False)
            extension = child.suffix.lower()
            yield FileMetadata(
                file_name=child.name,
                file_extension=extension,
                relative_path=child.relative_to(root_folder).as_posix(),
                file_size=stats.st_size,
                modified_timestamp=datetime.fromtimestamp(stats.st_mtime, UTC).isoformat(),
                supported_for_future_indexing=extension in SUPPORTED_FUTURE_INDEXING_SUFFIXES,
            )
