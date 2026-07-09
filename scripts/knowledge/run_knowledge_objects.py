"""Run the local Knowledge Object Builder V1 from ignored verification output."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.knowledge_objects import run_knowledge_object_builder, save_knowledge_object_outputs


def main() -> int:
    parser = ArgumentParser(description="Build local Knowledge Object candidates from Verified Facts.")
    parser.add_argument(
        "--verification",
        default="data/verification/verification-report.json",
        help="Path to ignored verification-report.json output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/knowledge",
        help="Ignored directory for knowledge object report outputs.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the summary without writing output files.",
    )
    args = parser.parse_args()

    report = run_knowledge_object_builder(args.verification)
    payload: dict[str, object] = {"summary": report.to_dict()["summary"]}
    if not args.no_write:
        payload["outputs"] = save_knowledge_object_outputs(report, args.output_directory)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
