"""Falcon Intelligence framework package."""

from falcon_intel.core import AppProfile
from falcon_intel.discovery import AssignmentCandidate, discover_assignments
from falcon_intel.manifest import ScanManifest, create_scan_manifest, save_scan_manifest
from falcon_intel.profile import (
    AssignmentProfile,
    build_assignment_profile,
    save_assignment_profile,
)
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
    "AssignmentCandidate",
    "AssignmentProfile",
    "FileMetadata",
    "ScanManifest",
    "ManifestSearchQuery",
    "ManifestSearchResult",
    "ManifestSummary",
    "build_assignment_profile",
    "create_scan_manifest",
    "discover_assignments",
    "is_likely_report_candidate",
    "load_manifest",
    "save_assignment_profile",
    "save_scan_manifest",
    "search_manifest",
    "search_manifest_files",
    "scan_metadata",
    "summarize_results",
]
