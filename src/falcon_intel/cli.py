"""Command-line interface for local metadata-only prototype workflows."""

from argparse import ArgumentParser, Namespace
import json
from pathlib import Path
from typing import Any

from falcon_intel.discovery import AssignmentCandidate, discover_assignments
from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)
from falcon_intel.manifest import (
    create_scan_manifest,
    latest_manifest_path,
    list_saved_manifests,
    save_scan_manifest,
)
from falcon_intel.profile import build_assignment_profile, save_assignment_profile
from falcon_intel.property_library import (
    PropertyLibraryFilters,
    build_demo_property_library_workspace,
)
from falcon_intel.report_registry import build_demo_subject_profile
from falcon_intel.scanner import scan_metadata
from falcon_intel.search import (
    ManifestSearchQuery,
    load_manifest,
    search_manifest,
    summarize_results,
)


DEFAULT_SYNTHETIC_INTELLIGENCE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "synthetic_verified_intelligence"
    / "verified-intelligence.json"
)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    payload = args.handler(args)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="falcon-intel",
        description="Falcon Intelligence metadata-only local prototype CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a selected folder into a local manifest.")
    scan_parser.add_argument("--root", required=True, help="Explicit folder to scan.")
    scan_parser.add_argument("--label", required=True, help="Friendly label for the selected folder.")
    scan_parser.add_argument(
        "--include-absolute-paths",
        action="store_true",
        help="Include the absolute selected root path in the manifest.",
    )
    scan_parser.set_defaults(handler=_handle_scan)

    manifests_parser = subparsers.add_parser(
        "manifests",
        help="List saved manifests under data/manifests/.",
    )
    manifests_parser.set_defaults(handler=_handle_manifests)

    search_parser = subparsers.add_parser("search", help="Search one manifest by metadata only.")
    _add_manifest_selector(search_parser)
    search_parser.add_argument("--name", help="File name keyword.")
    search_parser.add_argument("--extension", help="File extension filter, such as pdf or .pdf.")
    search_parser.add_argument("--path", dest="path_keyword", help="Relative path keyword.")
    search_parser.add_argument(
        "--supported-only",
        action="store_true",
        help="Return only files marked supported for future indexing.",
    )
    search_parser.set_defaults(handler=_handle_search)

    summary_parser = subparsers.add_parser("summary", help="Summarize one manifest by metadata only.")
    _add_manifest_selector(summary_parser)
    summary_parser.set_defaults(handler=_handle_summary)

    discover_parser = subparsers.add_parser(
        "discover",
        help="Discover probable assignment folders from one manifest.",
    )
    _add_manifest_selector(discover_parser)
    discover_parser.add_argument(
        "--min-confidence",
        type=int,
        default=0,
        help="Minimum completeness score from 0 to 100.",
    )
    discover_parser.add_argument(
        "--label",
        choices=[
            "high-confidence-assignment",
            "archived-report",
            "work-in-progress",
            "media-folder",
        ],
        help="Filter by assignment discovery heuristic label.",
    )
    discover_parser.add_argument("--limit", type=int, help="Maximum candidates to return.")
    discover_parser.set_defaults(handler=_handle_discover)

    profile_parser = subparsers.add_parser(
        "profile",
        help="Build one metadata-only assignment profile from a manifest.",
    )
    _add_manifest_selector(profile_parser)
    profile_parser.add_argument(
        "--assignment-folder",
        required=True,
        help="Discovered assignment folder to profile.",
    )
    profile_parser.add_argument(
        "--save",
        action="store_true",
        help="Save profile JSON under ignored data/profiles/.",
    )
    profile_parser.set_defaults(handler=_handle_profile)

    intelligence_card_parser = subparsers.add_parser(
        "intelligence-card",
        help="Preview a synthetic Firm Intelligence Found card for a fake Falcon order.",
    )
    intelligence_card_parser.add_argument("--address", required=True, help="Fake order property address.")
    intelligence_card_parser.add_argument("--city", required=True, help="Fake order city.")
    intelligence_card_parser.add_argument("--state", required=True, help="Fake order state.")
    intelligence_card_parser.add_argument("--property-type", required=True, help="Fake order property type.")
    intelligence_card_parser.add_argument(
        "--building-size-sf",
        required=True,
        type=int,
        help="Fake order building size in square feet.",
    )
    intelligence_card_parser.add_argument("--client", required=True, help="Fake order client.")
    intelligence_card_parser.set_defaults(handler=_handle_intelligence_card)

    subject_profile_parser = subparsers.add_parser(
        "subject-profile",
        help="Preview the synthetic Subject Profile and Report Field Registry workflow.",
    )
    subject_profile_parser.add_argument(
        "--approve",
        action="append",
        default=[],
        help="Mark a value-bearing report field approved in the preview.",
    )
    subject_profile_parser.add_argument(
        "--lock",
        action="append",
        default=[],
        help="Mark a value-bearing report field locked in the preview.",
    )
    subject_profile_parser.set_defaults(handler=_handle_subject_profile)

    property_library_parser = subparsers.add_parser(
        "property-library",
        help="Preview the synthetic Property Library and Controlled Comp Vault workspace.",
    )
    property_library_parser.add_argument("--query", help="Search across property, evidence, and report usage fields.")
    property_library_parser.add_argument("--property-type", help="Filter by property type.")
    property_library_parser.add_argument("--county", help="Filter by county.")
    property_library_parser.add_argument("--comp-role", help="Filter by report usage role.")
    property_library_parser.add_argument("--report-usage", help="Filter by synthetic order number.")
    property_library_parser.add_argument("--date-from", help="Filter evidence or report usage dates from YYYY-MM-DD.")
    property_library_parser.add_argument("--date-to", help="Filter evidence or report usage dates through YYYY-MM-DD.")
    property_library_parser.add_argument("--min-size-sf", type=int, help="Minimum building size in square feet.")
    property_library_parser.add_argument("--max-size-sf", type=int, help="Maximum building size in square feet.")
    property_library_parser.add_argument("--verification-status", help="Filter by verification status.")
    property_library_parser.add_argument("--selected-property-id", help="Property ID to show in the details drawer.")
    property_library_parser.set_defaults(handler=_handle_property_library)

    return parser


def _add_manifest_selector(parser: ArgumentParser) -> None:
    manifest_group = parser.add_mutually_exclusive_group(required=True)
    manifest_group.add_argument("--manifest", help="Manifest JSON path.")
    manifest_group.add_argument(
        "--latest",
        action="store_true",
        help="Use the most recently created manifest under data/manifests/.",
    )


def _handle_scan(args: Namespace) -> dict[str, Any]:
    root_path = Path(args.root)
    scanner_results = scan_metadata(root_path)
    manifest = create_scan_manifest(
        scanner_results,
        args.label,
        selected_root_path=root_path if args.include_absolute_paths else None,
        include_absolute_root_path=args.include_absolute_paths,
    )
    manifest_path = save_scan_manifest(manifest)
    return {
        "manifest_path": str(manifest_path),
        "file_count": manifest.file_count,
        "supported_future_indexing_count": manifest.supported_future_indexing_count,
        "counts_by_extension": manifest.counts_by_extension,
        "absolute_paths_included": args.include_absolute_paths,
    }


def _handle_manifests(args: Namespace) -> dict[str, Any]:
    manifests = list_saved_manifests()
    return {
        "manifest_count": len(manifests),
        "manifests": [
            {
                "filename": manifest.filename,
                "path": manifest.path,
                "scan_timestamp": manifest.scan_timestamp,
                "label": manifest.selected_root_label,
                "total_files": manifest.file_count,
                "supported_future_indexing_count": manifest.supported_future_indexing_count,
            }
            for manifest in manifests
        ],
    }


def _handle_search(args: Namespace) -> dict[str, Any]:
    manifest_path = _resolve_manifest_path(args)
    query = ManifestSearchQuery(
        file_name_keyword=args.name,
        extension=args.extension,
        relative_path_keyword=args.path_keyword,
        supported_for_future_indexing=True if args.supported_only else None,
    )
    results = search_manifest(load_manifest(manifest_path), query)
    return {
        "manifest_path": str(manifest_path),
        "result_count": len(results),
        "results": [result.to_dict() for result in results],
    }


def _handle_summary(args: Namespace) -> dict[str, Any]:
    manifest_path = _resolve_manifest_path(args)
    results = search_manifest(load_manifest(manifest_path))
    summary = summarize_results(results)
    return {
        "manifest_path": str(manifest_path),
        "total_files": summary.total_files,
        "extension_counts": dict(summary.top_extensions),
        "supported_future_indexing_files": summary.supported_future_indexing_files,
        "likely_report_candidates": summary.likely_report_candidates,
    }


def _handle_discover(args: Namespace) -> dict[str, Any]:
    if args.min_confidence < 0 or args.min_confidence > 100:
        raise ValueError("--min-confidence must be between 0 and 100.")
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be at least 1.")

    manifest_path = _resolve_manifest_path(args)
    candidates = [
        candidate
        for candidate in discover_assignments(load_manifest(manifest_path))
        if candidate.estimated_completeness_score >= args.min_confidence
    ]
    if args.label is not None:
        candidates = [
            candidate
            for candidate in candidates
            if _heuristic_label(candidate) == args.label
        ]
    if args.limit is not None:
        candidates = candidates[: args.limit]

    return {
        "manifest_path": str(manifest_path),
        "candidate_count": len(candidates),
        "candidates": [_candidate_payload(candidate) for candidate in candidates],
    }


def _candidate_payload(candidate: AssignmentCandidate) -> dict[str, Any]:
    return {
        "assignment_folder": candidate.assignment_folder,
        "heuristic_label": _heuristic_label(candidate),
        "completeness_score": candidate.estimated_completeness_score,
        "confidence": candidate.confidence_label,
        "total_files": candidate.total_file_count,
        "pdf_count": candidate.pdf_count,
        "word_count": candidate.word_count,
        "excel_count": candidate.excel_count,
        "photo_count": candidate.photo_count,
        "map_image_count": candidate.map_image_count,
    }


def _heuristic_label(candidate: AssignmentCandidate) -> str:
    if candidate.heuristic.startswith("PDF + DOCX + Photos"):
        return "high-confidence-assignment"
    if candidate.heuristic.startswith("PDF only"):
        return "archived-report"
    if candidate.heuristic.startswith("DOCX + XLSX"):
        return "work-in-progress"
    if candidate.heuristic.startswith("Images only"):
        return "media-folder"
    return "review-candidate"


def _handle_profile(args: Namespace) -> dict[str, Any]:
    manifest_path = _resolve_manifest_path(args)
    profile = build_assignment_profile(
        load_manifest(manifest_path),
        args.assignment_folder,
    )
    payload = profile.to_dict()
    payload["manifest_path"] = str(manifest_path)
    if args.save:
        payload["profile_path"] = str(save_assignment_profile(profile))
    return payload


def _handle_intelligence_card(args: Namespace) -> dict[str, Any]:
    if args.building_size_sf < 1:
        raise ValueError("--building-size-sf must be at least 1.")

    intelligence = load_synthetic_verified_intelligence(DEFAULT_SYNTHETIC_INTELLIGENCE_PATH)
    result = match_firm_intelligence(
        FakeOrder(
            address=args.address,
            city=args.city,
            state=args.state,
            property_type=args.property_type,
            building_size_sf=args.building_size_sf,
            client=args.client,
        ),
        intelligence,
    )
    return build_firm_intelligence_card(result, intelligence).to_dict()


def _handle_subject_profile(args: Namespace) -> dict[str, Any]:
    profile = build_demo_subject_profile(
        approve=tuple(args.approve),
        lock=tuple(args.lock),
    )
    payload = profile.to_dict()
    payload["profileType"] = "synthetic_subject_profile_preview"
    payload["guardrail"] = (
        "Synthetic demo data only. No report export, OCR, embeddings, "
        "OneDrive integration, or source document ingestion is performed."
    )
    return payload


def _handle_property_library(args: Namespace) -> dict[str, Any]:
    return build_demo_property_library_workspace(
        PropertyLibraryFilters(
            query=args.query,
            property_type=args.property_type,
            county=args.county,
            comp_role=args.comp_role,
            report_usage=args.report_usage,
            date_from=args.date_from,
            date_to=args.date_to,
            min_size_sf=args.min_size_sf,
            max_size_sf=args.max_size_sf,
            verification_status=args.verification_status,
            selected_property_id=args.selected_property_id,
        )
    )


def _resolve_manifest_path(args: Namespace) -> Path:
    if getattr(args, "latest", False):
        return latest_manifest_path()
    return Path(args.manifest)


if __name__ == "__main__":
    raise SystemExit(main())
