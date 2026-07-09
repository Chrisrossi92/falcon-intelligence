"""Run opt-in privacy-safe OCR/layout pilot diagnostics."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.ocr_layout_pilot import (
    render_ocr_layout_pilot_markdown,
    run_local_ocr_layout_pilot,
    save_ocr_layout_pilot_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run opt-in privacy-safe OCR/layout diagnostics.")
    parser.add_argument(
        "--intake",
        default="data/historical-intake/historical-intake-report.json",
        help="Path to the ignored historical intake JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/ocr-layout-pilot",
        help="Ignored local output directory for privacy-safe OCR/layout diagnostics.",
    )
    parser.add_argument(
        "--enable-ocr",
        action="store_true",
        help="Opt in to local OCR. Without this flag, the pilot writes availability diagnostics only.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=170,
        help="Rasterization DPI for opt-in OCR. Lower values reduce artifact size in memory and runtime.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print privacy-safe Markdown without writing output files.",
    )
    args = parser.parse_args()

    report = run_local_ocr_layout_pilot(args.intake, enable_ocr=args.enable_ocr, dpi=args.dpi)
    if args.no_write:
        print(render_ocr_layout_pilot_markdown(report))
        return 0

    outputs = save_ocr_layout_pilot_outputs(report, args.output_directory)
    print(
        json.dumps(
            {
                "outputs": outputs,
                "summary": {
                    "ocr_enabled": report.ocr_enabled,
                    "candidate_final_report_count": report.candidate_final_report_count,
                    "analyzed_report_count": report.analyzed_report_count,
                    "diagnostic_count": len(report.diagnostics),
                    "aggregate_counts": report.aggregate_counts,
                    "warnings": report.warnings,
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
