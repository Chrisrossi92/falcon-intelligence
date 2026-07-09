"""Smoke validation for the local Memory Graph Prototype V1."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from falcon_intel.knowledge_objects import KnowledgeObjectsReport, build_report_knowledge_objects
from falcon_intel.memory_graph import (
    MemoryGraphReport,
    build_report_memory_graph,
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
        "verification_method": "synthetic smoke rule",
        "verification_timestamp": "2026-06-30T00:00:00+00:00",
        "notes": [],
        "source_references": [f"synthetic:{field_name}"] if value else [],
    }


def main() -> int:
    knowledge_package = build_report_knowledge_objects(
        {
            "file_id": "synthetic-final",
            "file_name": "Synthetic Restricted Appraisal Report.pdf",
            "file_path": "synthetic/Synthetic Restricted Appraisal Report.pdf",
            "facts": [
                _fact("property_address", "100 Sample Industrial Avenue"),
                _fact("report_type", "restricted appraisal report"),
                _fact("effective_date", "June 1, 2026"),
                _fact("client", "Example Bank"),
                _fact("intended_user", "Example Bank"),
                _fact("appraiser_name", "Synthetic Appraiser"),
                _fact("reviewer_name", None, "missing", "missing"),
            ],
            "warnings": [],
        },
        timestamp="2026-06-30T00:00:00+00:00",
    )
    knowledge_report = KnowledgeObjectsReport(
        knowledge_object_version="1",
        generated_at="2026-06-30T00:00:00+00:00",
        source_verification_path="synthetic-verification.json",
        reports=(knowledge_package,),
    )
    graph = build_report_memory_graph(knowledge_report.to_dict()["reports"][0])

    assert len(graph.nodes) == 4
    assert graph.graph_readiness == "needs_review"
    relationship_types = {relationship.relationship_type for relationship in graph.relationships}
    assert "PROPERTY_HAS_REPORT" in relationship_types
    assert "REPORT_FOR_CLIENT" in relationship_types
    assert "REPORT_PREPARED_BY_APPRAISER" in relationship_types

    with TemporaryDirectory() as directory:
        outputs = save_memory_graph_outputs(
            report=MemoryGraphReport(
                memory_graph_version="1",
                generated_at="2026-06-30T00:00:00+00:00",
                source_knowledge_objects_path="synthetic-knowledge-objects.json",
                graphs=(graph,),
            ),
            output_directory=Path(directory),
        )
        assert Path(outputs["json"]).exists()
        assert Path(outputs["markdown"]).exists()

    print("memory graph smoke validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
