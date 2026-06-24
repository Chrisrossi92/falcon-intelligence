"""Metadata-only search over local scan manifests."""

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Iterable


REPORT_CANDIDATE_EXTENSIONS = {".docx", ".pdf"}
REPORT_CANDIDATE_KEYWORDS = {
    "appraisal",
    "narrative",
    "report",
    "valuation",
}


@dataclass(frozen=True)
class ManifestSearchQuery:
    """Filters for metadata-only manifest search."""

    file_name_keyword: str | None = None
    extension: str | None = None
    relative_path_keyword: str | None = None
    supported_for_future_indexing: bool | None = None
    modified_from: str | datetime | None = None
    modified_to: str | datetime | None = None


@dataclass(frozen=True)
class ManifestSearchResult:
    """Safe metadata-only search result."""

    selected_root_label: str
    scan_timestamp: str
    file_name: str
    file_extension: str
    relative_path: str
    file_size: int
    modified_timestamp: str
    supported_for_future_indexing: bool
    absolute_root_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "selected_root_label": self.selected_root_label,
            "scan_timestamp": self.scan_timestamp,
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "relative_path": self.relative_path,
            "file_size": self.file_size,
            "modified_timestamp": self.modified_timestamp,
            "supported_for_future_indexing": self.supported_for_future_indexing,
        }
        if self.absolute_root_path is not None:
            payload["absolute_root_path"] = self.absolute_root_path
        return payload


@dataclass(frozen=True)
class ManifestSummary:
    """Metadata-only summary of manifest search records."""

    total_files: int
    supported_future_indexing_files: int
    top_extensions: list[tuple[str, int]]
    likely_report_candidates: int


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load one scan manifest JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def search_manifest(
    manifest: dict[str, Any],
    query: ManifestSearchQuery | None = None,
) -> list[ManifestSearchResult]:
    """Search one manifest by metadata fields only."""

    active_query = query or ManifestSearchQuery()
    return [
        result
        for result in _iter_manifest_results(manifest)
        if _matches_query(result, active_query)
    ]


def search_manifest_files(
    manifest_paths: Iterable[str | Path],
    query: ManifestSearchQuery | None = None,
) -> list[ManifestSearchResult]:
    """Search multiple local manifest JSON files."""

    results: list[ManifestSearchResult] = []
    for manifest_path in manifest_paths:
        results.extend(search_manifest(load_manifest(manifest_path), query))
    return results


def summarize_results(results: Iterable[ManifestSearchResult]) -> ManifestSummary:
    """Summarize metadata-only search results."""

    result_list = list(results)
    extension_counts: dict[str, int] = {}
    supported_count = 0
    candidate_count = 0
    for result in result_list:
        extension_counts[result.file_extension] = extension_counts.get(result.file_extension, 0) + 1
        if result.supported_for_future_indexing:
            supported_count += 1
        if is_likely_report_candidate(result):
            candidate_count += 1

    return ManifestSummary(
        total_files=len(result_list),
        supported_future_indexing_files=supported_count,
        top_extensions=sorted(
            extension_counts.items(),
            key=lambda item: (-item[1], item[0]),
        ),
        likely_report_candidates=candidate_count,
    )


def is_likely_report_candidate(result: ManifestSearchResult) -> bool:
    """Estimate report candidates from extension and metadata text only."""

    if result.file_extension not in REPORT_CANDIDATE_EXTENSIONS:
        return False
    searchable_text = f"{result.file_name} {result.relative_path}".lower()
    return any(keyword in searchable_text for keyword in REPORT_CANDIDATE_KEYWORDS)


def _iter_manifest_results(manifest: dict[str, Any]) -> Iterable[ManifestSearchResult]:
    absolute_root_path = manifest.get("absolute_root_path")
    for file_record in manifest.get("files", []):
        yield ManifestSearchResult(
            selected_root_label=str(manifest["selected_root_label"]),
            scan_timestamp=str(manifest["scan_timestamp"]),
            file_name=str(file_record["file_name"]),
            file_extension=str(file_record["file_extension"]).lower(),
            relative_path=str(file_record["relative_path"]),
            file_size=int(file_record["file_size"]),
            modified_timestamp=str(file_record["modified_timestamp"]),
            supported_for_future_indexing=bool(file_record["supported_for_future_indexing"]),
            absolute_root_path=str(absolute_root_path) if absolute_root_path is not None else None,
        )


def _matches_query(result: ManifestSearchResult, query: ManifestSearchQuery) -> bool:
    if query.file_name_keyword and query.file_name_keyword.lower() not in result.file_name.lower():
        return False
    if query.extension and _normalize_extension(query.extension) != result.file_extension:
        return False
    if query.relative_path_keyword and query.relative_path_keyword.lower() not in result.relative_path.lower():
        return False
    if (
        query.supported_for_future_indexing is not None
        and query.supported_for_future_indexing != result.supported_for_future_indexing
    ):
        return False

    modified_timestamp = _parse_timestamp(result.modified_timestamp)
    modified_from = _optional_timestamp(query.modified_from)
    modified_to = _optional_timestamp(query.modified_to)
    if modified_from is not None and modified_timestamp < modified_from:
        return False
    if modified_to is not None and modified_timestamp > modified_to:
        return False

    return True


def _normalize_extension(extension: str) -> str:
    normalized = extension.lower().strip()
    if not normalized.startswith("."):
        normalized = f".{normalized}"
    return normalized


def _optional_timestamp(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return _parse_timestamp(value)


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
