"""Local JSON scan manifests for metadata-only prototype use."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from falcon_intel.scanner import FileMetadata


DEFAULT_MANIFEST_DIR = Path("data") / "manifests"


@dataclass(frozen=True)
class ScanManifest:
    """Metadata-only scan manifest."""

    manifest_version: str
    scan_timestamp: str
    selected_root_label: str
    file_count: int
    counts_by_extension: dict[str, int]
    supported_future_indexing_count: int
    files: list[dict[str, Any]]
    absolute_root_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.absolute_root_path is None:
            payload.pop("absolute_root_path")
        return payload


@dataclass(frozen=True)
class SavedManifestInfo:
    """Summary of one saved local scan manifest."""

    path: str
    filename: str
    scan_timestamp: str
    selected_root_label: str
    file_count: int
    supported_future_indexing_count: int


def create_scan_manifest(
    scanner_results: Iterable[FileMetadata],
    selected_root_label: str,
    *,
    selected_root_path: str | Path | None = None,
    include_absolute_root_path: bool = False,
) -> ScanManifest:
    """Create a metadata-only manifest from scanner results."""

    if not selected_root_label.strip():
        raise ValueError("A selected root label is required.")
    if include_absolute_root_path and selected_root_path is None:
        raise ValueError("selected_root_path is required when absolute paths are included.")

    files = [asdict(result) for result in scanner_results]
    counts_by_extension: dict[str, int] = {}
    supported_count = 0
    for file_record in files:
        extension = str(file_record["file_extension"])
        counts_by_extension[extension] = counts_by_extension.get(extension, 0) + 1
        if bool(file_record["supported_for_future_indexing"]):
            supported_count += 1

    absolute_root_path = None
    if include_absolute_root_path:
        absolute_root_path = str(Path(selected_root_path).resolve(strict=True))

    return ScanManifest(
        manifest_version="1",
        scan_timestamp=datetime.now(UTC).isoformat(),
        selected_root_label=selected_root_label,
        file_count=len(files),
        counts_by_extension=dict(sorted(counts_by_extension.items())),
        supported_future_indexing_count=supported_count,
        files=files,
        absolute_root_path=absolute_root_path,
    )


def save_scan_manifest(
    manifest: ScanManifest,
    *,
    output_dir: str | Path = DEFAULT_MANIFEST_DIR,
    file_name: str | None = None,
) -> Path:
    """Save a manifest under an ignored local manifest directory."""

    manifest_dir = Path(output_dir)
    _require_manifest_dir(manifest_dir)
    manifest_dir.mkdir(parents=True, exist_ok=True)

    output_name = file_name or f"scan-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}.json"
    if Path(output_name).name != output_name or not output_name.endswith(".json"):
        raise ValueError("Manifest file name must be a local .json file name.")

    output_path = manifest_dir / output_name
    output_path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def list_saved_manifests(
    manifest_dir: str | Path = DEFAULT_MANIFEST_DIR,
) -> list[SavedManifestInfo]:
    """List saved local manifests without reading source files."""

    manifest_path = Path(manifest_dir)
    _require_manifest_dir(manifest_path)
    if not manifest_path.exists():
        return []

    manifests: list[SavedManifestInfo] = []
    for path in sorted(manifest_path.glob("*.json"), key=lambda item: item.stat().st_ctime, reverse=True):
        payload = json.loads(path.read_text(encoding="utf-8"))
        manifests.append(
            SavedManifestInfo(
                path=str(path),
                filename=path.name,
                scan_timestamp=str(payload.get("scan_timestamp", "")),
                selected_root_label=str(payload.get("selected_root_label", "")),
                file_count=int(payload.get("file_count", 0)),
                supported_future_indexing_count=int(payload.get("supported_future_indexing_count", 0)),
            )
        )
    return manifests


def latest_manifest_path(
    manifest_dir: str | Path = DEFAULT_MANIFEST_DIR,
) -> Path:
    """Return the most recently created local manifest path."""

    manifest_path = Path(manifest_dir)
    _require_manifest_dir(manifest_path)
    manifests = sorted(manifest_path.glob("*.json"), key=lambda item: item.stat().st_ctime, reverse=True)
    if not manifests:
        raise FileNotFoundError("No saved manifests found under data/manifests/.")
    return manifests[0]


def _require_manifest_dir(output_dir: Path) -> None:
    parts = [part.lower() for part in output_dir.parts]
    if len(parts) < 2 or parts[-2:] != ["data", "manifests"]:
        raise ValueError("Scan manifests may only be saved under data/manifests/.")
