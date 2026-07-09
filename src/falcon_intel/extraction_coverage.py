"""Privacy-safe extraction coverage reporting for local sample runs.

This module summarizes deterministic extraction output without preserving raw
private values. It is intended for ignored local reports under data/.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from falcon_intel.historical_knowledge import (
    HistoricalKnowledgeReport,
    run_historical_knowledge_extraction,
)
from falcon_intel.knowledge_objects import (
    KnowledgeObjectsReport,
    build_report_knowledge_objects,
    build_knowledge_objects_summary,
)
from falcon_intel.memory_graph import (
    MemoryGraphReport,
    build_memory_graph_summary,
    build_report_memory_graph,
)
from falcon_intel.verification_engine import (
    VERIFY_FIELDS,
    VerificationReport,
    build_verification_summary,
    verify_report_candidate,
)


COVERAGE_VERSION = "1"
OUTPUT_BASENAME = "extraction-coverage-report"
APPROACH_FIELDS = ("sales_comparison_approach", "income_approach", "cost_approach")
EXAMPLE_LIMIT = 3


@dataclass(frozen=True)
class ExtractionCoverageReport:
    """Privacy-safe coverage summary for a local deterministic extraction run."""

    coverage_version: str
    generated_at: str
    source_intake_path: str
    source_file_count: int
    candidate_final_report_count: int
    analyzed_report_count: int
    fields_attempted: tuple[str, ...]
    field_coverage: dict[str, dict[str, Any]]
    confidence_distribution: dict[str, int]
    verification_status_distribution: dict[str, int]
    conflict_count: int
    warning_type_counts: dict[str, int]
    approach_indicators: dict[str, dict[str, int]]
    common_missing_fields: tuple[dict[str, Any], ...]
    common_low_confidence_fields: tuple[dict[str, Any], ...]
    redacted_examples: tuple[dict[str, Any], ...]
    knowledge_object_readiness: dict[str, int]
    memory_graph_readiness: dict[str, int]
    conflict_fields_by_type: tuple[dict[str, Any], ...]
    readiness_reason_counts: dict[str, int]
    promotion_blockers: tuple[dict[str, Any], ...]
    promotion_field_summary: dict[str, Any]
    next_parsing_targets: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_local_extraction_coverage(intake_path: str | Path) -> ExtractionCoverageReport:
    """Run current local stages in memory and return a privacy-safe report."""

    intake = _load_json(intake_path)
    knowledge_report = run_historical_knowledge_extraction(intake_path)
    verification_report = _build_verification_report(knowledge_report)
    knowledge_objects_report = _build_knowledge_objects_report(verification_report)
    memory_graph_report = _build_memory_graph_report(knowledge_objects_report)
    return build_extraction_coverage_report(
        intake=intake,
        knowledge_report=knowledge_report.to_dict(),
        verification_report=verification_report.to_dict(),
        knowledge_objects_summary=build_knowledge_objects_summary(knowledge_objects_report),
        knowledge_objects_report=knowledge_objects_report.to_dict(),
        memory_graph_summary=build_memory_graph_summary(memory_graph_report),
        source_intake_path=str(intake_path),
    )


def build_extraction_coverage_report(
    *,
    intake: dict[str, Any],
    knowledge_report: dict[str, Any],
    verification_report: dict[str, Any],
    knowledge_objects_summary: dict[str, Any] | None = None,
    knowledge_objects_report: dict[str, Any] | None = None,
    memory_graph_summary: dict[str, Any] | None = None,
    source_intake_path: str = "",
    generated_at: str | None = None,
) -> ExtractionCoverageReport:
    """Build privacy-safe coverage metrics from current pipeline payloads."""

    generated_at = generated_at or datetime.now(UTC).isoformat()
    files = tuple(dict(item) for item in intake.get("files", []))
    final_reports = tuple(item for item in files if item.get("candidate_role") == "final_report")
    report_candidates = tuple(dict(item) for item in knowledge_report.get("report_candidates", []))
    report_facts = tuple(dict(item) for item in verification_report.get("report_facts", []))

    field_coverage = _build_field_coverage(report_facts)
    confidence_distribution = _counter_to_dict(_fact_counter(report_facts, "confidence"))
    verification_status_distribution = _counter_to_dict(_fact_counter(report_facts, "verification_status"))
    warning_type_counts = _build_warning_type_counts(knowledge_report, verification_report, report_facts)
    approach_indicators = _build_approach_indicators(field_coverage)
    common_missing = _rank_field_status(field_coverage, "missing")
    common_low_confidence = _rank_low_confidence(field_coverage)
    redacted_examples = _build_redacted_examples(report_candidates, report_facts)
    knowledge_objects_summary = knowledge_objects_summary or {}
    knowledge_objects_report = knowledge_objects_report or {}
    memory_graph_summary = memory_graph_summary or {}
    promotion_field_summary = _build_promotion_field_summary(report_facts)

    return ExtractionCoverageReport(
        coverage_version=COVERAGE_VERSION,
        generated_at=generated_at,
        source_intake_path=str(source_intake_path),
        source_file_count=len(files),
        candidate_final_report_count=len(final_reports),
        analyzed_report_count=len(report_candidates),
        fields_attempted=tuple(VERIFY_FIELDS),
        field_coverage=field_coverage,
        confidence_distribution=confidence_distribution,
        verification_status_distribution=verification_status_distribution,
        conflict_count=verification_status_distribution.get("conflicting", 0),
        warning_type_counts=warning_type_counts,
        approach_indicators=approach_indicators,
        common_missing_fields=common_missing,
        common_low_confidence_fields=common_low_confidence,
        redacted_examples=redacted_examples,
        knowledge_object_readiness=dict(knowledge_objects_summary.get("readiness_breakdown", {})),
        memory_graph_readiness=dict(memory_graph_summary.get("graph_readiness_breakdown", {})),
        conflict_fields_by_type=_build_conflict_fields_by_type(report_facts),
        readiness_reason_counts=_build_readiness_reason_counts(knowledge_objects_report),
        promotion_blockers=_build_promotion_blockers(knowledge_objects_report),
        promotion_field_summary=promotion_field_summary,
        next_parsing_targets=_recommend_next_targets(field_coverage, warning_type_counts),
    )


def render_extraction_coverage_markdown(report: ExtractionCoverageReport) -> str:
    """Render coverage as Markdown without raw extracted values."""

    payload = report.to_dict()
    lines = [
        "# Privacy-Safe Extraction Coverage Report",
        "",
        "This local-only report summarizes deterministic extraction coverage. It does not include report bodies, raw extracted names, full addresses, client names, owner names, appraiser names, reviewer names, or long source values.",
        "",
        "## Totals",
        "",
        f"- Source files in intake: {report.source_file_count}",
        f"- Candidate final reports in intake: {report.candidate_final_report_count}",
        f"- Candidate final reports analyzed: {report.analyzed_report_count}",
        f"- Fields attempted per analyzed report: {len(report.fields_attempted)}",
        f"- Conflicting field ledgers: {report.conflict_count}",
        "",
        "## Verification Status Distribution",
        "",
    ]
    lines.extend(_markdown_count_lines(report.verification_status_distribution))
    lines.extend(["", "## Confidence Distribution", ""])
    lines.extend(_markdown_count_lines(report.confidence_distribution))
    lines.extend(["", "## Approach Indicators", ""])
    for field, counts in report.approach_indicators.items():
        label = field.replace("_", " ")
        lines.append(f"- {label}: present={counts.get('present', 0)}, missing={counts.get('missing', 0)}, other={counts.get('other', 0)}")
    lines.extend(["", "## Common Missing Fields", ""])
    lines.extend(_ranked_field_lines(report.common_missing_fields))
    lines.extend(["", "## Common Low-Confidence Fields", ""])
    lines.extend(_ranked_field_lines(report.common_low_confidence_fields))
    lines.extend(["", "## Warning Types", ""])
    lines.extend(_markdown_count_lines(report.warning_type_counts))
    lines.extend(["", "## Conflict Fields", ""])
    if report.conflict_fields_by_type:
        for item in report.conflict_fields_by_type:
            lines.append(
                "- "
                f"field={item['field_name']}; "
                f"candidate_count={item['candidate_count']}; "
                f"fingerprints={','.join(item['normalized_candidate_fingerprints']) or 'none'}; "
                f"source_labels={','.join(item['source_labels']) or 'none'}; "
                f"tiers={item.get('provenance_tier_counts', {})}; "
                f"status={item.get('verification_status', 'unknown')}; "
                f"reason={item['status_reason']}"
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Promotion Field Summary", ""])
    for label in ("safe_to_promote", "needs_review", "blocked", "missing"):
        group = report.promotion_field_summary.get(label, {})
        lines.append(f"- {label}: count={group.get('count', 0)}")
    lines.extend(["", "## Readiness Reasons", ""])
    lines.extend(_markdown_count_lines(report.readiness_reason_counts))
    lines.extend(["", "## Promotion Blockers", ""])
    if report.promotion_blockers:
        for item in report.promotion_blockers:
            lines.append(
                "- "
                f"object_type={item['object_type']}; "
                f"readiness={item['readiness']}; "
                f"missing={item['missing_required_count']}; "
                f"review={item['review_required_count']}; "
                f"conflicts={item['conflicting_count']}"
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Knowledge Object Readiness", ""])
    lines.extend(_markdown_count_lines(report.knowledge_object_readiness))
    lines.extend(["", "## Memory Graph Readiness", ""])
    lines.extend(_markdown_count_lines(report.memory_graph_readiness))
    lines.extend(["", "## Redacted Examples", ""])
    if report.redacted_examples:
        for example in report.redacted_examples:
            profile = example["value_profile"]
            lines.append(
                "- "
                f"field={example['field_name']}; "
                f"status={example['verification_status']}; "
                f"confidence={example['confidence']}; "
                f"type={profile['value_type']}; "
                f"length={profile['length_bucket']}; "
                f"year={profile.get('year') or 'n/a'}; "
                f"fingerprint={profile.get('fingerprint') or 'n/a'}"
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Next Parsing Targets", ""])
    lines.extend(f"- {item}" for item in report.next_parsing_targets) if report.next_parsing_targets else lines.append("- None")
    lines.extend(["", "## Machine Summary", ""])
    lines.append("```json")
    lines.append(json.dumps(_compact_machine_summary(payload), indent=2, sort_keys=True))
    lines.append("```")
    return "\n".join(lines) + "\n"


def save_extraction_coverage_outputs(
    report: ExtractionCoverageReport,
    output_directory: str | Path,
    *,
    basename: str = OUTPUT_BASENAME,
) -> dict[str, str]:
    """Save privacy-safe coverage JSON and Markdown under an ignored local folder."""

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{basename}.json"
    markdown_path = output_dir / f"{basename}.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_extraction_coverage_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _build_verification_report(knowledge_report: HistoricalKnowledgeReport) -> VerificationReport:
    timestamp = datetime.now(UTC).isoformat()
    payload = knowledge_report.to_dict()
    report_facts = tuple(verify_report_candidate(candidate, timestamp=timestamp) for candidate in payload.get("report_candidates", []))
    return VerificationReport(
        verification_version="1",
        generated_at=timestamp,
        source_knowledge_path="in-memory historical knowledge report",
        report_facts=report_facts,
        warnings=tuple(str(item) for item in payload.get("warnings", []) if item),
        errors=tuple(str(item) for item in payload.get("errors", []) if item),
    )


def _build_knowledge_objects_report(verification_report: VerificationReport) -> KnowledgeObjectsReport:
    timestamp = datetime.now(UTC).isoformat()
    payload = verification_report.to_dict()
    reports = tuple(build_report_knowledge_objects(item, timestamp=timestamp) for item in payload.get("report_facts", []))
    return KnowledgeObjectsReport(
        knowledge_object_version="1",
        generated_at=timestamp,
        source_verification_path="in-memory verification report",
        reports=reports,
        warnings=tuple(str(item) for item in payload.get("warnings", []) if item),
        errors=tuple(str(item) for item in payload.get("errors", []) if item),
    )


def _build_memory_graph_report(knowledge_objects_report: KnowledgeObjectsReport) -> MemoryGraphReport:
    timestamp = datetime.now(UTC).isoformat()
    payload = knowledge_objects_report.to_dict()
    graphs = tuple(build_report_memory_graph(item) for item in payload.get("reports", []))
    return MemoryGraphReport(
        memory_graph_version="1",
        generated_at=timestamp,
        source_knowledge_objects_path="in-memory knowledge object report",
        graphs=graphs,
        warnings=tuple(str(item) for item in payload.get("warnings", []) if item),
        errors=tuple(str(item) for item in payload.get("errors", []) if item),
    )


def _build_field_coverage(report_facts: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    fields: dict[str, dict[str, Any]] = {
        field: {
            "attempted": 0,
            "found": 0,
            "missing": 0,
            "verified": 0,
            "probable": 0,
            "needs_review": 0,
            "conflicting": 0,
            "rejected": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
        }
        for field in VERIFY_FIELDS
    }
    for package in report_facts:
        for fact in package.get("facts", []):
            field = str(fact.get("field_name", ""))
            if field not in fields:
                continue
            status = str(fact.get("verification_status") or "missing")
            confidence = str(fact.get("confidence") or "missing")
            fields[field]["attempted"] += 1
            fields[field][status] = fields[field].get(status, 0) + 1
            if status != "missing":
                fields[field]["found"] += 1
            if confidence in {"high", "medium", "low"}:
                fields[field][f"{confidence}_confidence"] += 1
    return fields


def _fact_counter(report_facts: Iterable[dict[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for package in report_facts:
        for fact in package.get("facts", []):
            counter[str(fact.get(key) or "unknown")] += 1
    return counter


def _build_warning_type_counts(
    knowledge_report: dict[str, Any],
    verification_report: dict[str, Any],
    report_facts: Iterable[dict[str, Any]],
) -> dict[str, int]:
    warning_observations: set[tuple[str, str]] = set()
    for item in knowledge_report.get("warnings", []):
        _add_warning_observation(warning_observations, item)
    for item in verification_report.get("warnings", []):
        _add_warning_observation(warning_observations, item)
    for candidate in knowledge_report.get("report_candidates", []):
        context = str(candidate.get("file_id") or "candidate")
        for item in candidate.get("warnings", []):
            _add_warning_observation(warning_observations, item, context)
    for package in report_facts:
        context = str(package.get("file_id") or "report")
        for item in package.get("warnings", []):
            _add_warning_observation(warning_observations, item, context)
        for fact in package.get("facts", []):
            for evidence_key in ("supporting_evidence", "conflicting_evidence"):
                for item in fact.get(evidence_key, []):
                    warning = item.get("warning")
                    if warning:
                        source_reference = str(item.get("source_reference") or context)
                        _add_warning_observation(warning_observations, warning, source_reference)
    return _counter_to_dict(Counter(item[0] for item in warning_observations))


def _build_approach_indicators(field_coverage: dict[str, dict[str, Any]]) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for field in APPROACH_FIELDS:
        coverage = field_coverage.get(field, {})
        present = int(coverage.get("found", 0))
        missing = int(coverage.get("missing", 0))
        attempted = int(coverage.get("attempted", 0))
        output[field] = {"present": present, "missing": missing, "other": max(0, attempted - present - missing)}
    return output


def _build_conflict_fields_by_type(report_facts: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    conflicts: list[dict[str, Any]] = []
    for package in report_facts:
        for fact in package.get("facts", []):
            diagnostics = dict(fact.get("diagnostics") or {})
            status = str(fact.get("verification_status") or "")
            reason = str(diagnostics.get("status_reason") or "")
            if status != "conflicting" and "disagrees" not in reason:
                continue
            source_labels = tuple(diagnostics.get("source_labels") or ())
            source_references = tuple(diagnostics.get("source_references") or ())
            fingerprints = tuple(diagnostics.get("normalized_candidate_fingerprints") or ())
            conflicts.append(
                {
                    "field_name": str(fact.get("field_name") or "unknown"),
                    "candidate_count": int(diagnostics.get("candidate_count") or len(fact.get("conflicting_evidence", ()))),
                    "normalized_candidate_fingerprints": tuple(sorted(set(str(item) for item in fingerprints))),
                    "source_labels": tuple(sorted(set(str(item) for item in source_labels))),
                    "source_references": tuple(sorted(set(str(item) for item in source_references))),
                    "verification_status": status,
                    "status_reason": reason or "conflicting",
                    "provenance_tier_counts": dict(diagnostics.get("provenance_tier_counts") or {}),
                }
            )
    conflicts.sort(key=lambda item: (item["field_name"], -item["candidate_count"]))
    return tuple(conflicts)


def _build_promotion_field_summary(report_facts: Iterable[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[str]] = {
        "safe_to_promote": [],
        "needs_review": [],
        "blocked": [],
        "missing": [],
    }
    for package in report_facts:
        for fact in package.get("facts", []):
            field = str(fact.get("field_name") or "unknown")
            status = str(fact.get("verification_status") or "missing")
            confidence = str(fact.get("confidence") or "missing")
            if status == "verified" and confidence == "high":
                groups["safe_to_promote"].append(field)
            elif status == "conflicting":
                groups["blocked"].append(field)
            elif status == "missing":
                groups["missing"].append(field)
            else:
                groups["needs_review"].append(field)
    return {
        label: {"count": len(fields), "fields": tuple(sorted(set(fields)))}
        for label, fields in groups.items()
    }


def _build_readiness_reason_counts(knowledge_objects_report: dict[str, Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for candidate in _iter_object_candidates(knowledge_objects_report):
        readiness = str(candidate.get("readiness") or "needs_review")
        counts[readiness] += 1
        reason = str(candidate.get("readiness_reason") or "")
        if reason:
            counts[reason] += 1
            continue
        if candidate.get("conflicting_fields"):
            counts["blocked_by_conflict"] += 1
        if candidate.get("missing_required_fields"):
            counts["needs_review_missing_required"] += 1
        if candidate.get("review_required_fields"):
            counts["needs_review_probable_or_low_confidence"] += 1
    return _counter_to_dict(counts)


def _build_promotion_blockers(knowledge_objects_report: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    blockers: list[dict[str, Any]] = []
    for candidate in _iter_object_candidates(knowledge_objects_report):
        readiness = str(candidate.get("readiness") or "needs_review")
        if readiness == "ready":
            continue
        blockers.append(
            {
                "object_type": str(candidate.get("object_type") or "unknown"),
                "readiness": readiness,
                "missing_required_count": len(tuple(candidate.get("missing_required_fields") or ())),
                "review_required_count": len(tuple(candidate.get("review_required_fields") or ())),
                "conflicting_count": len(tuple(candidate.get("conflicting_fields") or ())),
            }
        )
    blockers.sort(key=lambda item: (item["readiness"], item["object_type"]))
    return tuple(blockers[:20])


def _iter_object_candidates(knowledge_objects_report: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for package in knowledge_objects_report.get("reports", []):
        for candidate in package.get("object_candidates", []):
            yield dict(candidate)


def _rank_field_status(field_coverage: dict[str, dict[str, Any]], status: str) -> tuple[dict[str, Any], ...]:
    ranked = [
        {"field_name": field, "count": int(counts.get(status, 0)), "attempted": int(counts.get("attempted", 0))}
        for field, counts in field_coverage.items()
        if int(counts.get(status, 0)) > 0
    ]
    ranked.sort(key=lambda item: (-item["count"], item["field_name"]))
    return tuple(ranked[:10])


def _rank_low_confidence(field_coverage: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    ranked = [
        {
            "field_name": field,
            "count": int(counts.get("low_confidence", 0) + counts.get("needs_review", 0)),
            "attempted": int(counts.get("attempted", 0)),
        }
        for field, counts in field_coverage.items()
        if int(counts.get("low_confidence", 0) + counts.get("needs_review", 0)) > 0
    ]
    ranked.sort(key=lambda item: (-item["count"], item["field_name"]))
    return tuple(ranked[:10])


def _build_redacted_examples(
    report_candidates: Iterable[dict[str, Any]],
    report_facts: Iterable[dict[str, Any]],
) -> tuple[dict[str, Any], ...]:
    examples: list[dict[str, Any]] = []
    for package in report_facts:
        for fact in package.get("facts", []):
            status = str(fact.get("verification_status") or "")
            confidence = str(fact.get("confidence") or "")
            if status not in {"probable", "conflicting", "needs_review"} and confidence not in {"low", "conflicting"}:
                continue
            examples.append(_redacted_fact_example(fact))
            if len(examples) >= EXAMPLE_LIMIT:
                return tuple(examples)

    for candidate in report_candidates:
        for field, values in dict(candidate.get("fields", {})).items():
            for item in values or ():
                if item.get("confidence") == "missing":
                    continue
                examples.append(
                    {
                        "field_name": str(field),
                        "verification_status": "candidate_only",
                        "confidence": str(item.get("confidence") or "unknown"),
                        "value_profile": _value_profile(item.get("value"), str(field)),
                    }
                )
                if len(examples) >= EXAMPLE_LIMIT:
                    return tuple(examples)
    return tuple(examples)


def _redacted_fact_example(fact: dict[str, Any]) -> dict[str, Any]:
    value = fact.get("verified_value")
    if value in (None, ""):
        evidence = tuple(fact.get("conflicting_evidence", ())) or tuple(fact.get("supporting_evidence", ()))
        value = evidence[0].get("value") if evidence else None
    return {
        "field_name": str(fact.get("field_name") or "unknown"),
        "verification_status": str(fact.get("verification_status") or "unknown"),
        "confidence": str(fact.get("confidence") or "unknown"),
        "value_profile": _value_profile(value, str(fact.get("field_name") or "")),
    }


def _value_profile(value: Any, field_name: str) -> dict[str, str | None]:
    if value in (None, ""):
        return {"value_type": "missing", "length_bucket": "0", "year": None, "fingerprint": None}
    text = str(value)
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    year = _year_from_value(text) if field_name.endswith("_date") else None
    return {
        "value_type": _value_type(field_name, text),
        "length_bucket": _length_bucket(len(text)),
        "year": year,
        "fingerprint": hashlib.sha256(f"falcon-coverage-v1|{normalized}".encode("utf-8")).hexdigest()[:10],
    }


def _value_type(field_name: str, value: str) -> str:
    if field_name.endswith("_date"):
        return "date-like"
    if field_name in {"client", "intended_user", "appraiser_name", "reviewer_name"}:
        return "party-or-person"
    if field_name == "property_address":
        return "address-like"
    if value.lower() == "present":
        return "presence-indicator"
    return "short-text"


def _length_bucket(length: int) -> str:
    if length == 0:
        return "0"
    if length <= 12:
        return "1-12"
    if length <= 32:
        return "13-32"
    if length <= 80:
        return "33-80"
    return "81+"


def _year_from_value(value: str) -> str | None:
    match = re.search(r"\b(19|20)\d{2}\b", value)
    return match.group(0) if match else None


def _warning_type(value: str) -> str:
    normalized = value.lower()
    normalized = re.sub(r"^[a-f0-9]{8,40}:\s*", "", normalized)
    normalized = re.sub(r"[a-z]:\\[^:]+", "<path>", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if "pypdf is not installed" in normalized:
        return "pdf_text_library_missing"
    if "python-docx is not installed" in normalized:
        return "docx_text_library_missing"
    if "no embedded" in normalized or "no searchable" in normalized:
        return "no_searchable_text"
    if "source pdf path does not exist" in normalized:
        return "source_pdf_missing"
    if "skipped non-pdf likely final report" in normalized:
        return "non_pdf_final_report_skipped"
    if "conflicting" in normalized:
        return "conflicting_candidate_values"
    if "not found" in normalized or "not detected" in normalized:
        return "field_or_section_missing"
    return normalized[:80] or "unknown_warning"


def _add_warning_observation(observations: set[tuple[str, str]], value: Any, context: str | None = None) -> None:
    if not value:
        return
    text = str(value)
    observations.add((_warning_type(text), context or _warning_context(text)))


def _warning_context(value: str) -> str:
    match = re.match(r"^([a-f0-9]{8,40}):\s*", value.lower())
    if match:
        return match.group(1)
    return "global"


def _recommend_next_targets(field_coverage: dict[str, dict[str, Any]], warning_type_counts: dict[str, int]) -> tuple[str, ...]:
    targets: list[str] = []
    missing_rank = _rank_field_status(field_coverage, "missing")
    low_rank = _rank_low_confidence(field_coverage)
    if warning_type_counts.get("pdf_text_library_missing"):
        targets.append("Install or vendor-review local PDF text extraction support before expanding PDF coverage.")
    if warning_type_counts.get("docx_text_library_missing"):
        targets.append("Install or vendor-review local DOCX text extraction support before deciding OCR is required.")
    if warning_type_counts.get("no_searchable_text"):
        targets.append("Separate searchable PDFs from scanned PDFs; keep OCR behind the production readiness gate.")
    if missing_rank:
        fields = ", ".join(item["field_name"] for item in missing_rank[:5])
        targets.append(f"Add deterministic label variants for commonly missing fields: {fields}.")
    missing_approaches = [field for field in APPROACH_FIELDS if field_coverage.get(field, {}).get("missing", 0)]
    if missing_approaches:
        targets.append("Improve approach-section detection for sales comparison, income, and cost approach language.")
    if low_rank:
        fields = ", ".join(item["field_name"] for item in low_rank[:5])
        targets.append(f"Add independent corroboration rules for probable or low-confidence fields: {fields}.")
    if field_coverage.get("client", {}).get("conflicting", 0) or field_coverage.get("intended_user", {}).get("conflicting", 0):
        targets.append("Differentiate client, intended user, owner, and borrower labels before promotion.")
    return tuple(dict.fromkeys(targets))


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted((key, int(value)) for key, value in counter.items()))


def _markdown_count_lines(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- None"]
    return [f"- {label}: {count}" for label, count in sorted(counts.items())]


def _ranked_field_lines(items: tuple[dict[str, Any], ...]) -> list[str]:
    if not items:
        return ["- None"]
    return [f"- {item['field_name']}: {item['count']} of {item['attempted']}" for item in items]


def _compact_machine_summary(payload: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "source_file_count",
        "candidate_final_report_count",
        "analyzed_report_count",
        "verification_status_distribution",
        "confidence_distribution",
        "conflict_count",
        "warning_type_counts",
        "approach_indicators",
        "conflict_fields_by_type",
        "readiness_reason_counts",
        "promotion_field_summary",
        "common_missing_fields",
        "common_low_confidence_fields",
        "next_parsing_targets",
    )
    return {key: payload[key] for key in keys}
