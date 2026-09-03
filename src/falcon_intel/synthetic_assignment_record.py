"""Synthetic end-to-end proof for Assignment Intelligence Record V1."""

from __future__ import annotations

from falcon_intel.assignment_intelligence_record import (
    AppraiserFactInput,
    AssignmentIntelligenceRecord,
    ComparableReference,
    EntityReference,
    KnowledgeReference,
    build_assignment_intelligence_record,
    build_candidate_evidence_bundle,
    build_candidate_review_event,
)
from falcon_intel.historical_knowledge import PageText, extract_report_metadata_from_pages


SYNTHETIC_TIMESTAMP = "2026-09-03T14:00:00+00:00"


def build_synthetic_assignment_intelligence_record() -> AssignmentIntelligenceRecord:
    """Run synthetic pages through extraction, review, and canonical assembly."""

    extracted = extract_report_metadata_from_pages(
        (
            PageText(
                page_number=1,
                text="""
                SYNTHETIC APPRAISAL INTAKE
                Restricted Appraisal Report
                Property Address: 800 Meridian Commerce Drive
                Property Type: Industrial
                Client: Example Regional Bank
                Intended User: Example Regional Bank
                Intended Use: Loan underwriting
                Effective Date: September 1, 2026
                Report Date: September 3, 2026
                Appraiser: Avery Jordan, MAI
                Reviewer: Riley Morgan, MAI

                Summary of Salient Facts
                Property Address: 800 Meridian Commerce Drive
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
                SYNTHETIC ENGAGEMENT NOTE
                Intended Use: Internal portfolio planning
                Extraordinary Assumptions
                No valuation conclusion is included in this synthetic source.
                """,
            ),
        ),
        file_id="synthetic-air-final-report",
        file_path="synthetic/assignment-intelligence-record/final-report.pdf",
        file_name="Restricted Appraisal Report.pdf",
    )
    bundle = build_candidate_evidence_bundle(
        extracted,
        extracted_at=SYNTHETIC_TIMESTAMP,
        extractor_version="1",
    )
    by_field = _candidates_by_field(bundle.candidates)
    reviews = (
        _review(by_field["assignment.client"][0], "candidate_verified", "Client confirmed from synthetic intake."),
        _review(
            by_field["assignment.intended_user"][0],
            "candidate_verified",
            "Intended user confirmed from synthetic intake.",
        ),
        _review(
            by_field["assignment.effective_date_requirement"][0],
            "candidate_verified",
            "Effective-date requirement confirmed by the synthetic appraiser.",
        ),
        _review(
            by_field["assignment.report_format"][0],
            "candidate_verified",
            "Report format confirmed from the synthetic title during review.",
            actor_id="user-synthetic-reviewer-001",
            actor_name="Robin Reviewer",
            actor_role="reviewer",
        ),
        _review(
            by_field["assignment.signing_appraiser"][0],
            "candidate_verified",
            "Signing appraiser confirmed for the synthetic assignment.",
        ),
        _review(
            by_field["subject.address"][0],
            "candidate_verified",
            "Subject address confirmed against the synthetic assignment setup.",
        ),
        _review(
            by_field["subject.property_type"][0],
            "candidate_corrected",
            "Appraiser refined the broad extracted type to the assignment subtype.",
            corrected_value="Industrial / Warehouse",
        ),
        _review(
            by_field["assignment.reviewer"][0],
            "candidate_rejected",
            "Named reviewer is historical source metadata and is not assigned to the current engagement.",
        ),
    )
    appraiser_facts = (
        _appraiser_fact(
            "assignment.interest_appraised",
            "Interest appraised",
            "assignment",
            "Leased fee interest",
            "Professional assignment condition entered by the appraiser.",
        ),
        _appraiser_fact(
            "assignment.inspection_requirements",
            "Inspection requirements",
            "assignment",
            "Exterior and interior inspection required",
            "Inspection scope entered from the synthetic engagement setup.",
        ),
        _appraiser_fact(
            "subject.site_area",
            "Site area",
            "site",
            6.25,
            "Synthetic site area entered by the appraiser for review.",
            value_type="number",
            unit="acres",
        ),
        _appraiser_fact(
            "subject.building_area",
            "Building area",
            "improvements",
            48000,
            "Synthetic gross building area entered by the appraiser for review.",
            value_type="integer",
            unit="square_feet",
        ),
    )
    return build_assignment_intelligence_record(
        tenant_id="tenant-synthetic-appraisal-firm",
        local_assignment_key="synthetic-assignment-air-v1",
        falcon_assignment_reference=EntityReference(
            reference_id="falcon-order-synthetic-air-001",
            reference_type="falcon_assignment",
            display_label="Synthetic Falcon assignment AIR-001",
            source_system="falcon",
        ),
        candidate_bundles=(bundle,),
        review_events=reviews,
        appraiser_facts=appraiser_facts,
        property_reference=EntityReference(
            reference_id="prop-synthetic-meridian-800",
            reference_type="property",
            display_label="800 Meridian Commerce Drive",
            source_system="falcon_intelligence_property_library",
        ),
        assignment_contacts=(
            EntityReference(
                reference_id="contact-synthetic-bank-reviewer",
                reference_type="assignment_contact",
                display_label="Synthetic bank review contact",
                source_system="falcon",
            ),
        ),
        ownership_references=(
            EntityReference(
                reference_id="owner-synthetic-meridian-holdings",
                reference_type="ownership_entity",
                display_label="Synthetic Meridian Holdings LLC",
                source_system="falcon_intelligence",
            ),
        ),
        comparable_references=(
            ComparableReference(
                reference_id="comp-ref-synthetic-sale-001",
                comparable_id="sale-comp-synthetic-001",
                comparable_type="sale",
                selection_status="selected",
                property_id="prop-synthetic-sale-001",
                knowledge_object_id="ko-synthetic-sale-001",
                evidence_ids=(),
                freshness="current",
                notes=("Reference only; no automated selection or adjustment conclusion.",),
            ),
            ComparableReference(
                reference_id="comp-ref-synthetic-lease-001",
                comparable_id="lease-comp-synthetic-001",
                comparable_type="lease",
                selection_status="candidate",
                property_id="prop-synthetic-lease-001",
                evidence_ids=(),
                freshness="unknown",
                notes=("Candidate reference remains subject to appraiser selection.",),
            ),
        ),
        market_references=(
            KnowledgeReference(
                reference_id="market-observation-synthetic-industrial-001",
                reference_type="market_observation",
                relationship="assignment_market_context",
                freshness="current",
                notes=("Synthetic reference only; observation body remains outside this record.",),
            ),
        ),
        prior_knowledge_references=(
            KnowledgeReference(
                reference_id="ko-synthetic-prior-property-001",
                reference_type="knowledge_object",
                relationship="prior_firm_property_knowledge",
                freshness="aging",
                notes=("Referenced, not copied; reverification is required before reuse.",),
            ),
        ),
        created_at=SYNTHETIC_TIMESTAMP,
        updated_at="2026-09-03T14:30:00+00:00",
    )


def _candidates_by_field(candidates: tuple) -> dict[str, list]:
    output: dict[str, list] = {}
    for candidate in candidates:
        output.setdefault(candidate.field_key, []).append(candidate)
    return output


def _review(
    candidate,
    action: str,
    reason: str,
    *,
    corrected_value=None,
    actor_id: str = "user-synthetic-appraiser-001",
    actor_name: str = "Alex Appraiser",
    actor_role: str = "appraiser",
):
    return build_candidate_review_event(
        candidate,
        action=action,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        occurred_at="2026-09-03T14:15:00+00:00",
        reason=reason,
        corrected_value=corrected_value,
    )


def _appraiser_fact(
    field_key: str,
    label: str,
    category: str,
    value,
    reason: str,
    *,
    value_type: str = "string",
    unit: str | None = None,
) -> AppraiserFactInput:
    return AppraiserFactInput(
        field_key=field_key,
        label=label,
        category=category,
        value=value,
        value_type=value_type,
        unit=unit,
        material=True,
        actor_id="user-synthetic-appraiser-001",
        actor_name="Alex Appraiser",
        actor_role="appraiser",
        occurred_at="2026-09-03T14:20:00+00:00",
        reason=reason,
    )
