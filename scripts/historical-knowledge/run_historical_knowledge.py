"""Run local-only historical knowledge metadata extraction."""

from argparse import ArgumentParser
import json

from falcon_intel.historical_knowledge import (
    run_historical_knowledge_extraction,
    save_historical_knowledge_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run deterministic metadata extraction for likely final historical reports.")
    parser.add_argument(
        "--intake",
        default="data/historical-intake/historical-intake-report.json",
        help="Path to the ignored historical intake JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/historical-knowledge",
        help="Ignored local output directory for historical knowledge metadata.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the extraction summary without writing output files.",
    )
    args = parser.parse_args()

    report = run_historical_knowledge_extraction(args.intake)
    if args.no_write:
        print(json.dumps(report.to_dict()["summary"], indent=2, sort_keys=True))
        return 0

    outputs = save_historical_knowledge_outputs(report, args.output_directory)
    print(json.dumps({"outputs": outputs, "summary": report.to_dict()["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
