from falcon_intel.match_policy import (
    MATCH_CATEGORY_LABELS,
    MATCH_CATEGORY_ORDER,
    AuditEventCode,
    MatchCategoryCode,
    RecommendedActionCode,
    WarningCode,
)


def test_match_policy_codes_are_stable() -> None:
    assert [category.value for category in MATCH_CATEGORY_ORDER] == [
        "same_subject_property",
        "nearby_prior_assignments",
        "same_property_type",
        "similar_building_size",
        "same_client",
        "verified_sale_comps",
        "verified_lease_comps",
        "relevant_market_indicators",
    ]
    assert MATCH_CATEGORY_LABELS[MatchCategoryCode.SAME_SUBJECT] == "Same Subject Property"


def test_warning_action_and_audit_codes_exist() -> None:
    assert WarningCode.STALE_DATA_PRESENT.value == "stale_data_present"
    assert WarningCode.DIFFERENT_PROPERTY_SUBTYPE.value == "different_property_subtype"
    assert RecommendedActionCode.OPEN_EVIDENCE.value == "open_evidence"
    assert RecommendedActionCode.JUSTIFY_HISTORICAL_COMP_USE.value == "justify_historical_comp_use"
    assert AuditEventCode.VIEWED_MATCH.value == "viewed_match"
    assert AuditEventCode.WROTE_JUSTIFICATION.value == "wrote_justification"
