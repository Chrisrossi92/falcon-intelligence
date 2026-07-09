"""Run the local Memory Graph Prototype V1 from ignored Knowledge Object output."""

from __future__ import annotations

from argparse import ArgumentParser
import json

from falcon_intel.memory_graph import run_memory_graph_builder, save_memory_graph_outputs


def main() -> int:
    parser = ArgumentParser(description="Build local Memory Graph nodes and relationships from Knowledge Objects.")
    parser.add_argument(
        "--knowledge-objects",
        default="data/knowledge/knowledge-objects-report.json",
        help="Path to ignored knowledge-objects-report.json output.",
    )
    parser.add_argument(
        "--output-directory",
        default="data/memory",
        help="Ignored directory for Memory Graph report outputs.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the summary without writing output files.",
    )
    args = parser.parse_args()

    report = run_memory_graph_builder(args.knowledge_objects)
    payload: dict[str, object] = {"summary": report.to_dict()["summary"]}
    if not args.no_write:
        payload["outputs"] = save_memory_graph_outputs(report, args.output_directory)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
