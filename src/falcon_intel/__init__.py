"""Falcon Intelligence framework package."""

from falcon_intel.core import AppProfile
from falcon_intel.manifest import ScanManifest, create_scan_manifest, save_scan_manifest
from falcon_intel.scanner import FileMetadata, scan_metadata
from falcon_intel.search import (
    ManifestSearchQuery,
    ManifestSearchResult,
    ManifestSummary,
    is_likely_report_candidate,
    load_manifest,
    search_manifest,
    search_manifest_files,
    summarize_results,
)

__all__ = [
    "AppProfile",
    "FileMetadata",
    "ScanManifest",
    "ManifestSearchQuery",
    "ManifestSearchResult",
    "ManifestSummary",
    "create_scan_manifest",
    "is_likely_report_candidate",
    "load_manifest",
    "save_scan_manifest",
    "search_manifest",
    "search_manifest_files",
    "scan_metadata",
    "summarize_results",
]
