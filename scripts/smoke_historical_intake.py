"""Smoke check for the local-only historical intake inventory."""

from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.historical_intake import (
    HistoricalIntakeConfig,
    classify_candidate_role,
    normalize_filename,
    run_historical_intake,
    save_inventory_outputs,
)


def main() -> int:
    assert normalize_filename("2024_Client-Final Report_v2.PDF") == "2024 client report"
    assert classify_candidate_role("Order 24001/100 Main St Final Appraisal Report.pdf") == "final_report"
    assert classify_candidate_role("Order 24001/workbooks/rent-roll.xlsx") == "rent_roll"

    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "history"
        order = root / "Client Apex" / "Order 24001 - 100 Main Street"
        support = order / "support"
        support.mkdir(parents=True)
        (order / "100 Main Street Final Appraisal Report 2024-03-01.pdf").write_bytes(b"final")
        (order / "100 Main Street Draft Report.docx").write_bytes(b"draft")
        (support / "100 Main Street Rent Roll.xlsx").write_bytes(b"rent roll")

        inventory = run_historical_intake(
            HistoricalIntakeConfig(
                source_directories=(str(root),),
                output_directory=str(Path(temp_dir) / "out"),
            )
        )
        assert len(inventory.files) == 3
        assert inventory.candidate_order_groups[0].readiness_classification == "Ready for future extraction"

        outputs = save_inventory_outputs(inventory, Path(temp_dir) / "out")
        assert Path(outputs["json"]).exists()
        assert Path(outputs["csv"]).exists()
        assert Path(outputs["markdown"]).exists()

    print("historical intake smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
