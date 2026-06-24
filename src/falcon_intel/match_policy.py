"""Stable policy identifiers for Firm Intelligence match UI/API contracts."""

from enum import StrEnum


class MatchCategoryCode(StrEnum):
    """Stable match category identifiers."""

    SAME_SUBJECT = "same_subject_property"
    NEARBY_ASSIGNMENTS = "nearby_prior_assignments"
    SAME_CLIENT = "same_client"
    SAME_PROPERTY_TYPE = "same_property_type"
    SIMILAR_SIZE = "similar_building_size"
    SALE_COMPS = "verified_sale_comps"
    LEASE_COMPS = "verified_lease_comps"
    MARKET_INDICATORS = "relevant_market_indicators"


class WarningCode(StrEnum):
    """Stable warning identifiers for match and card displays."""

    SYNTHETIC_PREVIEW_ONLY = "synthetic_preview_only"
    APPRAISER_REVIEW_REQUIRED = "appraiser_review_required"
    STALE_DATA_PRESENT = "stale_data_present"
    STALE_MATCH = "stale"
    CONFLICTING_DATA = "conflicting_data"
    LOW_CONFIDENCE = "low_confidence"
    UNREVIEWED_EXTRACTION = "unreviewed_extraction"
    DIFFERENT_PROPERTY_SUBTYPE = "different_property_subtype"


class RecommendedActionCode(StrEnum):
    """Stable recommended action identifiers."""

    REVIEW_TOP_MATCHES = "review_top_matches"
    CONFIRM_RELEVANCE = "confirm_relevance"
    EVALUATE_COMPARABLE_REUSE = "evaluate_comparable_reuse"
    CONTINUE_STANDARD_RESEARCH = "continue_standard_research"
    USE_AS_REFERENCE = "use_as_reference"
    OPEN_EVIDENCE = "open_evidence"
    MARK_NOT_RELEVANT = "mark_not_relevant"
    SELECT_FOR_REPORT_CONSIDERATION = "select_for_report_consideration"
    JUSTIFY_HISTORICAL_COMP_USE = "justify_historical_comp_use"


class AuditEventCode(StrEnum):
    """Stable audit event identifiers for future Falcon integration."""

    VIEWED_MATCH = "viewed_match"
    OPENED_EVIDENCE = "opened_evidence"
    SELECTED_COMP_FACT = "selected_comp_fact"
    REJECTED_MATCH = "rejected_match"
    WROTE_JUSTIFICATION = "wrote_justification"


MATCH_CATEGORY_LABELS = {
    MatchCategoryCode.SAME_SUBJECT: "Same Subject Property",
    MatchCategoryCode.NEARBY_ASSIGNMENTS: "Nearby Prior Assignments",
    MatchCategoryCode.SAME_CLIENT: "Same Client",
    MatchCategoryCode.SAME_PROPERTY_TYPE: "Same Property Type",
    MatchCategoryCode.SIMILAR_SIZE: "Similar Building Size",
    MatchCategoryCode.SALE_COMPS: "Verified Sale Comps",
    MatchCategoryCode.LEASE_COMPS: "Verified Lease Comps",
    MatchCategoryCode.MARKET_INDICATORS: "Relevant Market Indicators",
}

MATCH_CATEGORY_ORDER = (
    MatchCategoryCode.SAME_SUBJECT,
    MatchCategoryCode.NEARBY_ASSIGNMENTS,
    MatchCategoryCode.SAME_PROPERTY_TYPE,
    MatchCategoryCode.SIMILAR_SIZE,
    MatchCategoryCode.SAME_CLIENT,
    MatchCategoryCode.SALE_COMPS,
    MatchCategoryCode.LEASE_COMPS,
    MatchCategoryCode.MARKET_INDICATORS,
)
