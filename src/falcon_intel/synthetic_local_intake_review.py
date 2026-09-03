"""Complete synthetic Local Intake Review to Assignment Brief V1 proof."""

from __future__ import annotations

from dataclasses import dataclass

from falcon_intel.assignment_brief import AssignmentPropertyBrief, build_assignment_property_brief
from falcon_intel.assignment_intelligence_record import (
    AssignmentIntelligenceRecord,
    ComparableReference,
    EntityReference,
    KnowledgeReference,
    ReadinessRequirement,
    build_candidate_evidence_bundle,
)
from falcon_intel.historical_knowledge import PageText, extract_report_metadata_from_pages
from falcon_intel.local_intake_review import (
    LocalIntakeReviewSession,
    ReviewActor,
    build_local_intake_review_workspace,
)


SYNTHETIC_REVIEW_CREATED_AT = "2026-09-03T15:00:00+00:00"
SYNTHETIC_REVIEW_ACTOR = ReviewActor(
    actor_id="user-synthetic-appraiser-brief-001",
    actor_name="Morgan Appraiser",
    actor_role="appraiser",
)

INTAKE_READINESS_REQUIREMENTS = (
    ReadinessRequirement(
        area="assignment_context",
        field_keys=(
            "assignment.client",
            "assignment.intended_user",
            "assignment.intended_use",
            "assignment.appraisal_purpose",
            "assignment.interest_appraised",
            "assignment.effective_date_requirement",
        ),
        blocking=True,
    ),
    ReadinessRequirement(
        area="subject_identity",
        field_keys=("subject.address", "subject.property_type"),
        blocking=True,
    ),
    ReadinessRequirement(area="site", field_keys=("subject.site_area",), blocking=False),
    ReadinessRequirement(
        area="improvements", field_keys=("subject.building_area",), blocking=False
    ),
    ReadinessRequirement(
        area="income_and_occupancy", field_keys=("subject.occupancy",), blocking=False
    ),
    ReadinessRequirement(
        area="professional_review",
        field_keys=("assignment.signing_appraiser",),
        blocking=False,
    ),
)


@dataclass(frozen=True)
class SyntheticLocalIntakeProof:
    """Artifacts produced by the deterministic vertical proof."""

    session: LocalIntakeReviewSession
    record: AssignmentIntelligenceRecord
    brief: AssignmentPropertyBrief
    workspace: dict


def build_synthetic_local_intake_review_proof() -> SyntheticLocalIntakeProof:
    """Extract, review, assemble, brief, and project one synthetic assignment."""

    report_bundle = build_candidate_evidence_bundle(
        extract_report_metadata_from_pages(
            (
                PageText(
                    page_number=1,
                    text="""
                    SYNTHETIC APPRAISAL INTAKE
                    Restricted Appraisal Report
                    Property Address: 1600 Northstar Logistics Way
                    Property Type: Industrial
                    Client: Example Regional Bank
                    Intended User: Example Regional Bank
                    Intended Use: Loan underwriting
                    Effective Date: September 1, 2026
                    Report Date: September 3, 2026
                    Inspection Date: August 29, 2026
                    Appraiser: Morgan Appraiser, MAI
                    Reviewer: Taylor Reviewer, MAI

                    Summary of Salient Facts
                    Property Address: 1600 Northstar Logistics Way
                    Property Type: Industrial
                    Client: Example Regional Bank
                    Intended User: Example Regional Bank
                    Effective Date: September 1, 2026
                    Scope of Work
                    The sales comparison approach and income approach are referenced.
                    """,
                ),
                PageText(
                    page_number=2,
                    text="""
                    SYNTHETIC ASSIGNMENT NOTE
                    Intended Use: Internal portfolio planning
                    Extraordinary Assumptions
                    No valuation conclusion is included in this synthetic source.
                    """,
                ),
            ),
            file_id="synthetic-intake-report-001",
            file_path="synthetic/local-intake-review/appraisal-report.pdf",
            file_name="Synthetic Northstar Appraisal Report.pdf",
        ),
        extracted_at=SYNTHETIC_REVIEW_CREATED_AT,
        extractor_version="1",
    )
    engagement_bundle = build_candidate_evidence_bundle(
        extract_report_metadata_from_pages(
            (
                PageText(
                    page_number=1,
                    text="""
                    SYNTHETIC ENGAGEMENT LETTER
                    Client: Example Regional Bank, N.A.
                    Effective Date: September 1, 2026
                    Property Address: 1600 Northstar Logistics Way
                    """,
                ),
            ),
            file_id="synthetic-engagement-letter-001",
            file_path="synthetic/local-intake-review/engagement-letter.docx",
            file_name="Synthetic Northstar Engagement Letter.docx",
        ),
        extracted_at=SYNTHETIC_REVIEW_CREATED_AT,
        extractor_version="1",
    )
    session = LocalIntakeReviewSession(
        tenant_id="tenant-synthetic-intake-review",
        local_assignment_key="synthetic-local-intake-review-001",
        candidate_bundles=(report_bundle, engagement_bundle),
        created_at=SYNTHETIC_REVIEW_CREATED_AT,
        updated_at=SYNTHETIC_REVIEW_CREATED_AT,
        falcon_assignment_reference=EntityReference(
            reference_id="falcon-order-synthetic-intake-001",
            reference_type="falcon_assignment",
            display_label="Synthetic Northstar Distribution Center assignment",
            source_system="falcon",
        ),
        property_reference=EntityReference(
            reference_id="property-synthetic-northstar-001",
            reference_type="property",
            display_label="Northstar Distribution Center",
            source_system="falcon_intelligence_property_library",
        ),
        assignment_contacts=(
            EntityReference(
                reference_id="contact-synthetic-jordan-client",
                reference_type="assignment_contact",
                display_label="Jordan Client Contact (synthetic)",
                source_system="falcon",
            ),
        ),
        ownership_references=(
            EntityReference(
                reference_id="owner-synthetic-northstar-holdings",
                reference_type="ownership_entity",
                display_label="Northstar Holdings LLC (synthetic)",
                source_system="falcon_intelligence",
            ),
        ),
        comparable_references=(
            ComparableReference(
                reference_id="comp-lead-synthetic-sale-101",
                comparable_id="synthetic-sale-101",
                comparable_type="sale",
                selection_status="candidate",
                property_id="property-synthetic-sale-101",
                freshness="current",
                notes=("Extracted reference only; not professionally selected.",),
            ),
            ComparableReference(
                reference_id="comp-lead-synthetic-lease-202",
                comparable_id="synthetic-lease-202",
                comparable_type="lease",
                selection_status="candidate",
                property_id="property-synthetic-lease-202",
                freshness="unknown",
                notes=("Market lead only; relevance remains subject to appraiser review.",),
            ),
        ),
        market_references=(
            KnowledgeReference(
                reference_id="market-lead-synthetic-logistics-001",
                reference_type="market_observation",
                relationship="assignment_market_lead",
                freshness="current",
                notes=("Synthetic reference without a market conclusion.",),
            ),
        ),
        readiness_requirements=INTAKE_READINESS_REQUIREMENTS,
    )

    initial_record = session.assemble_air()
    client_conflict = next(
        conflict
        for conflict in initial_record.conflicts
        if conflict.field_key == "assignment.client"
    )
    selected_client = next(
        candidate
        for candidate in initial_record.candidates
        if candidate.candidate_id in client_conflict.candidate_ids
        and candidate.value == "Example Regional Bank, N.A."
    )
    session = session.resolve_conflict(
        client_conflict.conflict_id,
        selected_client.candidate_id,
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:10:00+00:00",
        reason="Engagement letter controls the synthetic legal client name.",
    )
    current = session.assemble_air()
    session = session.accept(
        _candidate_id(current, "assignment.intended_user", source="report"),
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:11:00+00:00",
    )
    session = session.accept(
        _candidate_id(current, "assignment.effective_date_requirement", source="engagement"),
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:12:00+00:00",
    )
    session = session.accept(
        _candidate_id(current, "assignment.report_format", source="report"),
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:13:00+00:00",
    )
    session = session.accept(
        _candidate_id(current, "assignment.signing_appraiser", source="report"),
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:14:00+00:00",
    )
    session = session.accept(
        _candidate_id(current, "subject.address", source="engagement"),
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:15:00+00:00",
    )
    session = session.correct(
        _candidate_id(current, "subject.property_type", source="report"),
        "Industrial / Distribution Warehouse",
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:16:00+00:00",
        reason="Refined the broad extracted type using the synthetic assignment scope.",
    )
    session = session.reject(
        _candidate_id(current, "assignment.reviewer", source="report"),
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:17:00+00:00",
        reason="Historical report reviewer is not assigned to the current synthetic engagement.",
    )
    session = session.defer(
        _candidate_id(current, "assignment.report_date_requirement", source="report"),
        actor=SYNTHETIC_REVIEW_ACTOR,
        occurred_at="2026-09-03T15:18:00+00:00",
        reason="Report-date requirement awaits confirmation from the synthetic engagement team.",
    )

    manual_facts = (
        (
            "assignment.interest_appraised",
            "Interest appraised",
            "assignment",
            "Leased fee interest",
            "string",
            None,
            "Entered by the appraiser from the synthetic engagement scope.",
        ),
        (
            "assignment.inspection_requirements",
            "Inspection requirements",
            "assignment",
            "Interior and exterior inspection required",
            "string",
            None,
            "Appraiser-entered synthetic inspection scope.",
        ),
        (
            "assignment.engagement_constraints",
            "Engagement constraints",
            "assignment",
            "Reliance limited to the named client and intended user",
            "string",
            None,
            "Appraiser-entered synthetic engagement constraint.",
        ),
        (
            "subject.name",
            "Property name",
            "subject_identity",
            "Northstar Distribution Center",
            "string",
            None,
            "Appraiser-entered synthetic property identity.",
        ),
        (
            "subject.parcel_identifiers",
            "Parcel identifiers",
            "subject_identity",
            ["SYN-440-22-018"],
            "array",
            None,
            "Appraiser-entered synthetic parcel identifier.",
        ),
        (
            "subject.site_area",
            "Site area",
            "site",
            12.4,
            "number",
            "acres",
            "Appraiser-entered synthetic site measurement.",
        ),
        (
            "subject.building_area",
            "Building area",
            "improvements",
            186500,
            "integer",
            "square_feet",
            "Appraiser-entered synthetic gross building area.",
        ),
        (
            "subject.year_built",
            "Year built",
            "improvements",
            2008,
            "integer",
            None,
            "Appraiser-entered synthetic year built.",
        ),
        (
            "subject.occupancy",
            "Occupancy",
            "economic_operational",
            "Single-tenant occupied",
            "string",
            None,
            "Appraiser-entered synthetic occupancy observation.",
        ),
        (
            "subject.zoning",
            "Zoning",
            "physical_legal",
            "LI — Light Industrial (synthetic)",
            "string",
            None,
            "Appraiser-entered synthetic zoning fact.",
        ),
        (
            "subject.taxes",
            "Taxes",
            "economic_operational",
            {"tax_year": 2026, "amount": 148200, "currency": "USD"},
            "object",
            None,
            "Appraiser-entered synthetic tax fact.",
        ),
    )
    for index, (field_key, label, category, value, value_type, unit, reason) in enumerate(
        manual_facts,
        start=20,
    ):
        session = session.add_fact(
            field_key=field_key,
            label=label,
            category=category,
            value=value,
            value_type=value_type,
            unit=unit,
            material=True,
            actor=SYNTHETIC_REVIEW_ACTOR,
            occurred_at=f"2026-09-03T15:{index:02d}:00+00:00",
            reason=reason,
        )

    record = session.assemble_air()
    brief = build_assignment_property_brief(record)
    return SyntheticLocalIntakeProof(
        session=session,
        record=record,
        brief=brief,
        workspace=build_local_intake_review_workspace(record, brief),
    )


def _candidate_id(
    record: AssignmentIntelligenceRecord,
    field_key: str,
    *,
    source: str,
) -> str:
    source_by_id = {item.source_id: item for item in record.sources}
    evidence_by_id = {item.evidence_id: item for item in record.evidence}
    token = "engagement" if source == "engagement" else "appraisal-report"
    return next(
        candidate.candidate_id
        for candidate in record.candidates
        if candidate.field_key == field_key
        and any(
            token in source_by_id[evidence_by_id[evidence_id].source_id].safe_reference.lower()
            for evidence_id in candidate.evidence_ids
        )
    )
