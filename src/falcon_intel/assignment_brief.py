"""Deterministic Assignment/Property Brief V1 built from canonical AIR facts.

The brief is a compact appraisal-production handoff. It never promotes a
candidate, invents a missing fact, or produces a professional conclusion.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from falcon_intel.assignment_intelligence_record import AssignmentIntelligenceRecord
from falcon_intel.schema_registry import ASSIGNMENT_PROPERTY_BRIEF_SCHEMA_VERSION


ASSIGNMENT_FIELD_ORDER = (
    "assignment.client",
    "assignment.intended_user",
    "assignment.intended_use",
    "assignment.appraisal_purpose",
    "assignment.interest_appraised",
    "assignment.effective_date_requirement",
    "assignment.report_date_requirement",
    "assignment.due_date",
    "assignment.report_format",
    "assignment.inspection_requirements",
    "assignment.inspection_date",
    "assignment.engagement_constraints",
    "assignment.signing_appraiser",
    "assignment.reviewer",
)

SUBJECT_FIELD_ORDER = (
    "subject.name",
    "subject.address",
    "subject.parcel_identifiers",
    "subject.property_type",
    "subject.property_subtype",
    "subject.site_area",
    "subject.building_area",
    "subject.year_built",
    "subject.units",
    "subject.occupancy",
    "subject.tenancy",
    "subject.zoning",
    "subject.taxes",
    "subject.ownership",
    "subject.sale_history",
    "subject.renovation_history",
    "subject.construction",
    "subject.condition",
    "subject.parking",
    "subject.income",
    "subject.operating_information",
)

IGNORED_LOCAL_OUTPUT_ROOTS = {"data", "exports", "local-data", "local_data"}


@dataclass(frozen=True)
class BriefFact:
    """One current AIR fact shown in the brief."""

    fact_id: str
    field_key: str
    label: str
    value: Any
    value_type: str
    unit: str | None
    fact_state: str
    origin: str
    professional_boundary: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class BriefEvidenceCitation:
    """Traceable metadata-only citation for one or more brief facts."""

    evidence_id: str
    fact_ids: tuple[str, ...]
    source_id: str
    source_document: str
    safe_reference: str
    locator: dict[str, Any]
    extraction_method: str
    confidence: str
    quality: str
    freshness: str


@dataclass(frozen=True)
class BriefIssue:
    """One readiness or review issue requiring attention."""

    issue_id: str
    area: str
    issue_type: str
    severity: str
    field_keys: tuple[str, ...]
    related_ids: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class BriefReadinessArea:
    """Practical readiness status for one appraisal area."""

    area: str
    status: str
    issue_ids: tuple[str, ...]


@dataclass(frozen=True)
class BriefLead:
    """Reference-only comparable or market lead."""

    reference_id: str
    lead_type: str
    relationship: str
    selection_status: str
    freshness: str
    evidence_ids: tuple[str, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class AssignmentPropertyBrief:
    """Versioned, deterministic projection of one Assignment Intelligence Record."""

    brief_format: str
    brief_version: str
    air_schema_version: str
    air_record_id: str
    air_record_version: int
    generated_at: str
    assignment_synopsis: tuple[BriefFact, ...]
    assignment_contacts: tuple[dict[str, str], ...]
    subject_synopsis: tuple[BriefFact, ...]
    ownership_references: tuple[dict[str, str], ...]
    issues_requiring_attention: tuple[BriefIssue, ...]
    evidence_summary: tuple[BriefEvidenceCitation, ...]
    comparable_and_market_leads: tuple[BriefLead, ...]
    readiness_status: str
    readiness_areas: tuple[BriefReadinessArea, ...]
    professional_conclusions: tuple[dict[str, Any], ...]
    professional_boundary: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-ready brief payload."""

        return asdict(self)

    def to_json(self) -> str:
        """Return deterministic, newline-terminated JSON."""

        return json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    def to_markdown(self) -> str:
        """Render a deterministic appraiser-facing Markdown brief."""

        lines = [
            "# Assignment / Property Brief",
            "",
            f"- Brief format: `{self.brief_format}` v{self.brief_version}",
            f"- AIR: `{self.air_record_id}` v{self.air_record_version} (schema {self.air_schema_version})",
            f"- Generated: {self.generated_at}",
            f"- Readiness: **{_title(self.readiness_status)}**",
            "",
            "## Assignment Synopsis",
            "",
        ]
        lines.extend(_fact_lines(self.assignment_synopsis))
        if self.assignment_contacts:
            lines.extend(["", "### Assignment Contacts", ""])
            lines.extend(
                f"- {item['display_label']} (`{item['reference_id']}`)"
                for item in self.assignment_contacts
            )
        lines.extend(["", "## Subject Synopsis", ""])
        lines.extend(_fact_lines(self.subject_synopsis))
        if self.ownership_references:
            lines.extend(["", "### Ownership References", ""])
            lines.extend(
                f"- {item['display_label']} (`{item['reference_id']}`)"
                for item in self.ownership_references
            )
        lines.extend(["", "## Issues Requiring Attention", ""])
        if self.issues_requiring_attention:
            lines.extend(
                f"- **{_title(item.severity)} — {_title(item.area)}:** {item.message}"
                for item in self.issues_requiring_attention
            )
        else:
            lines.append("- No current AIR readiness issues.")
        lines.extend(["", "## Readiness by Appraisal Area", ""])
        lines.extend(
            f"- {_title(item.area)}: **{_title(item.status)}** ({len(item.issue_ids)} issue(s))"
            for item in self.readiness_areas
        )
        lines.extend(["", "## Evidence Summary", ""])
        if self.evidence_summary:
            for item in self.evidence_summary:
                locator = _locator_label(item.locator)
                lines.append(
                    f"- `{item.evidence_id}` — {item.source_document}; {locator}; "
                    f"{item.extraction_method}; confidence {_title(item.confidence)}; "
                    f"supports {', '.join(f'`{fact_id}`' for fact_id in item.fact_ids)}."
                )
        else:
            lines.append("- No source evidence is attached to the current brief facts.")
        lines.extend(["", "## Comparable and Market Leads", ""])
        if self.comparable_and_market_leads:
            for item in self.comparable_and_market_leads:
                lines.append(
                    f"- `{item.reference_id}` — {_title(item.lead_type)}; "
                    f"{_title(item.selection_status)}; {_title(item.relationship)}."
                )
        else:
            lines.append("- No comparable or market leads are referenced by the AIR.")
        lines.extend(
            [
                "",
                "> Leads are references only. Extraction does not constitute professional comparable selection.",
                "",
                "## Professional Boundary",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in self.professional_boundary)
        if self.professional_conclusions:
            lines.extend(["", "### Explicit Appraiser Conclusions", ""])
            lines.extend(
                f"- {_title(str(item['conclusion_type']))}: {item['statement']} "
                f"({_title(str(item['status']))})"
                for item in self.professional_conclusions
            )
        else:
            lines.extend(["", "- No professional conclusions are included in this brief."])
        return "\n".join(lines) + "\n"


def build_assignment_property_brief(
    record: AssignmentIntelligenceRecord,
) -> AssignmentPropertyBrief:
    """Build Brief V1 solely from the current canonical AIR state."""

    current_ids = set(record.current_fact_ids)
    current_facts = {
        fact.field_key: fact for fact in record.facts if fact.fact_id in current_ids
    }
    assignment = tuple(
        _brief_fact(current_facts[key]) for key in ASSIGNMENT_FIELD_ORDER if key in current_facts
    )
    subject = tuple(
        _brief_fact(current_facts[key]) for key in SUBJECT_FIELD_ORDER if key in current_facts
    )
    included_fact_ids = {
        item.fact_id
        for item in (*assignment, *subject)
    }
    evidence_to_facts: dict[str, list[str]] = {}
    for fact in current_facts.values():
        if fact.fact_id not in included_fact_ids and not fact.material:
            continue
        for evidence_id in fact.evidence_ids:
            evidence_to_facts.setdefault(evidence_id, []).append(fact.fact_id)
    source_by_id = {source.source_id: source for source in record.sources}
    evidence_summary = []
    for evidence in sorted(record.evidence, key=lambda item: item.evidence_id):
        fact_ids = evidence_to_facts.get(evidence.evidence_id)
        if not fact_ids:
            continue
        source = source_by_id[evidence.source_id]
        evidence_summary.append(
            BriefEvidenceCitation(
                evidence_id=evidence.evidence_id,
                fact_ids=tuple(sorted(fact_ids)),
                source_id=source.source_id,
                source_document=source.display_label,
                safe_reference=source.safe_reference,
                locator=asdict(evidence.locator),
                extraction_method=evidence.extraction_method,
                confidence=evidence.confidence,
                quality=evidence.quality,
                freshness=evidence.freshness,
            )
        )
    leads = [
        BriefLead(
            reference_id=item.reference_id,
            lead_type=f"comparable_{item.comparable_type}",
            relationship="assignment_comparable_reference",
            selection_status=item.selection_status,
            freshness=item.freshness,
            evidence_ids=item.evidence_ids,
            notes=item.notes,
        )
        for item in record.comparable_references
    ]
    leads.extend(
        BriefLead(
            reference_id=item.reference_id,
            lead_type=item.reference_type,
            relationship=item.relationship,
            selection_status="reference_only",
            freshness=item.freshness,
            evidence_ids=item.evidence_ids,
            notes=item.notes,
        )
        for item in record.market_references
    )
    return AssignmentPropertyBrief(
        brief_format="assignment_property_brief",
        brief_version=ASSIGNMENT_PROPERTY_BRIEF_SCHEMA_VERSION,
        air_schema_version=record.identity.schema_version,
        air_record_id=record.identity.record_id,
        air_record_version=record.identity.record_version,
        generated_at=record.identity.updated_at,
        assignment_synopsis=assignment,
        assignment_contacts=tuple(
            asdict(item) for item in record.assignment_context.contact_references
        ),
        subject_synopsis=subject,
        ownership_references=tuple(
            asdict(item) for item in record.subject_property.ownership_references
        ),
        issues_requiring_attention=tuple(
            BriefIssue(**asdict(item)) for item in record.readiness.issues
        ),
        evidence_summary=tuple(evidence_summary),
        comparable_and_market_leads=tuple(sorted(leads, key=lambda item: item.reference_id)),
        readiness_status=record.readiness.overall_status,
        readiness_areas=tuple(
            BriefReadinessArea(
                area=item.area,
                status=item.status,
                issue_ids=item.issue_ids,
            )
            for item in record.readiness.areas
        ),
        professional_conclusions=tuple(asdict(item) for item in record.conclusions),
        professional_boundary=(
            "Verified and corrected facts come only from explicit AIR review events.",
            "Appraiser-entered facts are identified by their AIR origin and review event.",
            "Unresolved observations remain issues and are not presented as facts.",
            "Professional conclusions are separate and are never inferred from readiness.",
            "This brief does not provide a value conclusion, highest and best use conclusion, "
            "comparable selection, adjustment, capitalization rate, or appraisal narrative.",
        ),
    )


def export_assignment_property_brief(
    record: AssignmentIntelligenceRecord,
    brief: AssignmentPropertyBrief,
    output_directory: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> dict[str, str]:
    """Write deterministic AIR JSON, brief JSON, and Markdown to a safe local directory."""

    output_dir = validate_local_output_directory(
        output_directory,
        repository_root=repository_root,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "air_json": output_dir / "assignment-intelligence-record-v1.json",
        "brief_json": output_dir / "assignment-property-brief-v1.json",
        "brief_markdown": output_dir / "assignment-property-brief-v1.md",
    }
    paths["air_json"].write_text(record.to_json(), encoding="utf-8")
    paths["brief_json"].write_text(brief.to_json(), encoding="utf-8")
    paths["brief_markdown"].write_text(brief.to_markdown(), encoding="utf-8")
    return {key: str(value) for key, value in paths.items()}


def validate_local_output_directory(
    output_directory: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> Path:
    """Reject tracked repository destinations while allowing ignored local roots."""

    raw = Path(output_directory)
    if not str(raw).strip():
        raise ValueError("An explicit output directory is required.")
    output_dir = raw.expanduser().resolve()
    repo_root = Path(repository_root or Path(__file__).resolve().parents[2]).resolve()
    try:
        relative = output_dir.relative_to(repo_root)
    except ValueError:
        return output_dir
    if not relative.parts or relative.parts[0] not in IGNORED_LOCAL_OUTPUT_ROOTS:
        raise ValueError(
            "Brief exports inside the repository must use an ignored local output root: "
            "data/, exports/, local-data/, or local_data/."
        )
    return output_dir


def _brief_fact(fact: Any) -> BriefFact:
    boundary = {
        "verified_candidate": "verified_fact",
        "corrected_candidate": "corrected_fact",
        "appraiser_entry": "appraiser_entered_fact",
    }.get(fact.origin, "explicit_air_fact")
    return BriefFact(
        fact_id=fact.fact_id,
        field_key=fact.field_key,
        label=fact.label,
        value=fact.value,
        value_type=fact.value_type,
        unit=fact.unit,
        fact_state=fact.state,
        origin=fact.origin,
        professional_boundary=boundary,
        evidence_ids=fact.evidence_ids,
    )


def _fact_lines(facts: Iterable[BriefFact]) -> list[str]:
    rows = list(facts)
    if not rows:
        return ["- No current AIR facts are available for this section."]
    return [
        f"- **{item.label}:** {_value_label(item.value, item.unit)} "
        f"— {_title(item.professional_boundary)} (`{item.fact_id}`)"
        for item in rows
    ]


def _value_label(value: Any, unit: str | None) -> str:
    if isinstance(value, (dict, list)):
        rendered = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        rendered = str(value)
    return f"{rendered} {_title(unit)}" if unit else rendered


def _locator_label(locator: dict[str, Any]) -> str:
    labels = []
    for key in ("page_number", "section", "table", "cell", "paragraph", "region"):
        value = locator.get(key)
        if value not in {None, ""}:
            labels.append(f"{_title(key)} {value}")
    return ", ".join(labels) if labels else "source-level locator"


def _title(value: str | None) -> str:
    return str(value or "unknown").replace("_", " ").title()
