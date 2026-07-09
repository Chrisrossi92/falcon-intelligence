"""Run local deterministic verification for historical knowledge candidates."""

from argparse import ArgumentParser
import json

from falcon_intel.verification_engine import run_verification, save_verification_outputs


def main() -> int:
    parser = ArgumentParser(description="Run deterministic verification for historical metadata candidates.")
    parser.add_argument(
        "--knowledge",
        default="data/historical-knowledge/historical-knowledge-report.json",
        help="Path to the ignored historical knowledge JSON output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/verification",
        help="Ignored local output directory for verification reports.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the verification summary without writing output files.",
    )
    args = parser.parse_args()

    report = run_verification(args.knowledge)
    if args.no_write:
        print(json.dumps(report.to_dict()["summary"], indent=2, sort_keys=True))
        return 0

    outputs = save_verification_outputs(report, args.output_directory)
    print(json.dumps({"outputs": outputs, "summary": report.to_dict()["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
