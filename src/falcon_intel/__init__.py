"""Falcon Intelligence framework package."""

from falcon_intel.core import AppProfile
from falcon_intel.discovery import AssignmentCandidate, discover_assignments
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    FirmIntelligenceMatchResult,
    IntelligenceMatch,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)
from falcon_intel.manifest import (
    SavedManifestInfo,
    ScanManifest,
    create_scan_manifest,
    latest_manifest_path,
    list_saved_manifests,
    save_scan_manifest,
)
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
    "FakeOrder",
    "FirmIntelligenceMatchResult",
    "IntelligenceMatch",
    "SavedManifestInfo",
    "ScanManifest",
    "ManifestSearchQuery",
    "ManifestSearchResult",
    "ManifestSummary",
    "build_assignment_profile",
    "create_scan_manifest",
    "discover_assignments",
    "is_likely_report_candidate",
    "latest_manifest_path",
    "list_saved_manifests",
    "load_manifest",
    "load_synthetic_verified_intelligence",
    "match_firm_intelligence",
    "save_assignment_profile",
    "save_scan_manifest",
    "search_manifest",
    "search_manifest_files",
    "scan_metadata",
    "summarize_results",
]
