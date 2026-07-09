"""Run privacy-safe unresolved-field extraction diagnostics."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.extraction_diagnostics import (
    render_extraction_diagnostics_markdown,
    run_local_extraction_diagnostics,
    save_extraction_diagnostics_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run privacy-safe unresolved-field extraction diagnostics.")
    parser.add_argument(
        "--intake",
        default="data/historical-intake/historical-intake-report.json",
        help="Path to the ignored historical intake JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/extraction-diagnostics",
        help="Ignored local output directory for privacy-safe diagnostics reports.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print privacy-safe Markdown without writing output files.",
    )
    args = parser.parse_args()

    report = run_local_extraction_diagnostics(args.intake)
    if args.no_write:
        print(render_extraction_diagnostics_markdown(report))
        return 0

    outputs = save_extraction_diagnostics_outputs(report, args.output_directory)
    print(
        json.dumps(
            {
                "outputs": outputs,
                "summary": {
                    "analyzed_report_count": report.analyzed_report_count,
                    "unresolved_count": report.unresolved_count,
                    "aggregate_categories": report.aggregate_categories,
                    "recommendations": report.recommendations,
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
