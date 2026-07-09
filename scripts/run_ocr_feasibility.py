"""Run privacy-safe OCR/layout feasibility planning without performing OCR."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.ocr_feasibility import (
    render_ocr_feasibility_markdown,
    run_local_ocr_feasibility,
    save_ocr_feasibility_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run privacy-safe OCR/layout feasibility planning without OCR.")
    parser.add_argument(
        "--intake",
        default="data/historical-intake/historical-intake-report.json",
        help="Path to the ignored historical intake JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/ocr-feasibility",
        help="Ignored local output directory for privacy-safe OCR feasibility reports.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print privacy-safe Markdown without writing output files.",
    )
    args = parser.parse_args()

    report = run_local_ocr_feasibility(args.intake)
    if args.no_write:
        print(render_ocr_feasibility_markdown(report))
        return 0

    outputs = save_ocr_feasibility_outputs(report, args.output_directory)
    print(
        json.dumps(
            {
                "outputs": outputs,
                "summary": {
                    "candidate_final_report_count": report.candidate_final_report_count,
                    "analyzed_report_count": report.analyzed_report_count,
                    "aggregate_counts": report.aggregate_counts,
                    "field_recommendations": report.field_recommendations,
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
