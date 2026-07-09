import json
from pathlib import Path

from falcon_intel.knowledge_objects import KnowledgeObjectsReport, build_report_knowledge_objects
from falcon_intel.memory_graph import (
    MemoryGraphReport,
    build_memory_graph_summary,
    build_report_memory_graph,
    calculate_graph_readiness,
    render_memory_graph_summary,
    run_memory_graph_builder,
    save_memory_graph_outputs,
)


def _fact(field_name: str, value: str | None, status: str = "verified", confidence: str = "high") -> dict[str, object]:
    return {
        "field_name": field_name,
        "verified_value": value,
        "verification_status": status,
        "confidence": confidence,
        "supporting_evidence": [],
        "conflicting_evidence": [],
        "verification_method": "synthetic test rule",
        "verification_timestamp": "2026-06-30T00:00:00+00:00",
        "notes": [],
        "source_references": [f"synthetic:{field_name}"] if value else [],
    }


def _knowledge_report_dict(*facts: dict[str, object]) -> dict[str, object]:
    package = build_report_knowledge_objects(
        {
            "file_id": "synthetic-final",
            "file_name": "Synthetic Restricted Appraisal Report.pdf",
            "file_path": "synthetic/Synthetic Restricted Appraisal Report.pdf",
            "facts": list(facts),
            "warnings": [],
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    report = KnowledgeObjectsReport(
        knowledge_object_version="1",
        generated_at="2026-06-30T00:00:00+00:00",
        source_verification_path="synthetic-verification.json",
        reports=(package,),
    )
    return report.to_dict()


def _graph(*facts: dict[str, object]):
    report = _knowledge_report_dict(*facts)
    return build_report_memory_graph(report["reports"][0])


def test_builds_nodes_from_knowledge_objects() -> None:
    graph = _graph(
        _fact("property_address", "100 Sample Industrial Avenue"),
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
    )

    assert {node.node_type for node in graph.nodes} == {"Property", "Report"}
    assert all(node.source_object_id.startswith("ko-") for node in graph.nodes)


def test_builds_property_to_report_relationship() -> None:
    graph = _graph(
        _fact("property_address", "100 Sample Industrial Avenue"),
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
    )

    relationship_types = {relationship.relationship_type for relationship in graph.relationships}

    assert "PROPERTY_HAS_REPORT" in relationship_types
    assert "PROPERTY_HAS_VERIFIED_IDENTITY" in relationship_types
    assert "REPORT_SUPPORTS_PROPERTY_PASSPORT" in relationship_types


def test_builds_report_to_client_user_relationships() -> None:
    graph = _graph(
        _fact("property_address", "100 Sample Industrial Avenue"),
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
        _fact("client", "Example Bank"),
        _fact("intended_user", "Example Bank"),
    )

    relationship_types = {relationship.relationship_type for relationship in graph.relationships}

    assert "REPORT_FOR_CLIENT" in relationship_types
    assert "REPORT_HAS_INTENDED_USER" in relationship_types


def test_builds_report_to_personnel_relationships() -> None:
    graph = _graph(
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
        _fact("appraiser_name", "Synthetic Appraiser"),
        _fact("reviewer_name", "Synthetic Reviewer"),
    )

    relationship_types = {relationship.relationship_type for relationship in graph.relationships}

    assert "REPORT_PREPARED_BY_APPRAISER" in relationship_types
    assert "REPORT_REVIEWED_BY_REVIEWER" in relationship_types


def test_builds_report_to_open_issues_relationship() -> None:
    graph = _graph(
        _fact("property_address", None, "conflicting", "conflicting"),
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
    )

    assert "REPORT_HAS_OPEN_ISSUE" in {relationship.relationship_type for relationship in graph.relationships}
    assert graph.graph_readiness == "blocked"


def test_graph_readiness_calculation() -> None:
    ready_graph = _graph(
        _fact("property_address", "100 Sample Industrial Avenue"),
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
        _fact("client", "Example Bank"),
        _fact("intended_user", "Example Bank"),
        _fact("appraiser_name", "Synthetic Appraiser"),
        _fact("reviewer_name", "Synthetic Reviewer"),
    )
    probable_graph = _graph(
        _fact("property_address", "100 Sample Industrial Avenue"),
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
        _fact("client", "Example Bank"),
        _fact("intended_user", "Example Bank"),
        _fact("appraiser_name", "Synthetic Appraiser"),
        _fact("reviewer_name", None, "missing", "missing"),
    )

    assert calculate_graph_readiness(ready_graph.nodes) == "ready"
    assert calculate_graph_readiness(probable_graph.nodes) == "needs_review"


def test_summary_generation_and_outputs(tmp_path: Path) -> None:
    graph = _graph(
        _fact("property_address", "100 Sample Industrial Avenue"),
        _fact("report_type", "restricted appraisal report"),
        _fact("effective_date", "June 1, 2026"),
    )
    report = MemoryGraphReport(
        memory_graph_version="1",
        generated_at="2026-06-30T00:00:00+00:00",
        source_knowledge_objects_path="synthetic-knowledge-objects.json",
        graphs=(graph,),
    )

    summary = build_memory_graph_summary(report)
    outputs = save_memory_graph_outputs(report, tmp_path)

    assert summary["node_count"] == 2
    assert summary["relationship_count"] >= 3
    assert Path(outputs["json"]).exists()
    assert Path(outputs["markdown"]).name == "memory-graph-summary.md"
    assert "deterministic Memory Graph prototype nodes and relationships only" in render_memory_graph_summary(report)


def test_runner_consumes_knowledge_object_output(tmp_path: Path) -> None:
    knowledge_path = tmp_path / "knowledge-objects-report.json"
    knowledge_path.write_text(json.dumps(_knowledge_report_dict(_fact("property_address", "100 Sample Industrial Avenue"))), encoding="utf-8")

    report = run_memory_graph_builder(knowledge_path)

    assert report.graphs[0].file_id == "synthetic-final"
    assert build_memory_graph_summary(report)["node_type_breakdown"]["Property"] == 1
