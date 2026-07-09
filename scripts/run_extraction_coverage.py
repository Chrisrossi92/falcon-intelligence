"""Run privacy-safe local extraction coverage reporting."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.extraction_coverage import (
    render_extraction_coverage_markdown,
    run_local_extraction_coverage,
    save_extraction_coverage_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run privacy-safe extraction coverage from local historical intake output.")
    parser.add_argument(
        "--intake",
        default="data/historical-intake/historical-intake-report.json",
        help="Path to the ignored historical intake JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/extraction-coverage",
        help="Ignored local output directory for privacy-safe coverage reports.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print privacy-safe Markdown without writing output files.",
    )
    args = parser.parse_args()

    report = run_local_extraction_coverage(args.intake)
    if args.no_write:
        print(render_extraction_coverage_markdown(report))
        return 0

    outputs = save_extraction_coverage_outputs(report, args.output_directory)
    print(
        json.dumps(
            {
                "outputs": outputs,
                "summary": {
                    "source_file_count": report.source_file_count,
                    "candidate_final_report_count": report.candidate_final_report_count,
                    "analyzed_report_count": report.analyzed_report_count,
                    "verification_status_distribution": report.verification_status_distribution,
                    "confidence_distribution": report.confidence_distribution,
                    "warning_type_counts": report.warning_type_counts,
                    "next_parsing_targets": report.next_parsing_targets,
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
