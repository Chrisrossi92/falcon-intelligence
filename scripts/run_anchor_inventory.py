"""Run privacy-safe anchor-family inventory over local searchable text."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.anchor_inventory import (
    render_anchor_inventory_markdown,
    run_local_anchor_inventory,
    save_anchor_inventory_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run privacy-safe anchor-family inventory over searchable report text.")
    parser.add_argument(
        "--intake",
        default="data/historical-intake/historical-intake-report.json",
        help="Path to the ignored historical intake JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/anchor-inventory",
        help="Ignored local output directory for privacy-safe anchor inventory reports.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print privacy-safe Markdown without writing output files.",
    )
    args = parser.parse_args()

    report = run_local_anchor_inventory(args.intake)
    if args.no_write:
        print(render_anchor_inventory_markdown(report))
        return 0

    outputs = save_anchor_inventory_outputs(report, args.output_directory)
    print(
        json.dumps(
            {
                "outputs": outputs,
                "summary": {
                    "analyzed_report_count": report.analyzed_report_count,
                    "anchor_count_rows": len(report.inventory_rows),
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
