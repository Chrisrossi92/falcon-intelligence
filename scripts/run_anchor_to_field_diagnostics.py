"""Run privacy-safe anchor-to-field diagnostics for appraiser/title fields."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.anchor_inventory import (
    render_anchor_to_field_diagnostics_markdown,
    run_local_anchor_to_field_diagnostics,
    save_anchor_to_field_diagnostics_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run privacy-safe appraiser/title anchor-to-field diagnostics.")
    parser.add_argument(
        "--intake",
        default="data/historical-intake/historical-intake-report.json",
        help="Path to the ignored historical intake JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/anchor-inventory",
        help="Ignored local output directory for privacy-safe anchor diagnostics.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print privacy-safe Markdown without writing output files.",
    )
    args = parser.parse_args()

    report = run_local_anchor_to_field_diagnostics(args.intake)
    if args.no_write:
        print(render_anchor_to_field_diagnostics_markdown(report))
        return 0

    outputs = save_anchor_to_field_diagnostics_outputs(report, args.output_directory)
    print(
        json.dumps(
            {
                "outputs": outputs,
                "summary": {
                    "analyzed_report_count": report.analyzed_report_count,
                    "diagnostic_count": report.diagnostic_count,
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
