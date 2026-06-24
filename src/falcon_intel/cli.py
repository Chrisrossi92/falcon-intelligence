"""Command-line interface for local metadata-only prototype workflows."""

from argparse import ArgumentParser, Namespace
import json
from pathlib import Path
from typing import Any

from falcon_intel.discovery import AssignmentCandidate, discover_assignments
from falcon_intel.manifest import create_scan_manifest, save_scan_manifest
from falcon_intel.scanner import scan_metadata
from falcon_intel.search import (
    ManifestSearchQuery,
    load_manifest,
    search_manifest,
    summarize_results,
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

    search_parser = subparsers.add_parser("search", help="Search one manifest by metadata only.")
    search_parser.add_argument("--manifest", required=True, help="Manifest JSON path.")
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
    summary_parser.add_argument("--manifest", required=True, help="Manifest JSON path.")
    summary_parser.set_defaults(handler=_handle_summary)

    discover_parser = subparsers.add_parser(
        "discover",
        help="Discover probable assignment folders from one manifest.",
    )
    discover_parser.add_argument("--manifest", required=True, help="Manifest JSON path.")
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

    return parser


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


def _handle_search(args: Namespace) -> dict[str, Any]:
    query = ManifestSearchQuery(
        file_name_keyword=args.name,
        extension=args.extension,
        relative_path_keyword=args.path_keyword,
        supported_for_future_indexing=True if args.supported_only else None,
    )
    results = search_manifest(load_manifest(args.manifest), query)
    return {
        "result_count": len(results),
        "results": [result.to_dict() for result in results],
    }


def _handle_summary(args: Namespace) -> dict[str, Any]:
    results = search_manifest(load_manifest(args.manifest))
    summary = summarize_results(results)
    return {
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

    candidates = [
        candidate
        for candidate in discover_assignments(load_manifest(args.manifest))
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


if __name__ == "__main__":
    raise SystemExit(main())
