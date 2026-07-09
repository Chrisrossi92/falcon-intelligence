"""Run the local-only historical report intake inventory."""

from argparse import ArgumentParser
import json

from falcon_intel.historical_intake import (
    load_historical_intake_config,
    run_historical_intake,
    save_inventory_outputs,
)


def main() -> int:
    parser = ArgumentParser(description="Run a metadata-only historical report intake inventory.")
    parser.add_argument("--config", required=True, help="Path to historical-intake.config.json.")
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the inventory summary without writing output files.",
    )
    args = parser.parse_args()

    config = load_historical_intake_config(args.config)
    inventory = run_historical_intake(config)
    if args.no_write:
        print(json.dumps(inventory.to_dict()["summary"], indent=2, sort_keys=True))
        return 0

    outputs = save_inventory_outputs(inventory, config.output_directory)
    print(json.dumps({"outputs": outputs, "summary": inventory.to_dict()["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
