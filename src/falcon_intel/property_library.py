"""Synthetic Property Library and Controlled Comp Vault preview workflows."""

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Literal


VerificationStatus = Literal["unverified", "needs_review", "verified", "locked"]
EvidenceEventType = Literal[
    "sale",
    "lease_rent",
    "expense",
    "cap_rate",
    "assessment_tax",
    "subject_assignment",
]
ReportUsageRole = Literal[
    "subject_property",
    "sale_comparable",
    "rental_comparable",
    "expense_comparable",
    "cap_rate_support",
    "narrative_reference",
]
CandidateReviewStatus = Literal["candidate", "needs_review", "approved", "rejected", "merged"]


@dataclass(frozen=True)
class PropertyRecord:
    """Canonical synthetic property identity for library and comp vault views."""

    property_id: str
    canonical_name: str
    address: str
    city: str
    county: str
    state: str
    property_type: str
    subtype: str
    latitude: float
    longitude: float
    building_size_sf: int
    site_size_acres: float
    year_built: int | None
    condition: str
    zoning: str
    verification_status: VerificationStatus

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceEvent:
    """One synthetic evidence event tied to a canonical property."""

    event_id: str
    property_id: str
    event_type: EvidenceEventType
    event_date: str
    summary: str
    amount: float | None
    unit: str
    source: str
    confidence: int
    verification_status: VerificationStatus

    def __post_init__(self) -> None:
        if self.confidence < 0 or self.confidence > 100:
            raise ValueError("Evidence confidence must be between 0 and 100.")
        date.fromisoformat(self.event_date)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReportUsage:
    """Synthetic record of how a property was used in a report/order."""

    usage_id: str
    property_id: str
    order_number: str
    report_label: str
    usage_role: ReportUsageRole
    effective_date: str
    appraiser: str
    notes: str

    def __post_init__(self) -> None:
        date.fromisoformat(self.effective_date)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateMatch:
    """Synthetic normalization candidate for possible duplicate/conflicting data."""

    match_id: str
    property_ids: tuple[str, ...]
    conflict_type: str
    summary: str
    conflicting_fields: dict[str, list[str | int | float]]
    confidence_score: int
    review_status: CandidateReviewStatus

    def __post_init__(self) -> None:
        if self.confidence_score < 0 or self.confidence_score > 100:
            raise ValueError("Candidate confidence score must be between 0 and 100.")
        if len(self.property_ids) < 2:
            raise ValueError("Candidate matches must compare at least two property records.")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["property_ids"] = list(self.property_ids)
        return payload


@dataclass(frozen=True)
class PropertyLibraryFilters:
    """Search and filter controls for the synthetic property library preview."""

    query: str | None = None
    property_type: str | None = None
    county: str | None = None
    comp_role: str | None = None
    report_usage: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    min_size_sf: int | None = None
    max_size_sf: int | None = None
    verification_status: str | None = None
    selected_property_id: str | None = None

    def __post_init__(self) -> None:
        if self.date_from is not None:
            date.fromisoformat(self.date_from)
        if self.date_to is not None:
            date.fromisoformat(self.date_to)
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from > self.date_to
        ):
            raise ValueError("date_from must be earlier than or equal to date_to.")
        if self.min_size_sf is not None and self.min_size_sf < 0:
            raise ValueError("min_size_sf must be zero or greater.")
        if self.max_size_sf is not None and self.max_size_sf < 0:
            raise ValueError("max_size_sf must be zero or greater.")
        if (
            self.min_size_sf is not None
            and self.max_size_sf is not None
            and self.min_size_sf > self.max_size_sf
        ):
            raise ValueError("min_size_sf must be less than or equal to max_size_sf.")


@dataclass(frozen=True)
class PropertyLibraryDataset:
    """Synthetic dataset backing the property intelligence workspace."""

    properties: tuple[PropertyRecord, ...]
    evidence_events: tuple[EvidenceEvent, ...]
    report_usages: tuple[ReportUsage, ...]
    candidate_matches: tuple[CandidateMatch, ...]


def build_demo_property_library_workspace(
    filters: PropertyLibraryFilters | None = None,
) -> dict[str, Any]:
    """Build a filtered synthetic Property Library / Controlled Comp Vault preview."""

    active_filters = filters or PropertyLibraryFilters()
    dataset = build_demo_property_library_dataset()
    properties = _filter_properties(dataset, active_filters)
    selected_property = _select_property(properties, dataset, active_filters.selected_property_id)
    property_ids = {property_record.property_id for property_record in properties}

    return {
        "workspaceType": "synthetic_property_library_preview",
        "guardrail": (
            "Synthetic demo data only. No report contents, OCR, embeddings, "
            "OneDrive data, completed reports, or source documents are ingested."
        ),
        "map": _map_payload(properties),
        "filters": _filters_payload(active_filters, dataset),
        "summary": _summary_payload(properties, dataset),
        "resultsTable": [_table_row(property_record, dataset) for property_record in properties],
        "selectedPropertyDrawer": _drawer_payload(selected_property, dataset),
        "candidateNormalization": [
            match.to_dict()
            for match in dataset.candidate_matches
            if any(property_id in property_ids for property_id in match.property_ids)
        ],
    }


def build_demo_property_library_dataset() -> PropertyLibraryDataset:
    """Return the synthetic property and evidence dataset."""

    properties = (
        PropertyRecord(
            "prop-riverview-517",
            "517 E Riverview Avenue",
            "517 E Riverview Avenue",
            "Dayton",
            "Montgomery County",
            "OH",
            "Commercial",
            "Neighborhood retail",
            39.7652,
            -84.1829,
            6120,
            0.42,
            1987,
            "Average",
            "NC",
            "needs_review",
        ),
        PropertyRecord(
            "prop-main-1220",
            "1220 W Main Street",
            "1220 W Main Street",
            "Dayton",
            "Montgomery County",
            "OH",
            "Commercial",
            "Retail showroom",
            39.7583,
            -84.2141,
            8400,
            0.81,
            1994,
            "Average",
            "CG",
            "verified",
        ),
        PropertyRecord(
            "prop-market-88",
            "88 Market Plaza",
            "88 Market Plaza",
            "Troy",
            "Miami County",
            "OH",
            "Office",
            "Medical office",
            40.0395,
            -84.2033,
            14200,
            1.35,
            2006,
            "Good",
            "O-1",
            "verified",
        ),
        PropertyRecord(
            "prop-dixie-4100",
            "4100 N Dixie Drive",
            "4100 N Dixie Drive",
            "Dayton",
            "Montgomery County",
            "OH",
            "Industrial",
            "Flex warehouse",
            39.8116,
            -84.1956,
            38250,
            3.8,
            1978,
            "Fair",
            "I-1",
            "needs_review",
        ),
        PropertyRecord(
            "prop-riverview-517-alt",
            "517 East Riverview Ave",
            "517 East Riverview Ave",
            "Dayton",
            "Montgomery County",
            "OH",
            "Commercial",
            "Neighborhood retail",
            39.7651,
            -84.1830,
            6400,
            0.42,
            1987,
            "Average",
            "NC",
            "unverified",
        ),
        PropertyRecord(
            "prop-countyline-730",
            "730 County Line Road",
            "730 County Line Road",
            "Beavercreek",
            "Greene County",
            "OH",
            "Multifamily",
            "Garden apartments",
            39.7244,
            -84.0582,
            48600,
            5.9,
            1999,
            "Good",
            "R-MF",
            "locked",
        ),
    )
    evidence_events = (
        EvidenceEvent(
            "evt-riverview-subject",
            "prop-riverview-517",
            "subject_assignment",
            "2026-06-01",
            "Current synthetic subject profile assignment.",
            None,
            "assignment",
            "Synthetic order FI-2026-001",
            92,
            "needs_review",
        ),
        EvidenceEvent(
            "evt-riverview-sale",
            "prop-riverview-517",
            "sale",
            "2026-05-12",
            "Pending purchase contract.",
            425000,
            "sale_price",
            "Synthetic purchase contract summary",
            76,
            "needs_review",
        ),
        EvidenceEvent(
            "evt-main-sale",
            "prop-main-1220",
            "sale",
            "2025-11-04",
            "Closed retail sale used as market evidence.",
            690000,
            "sale_price",
            "Synthetic sale confirmation",
            88,
            "verified",
        ),
        EvidenceEvent(
            "evt-main-cap",
            "prop-main-1220",
            "cap_rate",
            "2025-11-04",
            "Stabilized cap-rate indication from closed sale.",
            7.4,
            "percent",
            "Synthetic appraiser analysis",
            82,
            "verified",
        ),
        EvidenceEvent(
            "evt-market-lease",
            "prop-market-88",
            "lease_rent",
            "2026-02-15",
            "Medical office renewal indication.",
            19.75,
            "rent_psf",
            "Synthetic lease abstract",
            84,
            "verified",
        ),
        EvidenceEvent(
            "evt-dixie-expense",
            "prop-dixie-4100",
            "expense",
            "2025-12-31",
            "Industrial operating expense benchmark.",
            3.85,
            "expense_psf",
            "Synthetic owner statement summary",
            69,
            "needs_review",
        ),
        EvidenceEvent(
            "evt-dixie-tax",
            "prop-dixie-4100",
            "assessment_tax",
            "2026-01-01",
            "Assessment and annual tax placeholder.",
            52400,
            "annual_tax",
            "Synthetic assessor note",
            63,
            "needs_review",
        ),
        EvidenceEvent(
            "evt-riverview-alt-sale",
            "prop-riverview-517-alt",
            "sale",
            "2026-05-12",
            "Alternate normalized sale record with conflicting size basis.",
            438000,
            "sale_price",
            "Synthetic duplicate comp sheet row",
            58,
            "unverified",
        ),
        EvidenceEvent(
            "evt-countyline-lease",
            "prop-countyline-730",
            "lease_rent",
            "2025-08-01",
            "Apartment rent support from synthetic rent roll.",
            1210,
            "monthly_unit_rent",
            "Synthetic rent roll summary",
            90,
            "locked",
        ),
        EvidenceEvent(
            "evt-countyline-expense",
            "prop-countyline-730",
            "expense",
            "2025-12-31",
            "Stabilized expense support.",
            4920,
            "expense_per_unit",
            "Synthetic operating statement summary",
            86,
            "verified",
        ),
    )
    report_usages = (
        ReportUsage(
            "use-riverview-subject",
            "prop-riverview-517",
            "FI-2026-001",
            "517 E Riverview Avenue Subject Profile",
            "subject_property",
            "2026-06-01",
            "A. Demo",
            "Current synthetic subject.",
        ),
        ReportUsage(
            "use-main-sale",
            "prop-main-1220",
            "FI-2025-144",
            "East Dayton Retail Market Study",
            "sale_comparable",
            "2025-12-15",
            "B. Appraiser",
            "Used as Sale 2.",
        ),
        ReportUsage(
            "use-main-cap",
            "prop-main-1220",
            "FI-2025-151",
            "Retail Cap Rate Support Memo",
            "cap_rate_support",
            "2025-12-20",
            "C. Reviewer",
            "Referenced for cap-rate support.",
        ),
        ReportUsage(
            "use-market-rent",
            "prop-market-88",
            "FI-2026-022",
            "Miami County Medical Office",
            "rental_comparable",
            "2026-03-01",
            "A. Demo",
            "Used as Rent Comp 1.",
        ),
        ReportUsage(
            "use-dixie-expense",
            "prop-dixie-4100",
            "FI-2026-014",
            "North Dayton Flex Review",
            "expense_comparable",
            "2026-02-10",
            "B. Appraiser",
            "Expense support requires verification.",
        ),
        ReportUsage(
            "use-riverview-alt-sale",
            "prop-riverview-517-alt",
            "FI-2026-009",
            "Riverview Corridor Retail Check",
            "sale_comparable",
            "2026-05-20",
            "D. Analyst",
            "Duplicate candidate, not canonical.",
        ),
        ReportUsage(
            "use-countyline-rent",
            "prop-countyline-730",
            "FI-2025-111",
            "Greene County Apartment Review",
            "rental_comparable",
            "2025-09-10",
            "C. Reviewer",
            "Locked rent support.",
        ),
        ReportUsage(
            "use-countyline-narrative",
            "prop-countyline-730",
            "FI-2026-017",
            "Suburban Multifamily Narrative Check",
            "narrative_reference",
            "2026-01-18",
            "A. Demo",
            "Used as market narrative reference.",
        ),
    )
    candidate_matches = (
        CandidateMatch(
            "match-riverview-address-size",
            ("prop-riverview-517", "prop-riverview-517-alt"),
            "same_address_conflicting_size",
            "Same Riverview address appears with 6,120 SF and 6,400 SF size bases.",
            {
                "building_size_sf": [6120, 6400],
                "address": ["517 E Riverview Avenue", "517 East Riverview Ave"],
            },
            87,
            "needs_review",
        ),
        CandidateMatch(
            "match-riverview-sale-price",
            ("prop-riverview-517", "prop-riverview-517-alt"),
            "same_sale_different_price",
            "Same synthetic May 2026 sale appears with different total price and price/SF.",
            {
                "sale_price": [425000, 438000],
                "price_per_sf": [69.44, 68.44],
            },
            74,
            "candidate",
        ),
        CandidateMatch(
            "match-main-report-usage",
            ("prop-main-1220", "prop-riverview-517"),
            "same_comp_used_by_different_appraisers",
            "Retail evidence appears in separate appraiser workflows and needs reuse context.",
            {
                "appraiser": ["B. Appraiser", "A. Demo"],
                "usage_role": ["sale_comparable", "subject_property"],
            },
            51,
            "candidate",
        ),
    )
    return PropertyLibraryDataset(properties, evidence_events, report_usages, candidate_matches)


def _filter_properties(
    dataset: PropertyLibraryDataset,
    filters: PropertyLibraryFilters,
) -> tuple[PropertyRecord, ...]:
    properties = dataset.properties
    if filters.query:
        query = filters.query.lower()
        properties = tuple(
            property_record
            for property_record in properties
            if _property_search_text(property_record, dataset).find(query) >= 0
        )
    if filters.property_type:
        properties = tuple(
            property_record
            for property_record in properties
            if property_record.property_type.lower() == filters.property_type.lower()
        )
    if filters.county:
        properties = tuple(
            property_record
            for property_record in properties
            if property_record.county.lower() == filters.county.lower()
        )
    if filters.verification_status:
        properties = tuple(
            property_record
            for property_record in properties
            if property_record.verification_status == filters.verification_status
        )
    if filters.min_size_sf is not None:
        properties = tuple(
            property_record
            for property_record in properties
            if property_record.building_size_sf >= filters.min_size_sf
        )
    if filters.max_size_sf is not None:
        properties = tuple(
            property_record
            for property_record in properties
            if property_record.building_size_sf <= filters.max_size_sf
        )
    if filters.comp_role:
        properties = tuple(
            property_record
            for property_record in properties
            if any(
                usage.property_id == property_record.property_id
                and usage.usage_role == filters.comp_role
                for usage in dataset.report_usages
            )
        )
    if filters.report_usage:
        properties = tuple(
            property_record
            for property_record in properties
            if any(
                usage.property_id == property_record.property_id
                and usage.order_number.lower() == filters.report_usage.lower()
                for usage in dataset.report_usages
            )
        )
    if filters.date_from or filters.date_to:
        properties = tuple(
            property_record
            for property_record in properties
            if _property_has_date_match(property_record.property_id, dataset, filters)
        )
    return tuple(sorted(properties, key=lambda property_record: property_record.address))


def _property_search_text(
    property_record: PropertyRecord,
    dataset: PropertyLibraryDataset,
) -> str:
    evidence = " ".join(
        event.summary
        for event in dataset.evidence_events
        if event.property_id == property_record.property_id
    )
    usages = " ".join(
        f"{usage.order_number} {usage.report_label} {usage.usage_role} {usage.appraiser}"
        for usage in dataset.report_usages
        if usage.property_id == property_record.property_id
    )
    return " ".join(
        (
            property_record.canonical_name,
            property_record.address,
            property_record.city,
            property_record.county,
            property_record.state,
            property_record.property_type,
            property_record.subtype,
            property_record.zoning,
            evidence,
            usages,
        )
    ).lower()


def _property_has_date_match(
    property_id: str,
    dataset: PropertyLibraryDataset,
    filters: PropertyLibraryFilters,
) -> bool:
    dates = [
        event.event_date
        for event in dataset.evidence_events
        if event.property_id == property_id
    ]
    dates.extend(
        usage.effective_date
        for usage in dataset.report_usages
        if usage.property_id == property_id
    )
    return any(
        (filters.date_from is None or item_date >= filters.date_from)
        and (filters.date_to is None or item_date <= filters.date_to)
        for item_date in dates
    )


def _select_property(
    properties: tuple[PropertyRecord, ...],
    dataset: PropertyLibraryDataset,
    selected_property_id: str | None,
) -> PropertyRecord | None:
    if selected_property_id is not None:
        for property_record in dataset.properties:
            if property_record.property_id == selected_property_id:
                return property_record
        raise ValueError(f"Unknown property_id: {selected_property_id}")
    return properties[0] if properties else None


def _map_payload(properties: tuple[PropertyRecord, ...]) -> dict[str, Any]:
    markers = [
        {
            "propertyId": property_record.property_id,
            "label": property_record.address,
            "latitude": property_record.latitude,
            "longitude": property_record.longitude,
            "verificationStatus": property_record.verification_status,
        }
        for property_record in properties
    ]
    return {
        "title": "Synthetic Miami Valley property map",
        "mode": "map_placeholder",
        "markerCount": len(markers),
        "markers": markers,
    }


def _filters_payload(
    filters: PropertyLibraryFilters,
    dataset: PropertyLibraryDataset,
) -> dict[str, Any]:
    return {
        "active": {
            "query": filters.query,
            "propertyType": filters.property_type,
            "county": filters.county,
            "compRole": filters.comp_role,
            "reportUsage": filters.report_usage,
            "dateFrom": filters.date_from,
            "dateTo": filters.date_to,
            "minSizeSf": filters.min_size_sf,
            "maxSizeSf": filters.max_size_sf,
            "verificationStatus": filters.verification_status,
            "selectedPropertyId": filters.selected_property_id,
        },
        "available": {
            "propertyTypes": sorted({item.property_type for item in dataset.properties}),
            "counties": sorted({item.county for item in dataset.properties}),
            "compRoles": sorted({item.usage_role for item in dataset.report_usages}),
            "verificationStatuses": sorted({item.verification_status for item in dataset.properties}),
        },
    }


def _summary_payload(
    properties: tuple[PropertyRecord, ...],
    dataset: PropertyLibraryDataset,
) -> dict[str, Any]:
    property_ids = {property_record.property_id for property_record in properties}
    return {
        "propertyCount": len(properties),
        "evidenceEventCount": sum(
            1 for event in dataset.evidence_events if event.property_id in property_ids
        ),
        "reportUsageCount": sum(
            1 for usage in dataset.report_usages if usage.property_id in property_ids
        ),
        "candidateConflictCount": sum(
            1
            for match in dataset.candidate_matches
            if any(property_id in property_ids for property_id in match.property_ids)
        ),
    }


def _table_row(
    property_record: PropertyRecord,
    dataset: PropertyLibraryDataset,
) -> dict[str, Any]:
    evidence = [
        event for event in dataset.evidence_events if event.property_id == property_record.property_id
    ]
    usages = [
        usage for usage in dataset.report_usages if usage.property_id == property_record.property_id
    ]
    conflicts = [
        match
        for match in dataset.candidate_matches
        if property_record.property_id in match.property_ids
    ]
    return {
        "propertyId": property_record.property_id,
        "address": property_record.address,
        "city": property_record.city,
        "county": property_record.county,
        "type": property_record.property_type,
        "subtype": property_record.subtype,
        "buildingSizeSf": property_record.building_size_sf,
        "siteSizeAcres": property_record.site_size_acres,
        "yearBuilt": property_record.year_built,
        "condition": property_record.condition,
        "zoning": property_record.zoning,
        "verificationStatus": property_record.verification_status,
        "evidenceEventTypes": sorted({event.event_type for event in evidence}),
        "reportUsageRoles": sorted({usage.usage_role for usage in usages}),
        "linkedReports": sorted({usage.order_number for usage in usages}),
        "candidateConflictCount": len(conflicts),
    }


def _drawer_payload(
    property_record: PropertyRecord | None,
    dataset: PropertyLibraryDataset,
) -> dict[str, Any] | None:
    if property_record is None:
        return None
    return {
        "property": property_record.to_dict(),
        "evidenceEvents": [
            event.to_dict()
            for event in dataset.evidence_events
            if event.property_id == property_record.property_id
        ],
        "reportUsages": [
            usage.to_dict()
            for usage in dataset.report_usages
            if usage.property_id == property_record.property_id
        ],
        "candidateMatches": [
            match.to_dict()
            for match in dataset.candidate_matches
            if property_record.property_id in match.property_ids
        ],
    }
