from pathlib import Path

from falcon_intel.historical_intake import (
    HistoricalIntakeConfig,
    classify_candidate_role,
    classify_readiness,
    detect_duplicate_groups,
    group_candidate_orders,
    load_historical_intake_config,
    normalize_filename,
    run_historical_intake,
    save_inventory_outputs,
)


def test_normalize_filename_removes_version_and_noise() -> None:
    assert normalize_filename("2024_Client-Final Report_v2.PDF") == "2024 client report"


def test_load_historical_intake_config_accepts_windows_utf8_signature(tmp_path: Path) -> None:
    config_path = tmp_path / "historical-intake.config.local.json"
    config_path.write_text(
        '{"source_directories":["C:/approved/local/sample"],"dry_run":true}',
        encoding="utf-8-sig",
    )

    config = load_historical_intake_config(config_path)

    assert config.source_directories == ("C:/approved/local/sample",)
    assert config.dry_run is True


def test_classify_candidate_role_from_filename_and_folder() -> None:
    assert classify_candidate_role("Order 24001/100 Main St Final Appraisal Report.pdf") == "final_report"
    assert classify_candidate_role("Order 24001/100 Main St Draft Report.docx") == "draft_report"
    assert classify_candidate_role("Order 24001/support/Engagement Letter.pdf") == "engagement_letter"
    assert classify_candidate_role("Order 24001/workbooks/rent-roll.xlsx") == "rent_roll"
    assert classify_candidate_role("Order 24001/maps/flood map.png") == "map"
    assert classify_candidate_role("Order 24001/photos/front exterior.jpg") == "photo"
    assert classify_candidate_role("100 Sample Highway/12345-000001_Appraisalversion2.pdf") == "final_report"
    assert classify_candidate_role("100 Sample Highway/Addendum/12345-000001_Appraisalversion2.pdf") == "final_report"
    assert classify_candidate_role("100 Sample Highway/Submitted Restricted Report/Complete Restricted Report.pdf") == "final_report"
    assert classify_candidate_role("100 Sample Highway/Addendum/Appendix.pdf") == "source_document"
    assert classify_candidate_role("100 Sample Highway/Addendum/Sales Comps.pdf") == "source_document"
    assert classify_candidate_role("100 Sample Highway/Addendum/PRC.pdf") == "source_document"


def test_run_historical_intake_discovers_metadata_only_inventory(tmp_path: Path) -> None:
    source = tmp_path / "history"
    order = source / "Client Apex" / "Order 24001 - 100 Main Street"
    support = order / "support"
    support.mkdir(parents=True)
    (order / "100 Main Street Final Appraisal Report 2024-03-01.pdf").write_bytes(b"final report placeholder")
    (order / "100 Main Street Draft Report.docx").write_bytes(b"draft placeholder")
    (support / "100 Main Street Rent Roll.xlsx").write_bytes(b"rent roll placeholder")

    inventory = run_historical_intake(
        HistoricalIntakeConfig(
            source_directories=(str(source),),
            output_directory=str(tmp_path / "out"),
        )
    )

    assert len(inventory.files) == 3
    assert {record.candidate_role for record in inventory.files} == {"draft_report", "final_report", "rent_roll"}
    assert inventory.candidate_order_groups
    group = inventory.candidate_order_groups[0]
    assert group.readiness_classification == "Ready for future extraction"
    assert group.likely_primary_report_file_id is not None
    assert group.grouping_reason == "Shared likely order identifier."


def test_duplicate_detection_exact_and_likely(tmp_path: Path) -> None:
    source = tmp_path / "history"
    source.mkdir()
    (source / "Order 24001 - 100 Main Street Final.pdf").write_bytes(b"same")
    (source / "Order 24001 - 100 Main Street Final Copy.pdf").write_bytes(b"same")
    folder_a = source / "Order 24002 - 200 Main Street"
    folder_b = source / "Order 24003 - 300 Main Street"
    folder_a.mkdir()
    folder_b.mkdir()
    (folder_a / "Final Report.pdf").write_bytes(b"abcd")
    (folder_b / "Final Report.pdf").write_bytes(b"wxyz")

    inventory = run_historical_intake(HistoricalIntakeConfig(source_directories=(str(source),)))
    duplicate_groups = detect_duplicate_groups(inventory.files)

    assert any(group.duplicate_type == "exact_hash" for group in duplicate_groups)
    assert any(group.duplicate_type == "likely_name_size" for group in duplicate_groups)


def test_grouping_uses_shared_address_when_order_id_missing(tmp_path: Path) -> None:
    source = tmp_path / "history"
    folder = source / "Client Beacon" / "100 Main Street"
    folder.mkdir(parents=True)
    (folder / "100 Main Street Final Appraisal Report.pdf").write_bytes(b"final")
    (folder / "100 Main Street Parcel Map.png").write_bytes(b"map")

    inventory = run_historical_intake(HistoricalIntakeConfig(source_directories=(str(source),)))
    groups = group_candidate_orders(inventory.files, inventory.duplicate_groups)

    assert len(groups) == 1
    assert groups[0].grouping_reason == "Shared likely property address."
    assert groups[0].confidence_level == "medium"


def test_unlabelled_assignment_id_does_not_split_address_named_folder(tmp_path: Path) -> None:
    source = tmp_path / "history"
    folder = source / "100 Sample Highway"
    addendum = folder / "Addendum"
    addendum.mkdir(parents=True)
    (folder / "12345-000001_Appraisalversion2.pdf").write_bytes(b"final")
    (folder / "Complete Restricted Report.pdf").write_bytes(b"restricted")
    (addendum / "Sales Comps.pdf").write_bytes(b"comps")
    (addendum / "PRC.pdf").write_bytes(b"record")

    inventory = run_historical_intake(HistoricalIntakeConfig(source_directories=(str(source),)))

    assert len(inventory.candidate_order_groups) == 1
    group = inventory.candidate_order_groups[0]
    assert group.grouping_reason == "Shared likely property address."
    assert group.likely_order_identifier == "12345-000001"
    assert group.likely_property_address == "100 Sample Highway"
    assert group.readiness_classification == "Ready for future extraction"


def test_readiness_classification_missing_final_report(tmp_path: Path) -> None:
    source = tmp_path / "history"
    source.mkdir()
    (source / "Order 24001 - 100 Main Street Draft Report.docx").write_bytes(b"draft")

    inventory = run_historical_intake(HistoricalIntakeConfig(source_directories=(str(source),)))

    assert inventory.candidate_order_groups[0].readiness_classification == "Missing final report"


def test_save_inventory_outputs_writes_json_csv_and_markdown(tmp_path: Path) -> None:
    source = tmp_path / "history"
    source.mkdir()
    (source / "Order 24001 - 100 Main Street Final Appraisal Report.pdf").write_bytes(b"final")
    inventory = run_historical_intake(HistoricalIntakeConfig(source_directories=(str(source),)))

    outputs = save_inventory_outputs(inventory, tmp_path / "out")

    assert Path(outputs["json"]).exists()
    assert Path(outputs["csv"]).exists()
    assert Path(outputs["markdown"]).exists()
    assert Path(outputs["markdown"]).name == "historical-intake-summary.md"
    assert "metadata-only" in Path(outputs["markdown"]).read_text(encoding="utf-8")
