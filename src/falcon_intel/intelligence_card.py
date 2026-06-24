"""UI-facing synthetic Firm Intelligence Found card schema."""

from dataclasses import asdict, dataclass
from typing import Any

from falcon_intel.intelligence_matcher import FirmIntelligenceMatchResult, MATCH_GROUPS
from falcon_intel.match_policy import (
    MATCH_CATEGORY_LABELS,
    AuditEventCode,
    MatchCategoryCode,
    RecommendedActionCode,
    WarningCode,
)


TOP_MATCHES_PER_GROUP = 3


@dataclass(frozen=True)
class IntelligenceCardOrderSummary:
    """Order fields needed by the future UI card header."""

    address: str
    city: str
    state: str
    property_type: str
    building_size_sf: int
    client: str


@dataclass(frozen=True)
class IntelligenceCardMatchGroupSummary:
    """One grouped match count and score summary."""

    group: str
    category_code: str
    label: str
    count: int
    top_score: int | None


@dataclass(frozen=True)
class IntelligenceCardTopMatch:
    """One UI card row for a surfaced synthetic match."""

    group: str
    category_code: str
    source_id: str
    source_type: str
    title: str
    score: int
    explanation: str
    confidence_label: str
    passport_id: str | None
    verification_status: str | None
    evidence_link_count: int
    confidence_summary: str | None
    searchable_status: str | None
    provenance: dict[str, Any]
    stale_data_flags: list[str]
    details: dict[str, Any]


@dataclass(frozen=True)
class IntelligenceCardConfidenceProvenanceSummary:
    """Card-level confidence and provenance rollup."""

    total_matches: int
    verified_match_count: int
    synthetic_fixture_only: bool
    highest_score: int | None
    source_fixture_kind: str
    source_fixture_version: str | None


@dataclass(frozen=True)
class IntelligenceCardWarning:
    """UI-visible card warning."""

    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class IntelligenceCardRecommendedAction:
    """Suggested appraiser/reviewer action for the future card."""

    code: str
    label: str
    reason: str
    audit_event_code: str | None = None


@dataclass(frozen=True)
class FirmIntelligenceCard:
    """Stable UI-facing schema for the future Firm Intelligence Found card."""

    schema_version: str
    headline: str
    order_summary: IntelligenceCardOrderSummary
    match_group_summaries: list[IntelligenceCardMatchGroupSummary]
    top_match_cards: list[IntelligenceCardTopMatch]
    confidence_provenance_summary: IntelligenceCardConfidenceProvenanceSummary
    warnings: list[IntelligenceCardWarning]
    recommended_actions: list[IntelligenceCardRecommendedAction]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_firm_intelligence_card(
    matcher_output: FirmIntelligenceMatchResult | dict[str, Any],
    synthetic_verified_intelligence: dict[str, Any],
    *,
    top_matches_per_group: int = TOP_MATCHES_PER_GROUP,
) -> FirmIntelligenceCard:
    """Serialize synthetic matcher output into the stable UI card schema."""

    matcher_payload = matcher_output.to_dict() if isinstance(matcher_output, FirmIntelligenceMatchResult) else matcher_output
    _validate_synthetic_fixture(synthetic_verified_intelligence)
    source_records = _source_lookup(synthetic_verified_intelligence)
    groups: dict[str, list[dict[str, Any]]] = matcher_payload["match_groups"]
    total_matches = sum(len(matches) for matches in groups.values())
    top_scores = [int(match["score"]) for matches in groups.values() for match in matches]

    top_match_cards = [
        _top_match_card(match, source_records)
        for group in MATCH_GROUPS
        for match in groups.get(group, [])[:top_matches_per_group]
    ]

    return FirmIntelligenceCard(
        schema_version="1",
        headline=_headline(total_matches, groups),
        order_summary=_order_summary(matcher_payload["order"]),
        match_group_summaries=[
            IntelligenceCardMatchGroupSummary(
                group=group,
                category_code=group,
                label=_category_label(group),
                count=len(groups.get(group, [])),
                top_score=max((int(match["score"]) for match in groups.get(group, [])), default=None),
            )
            for group in MATCH_GROUPS
        ],
        top_match_cards=top_match_cards,
        confidence_provenance_summary=IntelligenceCardConfidenceProvenanceSummary(
            total_matches=total_matches,
            verified_match_count=sum(
                1
                for card in top_match_cards
                if card.provenance.get("verification_status") == "verified"
            ),
            synthetic_fixture_only=all(
                record.get("synthetic_fixture") is True
                for record in source_records.values()
            ),
            highest_score=max(top_scores) if top_scores else None,
            source_fixture_kind=str(synthetic_verified_intelligence["fixture_kind"]),
            source_fixture_version=(
                str(synthetic_verified_intelligence["fixture_version"])
                if synthetic_verified_intelligence.get("fixture_version") is not None
                else None
            ),
        ),
        warnings=_warnings(top_match_cards),
        recommended_actions=_recommended_actions(total_matches, top_match_cards),
    )


def _validate_synthetic_fixture(payload: dict[str, Any]) -> None:
    if payload.get("fixture_kind") != "synthetic_verified_intelligence":
        raise ValueError("UI card schema requires a synthetic verified intelligence fixture.")


def _source_lookup(intelligence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for collection_name in ("assignments", "sale_comps", "lease_comps", "market_indicators"):
        for record in intelligence.get(collection_name, []):
            lookup[str(record["id"])] = record
    return lookup


def _top_match_card(match: dict[str, Any], source_records: dict[str, dict[str, Any]]) -> IntelligenceCardTopMatch:
    source_record = source_records.get(str(match["source_id"]), {})
    stale_flags = _stale_flags(source_record)
    passport = _passport_summary(source_record)
    return IntelligenceCardTopMatch(
        group=str(match["group"]),
        category_code=str(match["group"]),
        source_id=str(match["source_id"]),
        source_type=str(match["source_type"]),
        title=str(match["title"]),
        score=int(match["score"]),
        explanation=str(match["explanation"]),
        confidence_label=_confidence_label(int(match["score"])),
        passport_id=passport["passport_id"],
        verification_status=passport["verification_status"],
        evidence_link_count=passport["evidence_link_count"],
        confidence_summary=passport["confidence_summary"],
        searchable_status=passport["searchable_status"],
        provenance={
            "verification_status": source_record.get("verification_status"),
            "synthetic_fixture": source_record.get("synthetic_fixture"),
            "record_type": source_record.get("record_type"),
            "source_id": match["source_id"],
        },
        stale_data_flags=stale_flags,
        details=dict(match["details"]),
    )


def _passport_summary(source_record: dict[str, Any]) -> dict[str, Any]:
    passport = source_record.get("passport") or {}
    evidence_links = passport.get("evidence_links") or []
    return {
        "passport_id": passport.get("passport_id"),
        "verification_status": source_record.get("verification_status"),
        "evidence_link_count": len(evidence_links),
        "confidence_summary": passport.get("confidence_summary"),
        "searchable_status": passport.get("searchable_status"),
    }


def _stale_flags(source_record: dict[str, Any]) -> list[str]:
    if source_record.get("stale_after") == "expired":
        return [WarningCode.STALE_MATCH.value]
    return []


def _order_summary(order: dict[str, Any]) -> IntelligenceCardOrderSummary:
    return IntelligenceCardOrderSummary(
        address=str(order["address"]),
        city=str(order["city"]),
        state=str(order["state"]),
        property_type=str(order["property_type"]),
        building_size_sf=int(order["building_size_sf"]),
        client=str(order["client"]),
    )


def _headline(total_matches: int, groups: dict[str, list[dict[str, Any]]]) -> str:
    if total_matches == 0:
        return "No synthetic firm intelligence matches found."
    active_group_count = sum(1 for matches in groups.values() if matches)
    return f"Firm Intelligence Found: {total_matches} synthetic matches across {active_group_count} groups."


def _warnings(top_match_cards: list[IntelligenceCardTopMatch]) -> list[IntelligenceCardWarning]:
    warnings = [
        IntelligenceCardWarning(
            code=WarningCode.SYNTHETIC_PREVIEW_ONLY.value,
            severity="info",
            message="Synthetic preview only; do not use as production firm intelligence.",
        ),
        IntelligenceCardWarning(
            code=WarningCode.APPRAISER_REVIEW_REQUIRED.value,
            severity="info",
            message="Matches are routing prompts and require appraiser judgment before reuse.",
        ),
    ]
    if any(card.stale_data_flags for card in top_match_cards):
        warnings.append(
            IntelligenceCardWarning(
                code=WarningCode.STALE_DATA_PRESENT.value,
                severity="warning",
                message="One or more matches has stale data flags.",
            )
        )
    return warnings


def _recommended_actions(
    total_matches: int,
    top_match_cards: list[IntelligenceCardTopMatch],
) -> list[IntelligenceCardRecommendedAction]:
    if total_matches == 0:
        return [
            IntelligenceCardRecommendedAction(
                code=RecommendedActionCode.CONTINUE_STANDARD_RESEARCH.value,
                label="Continue standard research",
                reason="No synthetic verified intelligence matches were found.",
                audit_event_code=None,
            )
        ]

    actions = [
        IntelligenceCardRecommendedAction(
            code=RecommendedActionCode.REVIEW_TOP_MATCHES.value,
            label="Review top matches",
            reason="Synthetic verified intelligence matches were found for this fake order.",
            audit_event_code=AuditEventCode.VIEWED_MATCH.value,
        ),
        IntelligenceCardRecommendedAction(
            code=RecommendedActionCode.CONFIRM_RELEVANCE.value,
            label="Confirm relevance",
            reason="Scores are routing hints, not valuation conclusions.",
            audit_event_code=None,
        ),
    ]
    if any(card.group in {"verified_sale_comps", "verified_lease_comps"} for card in top_match_cards):
        actions.append(
            IntelligenceCardRecommendedAction(
                code=RecommendedActionCode.EVALUATE_COMPARABLE_REUSE.value,
                label="Evaluate comparable reuse",
                reason="Verified synthetic comparable matches are present.",
                audit_event_code=AuditEventCode.SELECTED_COMP_FACT.value,
            )
        )
    return actions


def _confidence_label(score: int) -> str:
    if score >= 85:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def _category_label(group: str) -> str:
    try:
        category = MatchCategoryCode(group)
    except ValueError:
        return group.replace("_", " ").title()
    return MATCH_CATEGORY_LABELS[category]
