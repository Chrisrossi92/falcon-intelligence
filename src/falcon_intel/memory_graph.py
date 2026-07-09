"""Local Memory Graph Prototype V1 for Falcon Intelligence.

The prototype converts local Knowledge Object candidates into graph nodes and
relationships. It does not create a production graph database, schemas, APIs,
uploads, embeddings, OCR, AI output, or source-document ingestion.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
from typing import Any


MEMORY_GRAPH_VERSION = "1"
READINESS_ORDER = ("ready", "probable", "needs_review", "blocked")
NODE_TYPES = {
    "property": "Property",
    "report": "Report",
    "client_user": "Client/User",
    "personnel": "Personnel",
    "open_issues": "Open Issues",
}


@dataclass(frozen=True)
class MemoryGraphNode:
    """One local graph node derived from a Knowledge Object candidate."""

    node_id: str
    node_type: str
    label: str
    source_object_id: str
    readiness: str
    confidence: str
    key_attributes: dict[str, str]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class MemoryGraphRelationship:
    """One local deterministic relationship between graph nodes."""

    relationship_id: str
    relationship_type: str
    from_node_id: str
    to_node_id: str
    confidence: str
    source_object_references: tuple[str, ...]
    source_fact_references: tuple[str, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ReportMemoryGraph:
    """Memory Graph nodes and relationships for one report package."""

    file_id: str
    file_name: str
    graph_readiness: str
    nodes: tuple[MemoryGraphNode, ...]
    relationships: tuple[MemoryGraphRelationship, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class MemoryGraphReport:
    """Complete local Memory Graph Prototype V1 output."""

    memory_graph_version: str
    generated_at: str
    source_knowledge_objects_path: str
    graphs: tuple[ReportMemoryGraph, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_graph_version": self.memory_graph_version,
            "generated_at": self.generated_at,
            "source_knowledge_objects_path": self.source_knowledge_objects_path,
            "graphs": [asdict(graph) for graph in self.graphs],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "summary": build_memory_graph_summary(self),
        }


def build_report_memory_graph(report_objects: dict[str, Any]) -> ReportMemoryGraph:
    """Build a local Memory Graph for one Knowledge Object report package."""

    candidates = tuple(report_objects.get("object_candidates", ()))
    nodes = tuple(_node_from_candidate(candidate) for candidate in candidates)
    nodes_by_type = {_source_type(candidate): node for candidate, node in zip(candidates, nodes)}
    candidates_by_type = {_source_type(candidate): candidate for candidate in candidates}
    relationships = tuple(_build_relationships(nodes_by_type, candidates_by_type))
    graph_readiness = calculate_graph_readiness(nodes)
    warnings = tuple(str(item) for item in report_objects.get("warnings", []) if item)

    return ReportMemoryGraph(
        file_id=str(report_objects.get("file_id", "unknown-report")),
        file_name=str(report_objects.get("file_name", "Unknown report")),
        graph_readiness=graph_readiness,
        nodes=nodes,
        relationships=relationships,
        warnings=warnings,
    )


def run_memory_graph_builder(knowledge_objects_path: str | Path) -> MemoryGraphReport:
    """Build local Memory Graph output from ignored Knowledge Object output."""

    path = Path(knowledge_objects_path)
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    timestamp = datetime.now(UTC).isoformat()
    graphs = tuple(build_report_memory_graph(item) for item in payload.get("reports", []))
    return MemoryGraphReport(
        memory_graph_version=MEMORY_GRAPH_VERSION,
        generated_at=timestamp,
        source_knowledge_objects_path=str(path),
        graphs=graphs,
        warnings=tuple(str(item) for item in payload.get("warnings", []) if item),
        errors=tuple(str(item) for item in payload.get("errors", []) if item),
    )


def calculate_graph_readiness(nodes: tuple[MemoryGraphNode, ...]) -> str:
    """Calculate deterministic graph readiness from node readiness."""

    readiness = {node.readiness for node in nodes}
    if "blocked" in readiness:
        return "blocked"
    if "needs_review" in readiness:
        return "needs_review"
    if "probable" in readiness:
        return "probable"
    return "ready"


def build_memory_graph_summary(report: MemoryGraphReport) -> dict[str, Any]:
    """Build compact graph, node, relationship, and readiness counts."""

    node_types = Counter()
    relationship_types = Counter()
    graph_readiness = Counter()
    node_readiness = Counter()
    for graph in report.graphs:
        graph_readiness[graph.graph_readiness] += 1
        for node in graph.nodes:
            node_types[node.node_type] += 1
            node_readiness[node.readiness] += 1
        for relationship in graph.relationships:
            relationship_types[relationship.relationship_type] += 1

    return {
        "graph_count": len(report.graphs),
        "node_count": sum(node_types.values()),
        "relationship_count": sum(relationship_types.values()),
        "node_type_breakdown": dict(sorted(node_types.items())),
        "relationship_type_breakdown": dict(sorted(relationship_types.items())),
        "graph_readiness_breakdown": dict(sorted(graph_readiness.items())),
        "node_readiness_breakdown": dict(sorted(node_readiness.items())),
        "warnings": list(report.warnings),
        "errors": list(report.errors),
    }


def render_memory_graph_summary(report: MemoryGraphReport) -> str:
    """Render a local Markdown summary without source report text."""

    summary = build_memory_graph_summary(report)
    lines = [
        "# Memory Graph Summary",
        "",
        "This local output contains deterministic Memory Graph prototype nodes and relationships only. It does not create a production graph database, schemas, APIs, AI output, OCR output, embeddings, or uploads.",
        "",
        "## Totals",
        "",
        f"- Graphs processed: {summary['graph_count']}",
        f"- Nodes: {summary['node_count']}",
        f"- Relationships: {summary['relationship_count']}",
        "",
        "## Node Types",
        "",
    ]
    lines.extend(_markdown_count_lines(summary["node_type_breakdown"]))
    lines.extend(["", "## Relationship Types", ""])
    lines.extend(_markdown_count_lines(summary["relationship_type_breakdown"]))
    lines.extend(["", "## Graph Readiness", ""])
    lines.extend(_markdown_count_lines(summary["graph_readiness_breakdown"]))
    lines.extend(["", "## Report Graphs", ""])
    if report.graphs:
        for graph in report.graphs:
            lines.append(f"- {graph.file_id}: {graph.graph_readiness}, {len(graph.nodes)} nodes, {len(graph.relationships)} relationships")
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings / Errors", ""])
    warnings = list(report.warnings) + list(report.errors)
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None")
    return "\n".join(lines) + "\n"


def save_memory_graph_outputs(
    report: MemoryGraphReport,
    output_directory: str | Path,
    *,
    basename: str = "memory-graph-report",
) -> dict[str, str]:
    """Save ignored JSON and Markdown Memory Graph outputs."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / "memory-graph-summary.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_memory_graph_summary(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _node_from_candidate(candidate: dict[str, Any]) -> MemoryGraphNode:
    object_type = _source_type(candidate)
    return MemoryGraphNode(
        node_id=_stable_id("node", str(candidate.get("object_id") or candidate.get("stable_key") or object_type)),
        node_type=NODE_TYPES.get(object_type, object_type),
        label=str(candidate.get("display_label") or NODE_TYPES.get(object_type, object_type)),
        source_object_id=str(candidate.get("object_id", "")),
        readiness=str(candidate.get("readiness", "needs_review")),
        confidence=str(candidate.get("confidence", "low")),
        key_attributes={str(key): str(value) for key, value in dict(candidate.get("attributes", {})).items()},
        notes=tuple(str(item) for item in candidate.get("notes", []) if item),
    )


def _build_relationships(
    nodes_by_type: dict[str, MemoryGraphNode],
    candidates_by_type: dict[str, dict[str, Any]],
) -> list[MemoryGraphRelationship]:
    relationships: list[MemoryGraphRelationship] = []
    property_node = nodes_by_type.get("property")
    report_node = nodes_by_type.get("report")
    client_user_node = nodes_by_type.get("client_user")
    personnel_node = nodes_by_type.get("personnel")
    open_issues_node = nodes_by_type.get("open_issues")

    if property_node and report_node:
        relationships.append(_relationship("PROPERTY_HAS_REPORT", property_node, report_node, candidates_by_type, ("property_address", "report_type")))
        relationships.append(_relationship("PROPERTY_HAS_VERIFIED_IDENTITY", property_node, report_node, candidates_by_type, ("property_address",)))
        relationships.append(_relationship("REPORT_SUPPORTS_PROPERTY_PASSPORT", report_node, property_node, candidates_by_type, ("property_address", "effective_date")))

    if report_node and client_user_node:
        relationships.append(_relationship("REPORT_FOR_CLIENT", report_node, client_user_node, candidates_by_type, ("client",)))
        if _has_attribute(candidates_by_type.get("client_user"), "intended_user"):
            relationships.append(_relationship("REPORT_HAS_INTENDED_USER", report_node, client_user_node, candidates_by_type, ("intended_user",)))

    if report_node and personnel_node:
        if _has_attribute(candidates_by_type.get("personnel"), "appraiser_name"):
            relationships.append(_relationship("REPORT_PREPARED_BY_APPRAISER", report_node, personnel_node, candidates_by_type, ("appraiser_name",)))
        if _has_attribute(candidates_by_type.get("personnel"), "reviewer_name"):
            relationships.append(_relationship("REPORT_REVIEWED_BY_REVIEWER", report_node, personnel_node, candidates_by_type, ("reviewer_name",)))

    if report_node and open_issues_node and open_issues_node.readiness != "ready":
        relationships.append(_relationship("REPORT_HAS_OPEN_ISSUE", report_node, open_issues_node, candidates_by_type, tuple(open_issues_node.key_attributes)))

    return relationships


def _relationship(
    relationship_type: str,
    from_node: MemoryGraphNode,
    to_node: MemoryGraphNode,
    candidates_by_type: dict[str, dict[str, Any]],
    source_facts: tuple[str, ...],
) -> MemoryGraphRelationship:
    source_object_references = tuple(
        candidate.get("object_id", "")
        for candidate in candidates_by_type.values()
        if candidate.get("object_id") in {from_node.source_object_id, to_node.source_object_id}
    )
    return MemoryGraphRelationship(
        relationship_id=_stable_id("rel", f"{relationship_type}|{from_node.node_id}|{to_node.node_id}"),
        relationship_type=relationship_type,
        from_node_id=from_node.node_id,
        to_node_id=to_node.node_id,
        confidence=_relationship_confidence(from_node, to_node),
        source_object_references=tuple(str(item) for item in source_object_references if item),
        source_fact_references=source_facts,
        notes=(f"{relationship_type} was created by deterministic Memory Graph Prototype V1 rules.",),
    )


def _relationship_confidence(from_node: MemoryGraphNode, to_node: MemoryGraphNode) -> str:
    if "blocked" in {from_node.readiness, to_node.readiness}:
        return "low"
    if "needs_review" in {from_node.readiness, to_node.readiness}:
        return "low"
    if "probable" in {from_node.readiness, to_node.readiness}:
        return "medium"
    return "high"


def _has_attribute(candidate: dict[str, Any] | None, key: str) -> bool:
    if not candidate:
        return False
    value = dict(candidate.get("attributes", {})).get(key)
    return bool(value and value not in {"missing", "conflicting", "needs_review"})


def _source_type(candidate: dict[str, Any]) -> str:
    return str(candidate.get("object_type", "unknown"))


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"mg-{prefix}-{digest[:16]}"


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]
