"""Synthetic-only firm intelligence matcher for future Falcon order cards."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
import json


MATCH_GROUPS = (
    "same_subject_property",
    "nearby_prior_assignments",
    "same_property_type",
    "similar_building_size",
    "same_client",
    "verified_sale_comps",
    "verified_lease_comps",
    "relevant_market_indicators",
)


@dataclass(frozen=True)
class FakeOrder:
    """Structured fake order seed used only for synthetic matching tests."""

    address: str
    city: str
    state: str
    property_type: str
    building_size_sf: int
    client: str
    borrower_contact: str | None = None


@dataclass(frozen=True)
class IntelligenceMatch:
    """One metadata/structured-data match for a future intelligence card."""

    group: str
    source_id: str
    source_type: str
    title: str
    score: int
    explanation: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FirmIntelligenceMatchResult:
    """Grouped synthetic-only matches for one fake order."""

    order: dict[str, Any]
    match_groups: dict[str, list[dict[str, Any]]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_synthetic_verified_intelligence(path: str | Path) -> dict[str, Any]:
    """Load synthetic verified intelligence JSON without reading source documents."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _validate_synthetic_index(payload)
    return payload


def match_firm_intelligence(
    order: FakeOrder | dict[str, Any],
    synthetic_verified_intelligence: dict[str, Any],
) -> FirmIntelligenceMatchResult:
    """Match one fake order against synthetic verified intelligence records."""

    _validate_synthetic_index(synthetic_verified_intelligence)
    active_order = _coerce_order(order)
    groups: dict[str, list[IntelligenceMatch]] = {group: [] for group in MATCH_GROUPS}

    for assignment in synthetic_verified_intelligence.get("assignments", []):
        _match_assignment(active_order, assignment, groups)

    for comp in synthetic_verified_intelligence.get("sale_comps", []):
        score = _comp_score(active_order, comp, base_score=50)
        if score > 0:
            groups["verified_sale_comps"].append(
                _match(
                    "verified_sale_comps",
                    comp,
                    "Verified sale comp",
                    score,
                    _comp_explanation(active_order, comp, "sale"),
                    _compact_details(comp, ("address", "city", "state", "property_type", "building_size_sf", "sale_date")),
                )
            )

    for comp in synthetic_verified_intelligence.get("lease_comps", []):
        score = _comp_score(active_order, comp, base_score=50)
        if score > 0:
            groups["verified_lease_comps"].append(
                _match(
                    "verified_lease_comps",
                    comp,
                    "Verified lease comp",
                    score,
                    _comp_explanation(active_order, comp, "lease"),
                    _compact_details(comp, ("address", "city", "state", "property_type", "building_size_sf", "lease_date")),
                )
            )

    for indicator in synthetic_verified_intelligence.get("market_indicators", []):
        score = _market_indicator_score(active_order, indicator)
        if score > 0:
            groups["relevant_market_indicators"].append(
                _match(
                    "relevant_market_indicators",
                    indicator,
                    "Relevant market indicator",
                    score,
                    _market_indicator_explanation(active_order, indicator),
                    _compact_details(indicator, ("market", "state", "property_type", "indicator_type", "value", "date_range")),
                )
            )

    sorted_groups = {
        group: [match.to_dict() for match in sorted(matches, key=lambda item: (-item.score, item.title.lower()))]
        for group, matches in groups.items()
    }
    return FirmIntelligenceMatchResult(order=asdict(active_order), match_groups=sorted_groups)


def _match_assignment(
    order: FakeOrder,
    assignment: dict[str, Any],
    groups: dict[str, list[IntelligenceMatch]],
) -> None:
    if _same_address(order, assignment):
        groups["same_subject_property"].append(
            _match(
                "same_subject_property",
                assignment,
                "Prior subject property",
                100,
                "Exact synthetic address, city, and state match.",
                _assignment_details(assignment),
            )
        )

    if _same_market(order, assignment) and not _same_address(order, assignment):
        groups["nearby_prior_assignments"].append(
            _match(
                "nearby_prior_assignments",
                assignment,
                "Nearby prior assignment",
                70 + (10 if _same_property_type(order, assignment) else 0),
                "Same synthetic city and state; useful as a prior assignment prompt.",
                _assignment_details(assignment),
            )
        )

    if _same_property_type(order, assignment):
        groups["same_property_type"].append(
            _match(
                "same_property_type",
                assignment,
                "Same property type assignment",
                65 + (15 if _same_market(order, assignment) else 0),
                f"Property type matches: {assignment['property_type']}.",
                _assignment_details(assignment),
            )
        )

    if _similar_size(order.building_size_sf, int(assignment.get("building_size_sf", 0))):
        percent_delta = _size_delta_percent(order.building_size_sf, int(assignment["building_size_sf"]))
        groups["similar_building_size"].append(
            _match(
                "similar_building_size",
                assignment,
                "Similar building size assignment",
                max(55, 90 - int(percent_delta)),
                f"Building size is within {percent_delta:.1f}% of the fake order.",
                _assignment_details(assignment),
            )
        )

    if _normalized(order.client) == _normalized(str(assignment.get("client", ""))):
        groups["same_client"].append(
            _match(
                "same_client",
                assignment,
                "Same synthetic client",
                85,
                "Client name matches the fake order client exactly after normalization.",
                _assignment_details(assignment),
            )
        )


def _validate_synthetic_index(payload: dict[str, Any]) -> None:
    if payload.get("fixture_kind") != "synthetic_verified_intelligence":
        raise ValueError("Matcher requires a synthetic verified intelligence fixture.")
    for collection_name in ("assignments", "sale_comps", "lease_comps", "market_indicators"):
        for record in payload.get(collection_name, []):
            if record.get("verification_status") != "verified":
                raise ValueError(f"{collection_name} contains a non-verified record.")
            if record.get("synthetic_fixture") is not True:
                raise ValueError(f"{collection_name} contains a non-synthetic record.")
            if "report_text" in record or "source_file_path" in record:
                raise ValueError(f"{collection_name} contains prohibited source-content fields.")


def _coerce_order(order: FakeOrder | dict[str, Any]) -> FakeOrder:
    if isinstance(order, FakeOrder):
        return order
    return FakeOrder(
        address=str(order["address"]),
        city=str(order["city"]),
        state=str(order["state"]),
        property_type=str(order["property_type"]),
        building_size_sf=int(order["building_size_sf"]),
        client=str(order["client"]),
        borrower_contact=str(order["borrower_contact"]) if order.get("borrower_contact") else None,
    )


def _match(
    group: str,
    record: dict[str, Any],
    title: str,
    score: int,
    explanation: str,
    details: dict[str, Any],
) -> IntelligenceMatch:
    return IntelligenceMatch(
        group=group,
        source_id=str(record["id"]),
        source_type=str(record.get("record_type", "synthetic_verified_record")),
        title=title,
        score=max(0, min(score, 100)),
        explanation=explanation,
        details=details,
    )


def _assignment_details(record: dict[str, Any]) -> dict[str, Any]:
    return _compact_details(
        record,
        ("address", "city", "state", "property_type", "building_size_sf", "client", "assignment_type", "effective_date"),
    )


def _compact_details(record: dict[str, Any], keys: Iterable[str]) -> dict[str, Any]:
    return {key: record[key] for key in keys if key in record}


def _same_address(order: FakeOrder, record: dict[str, Any]) -> bool:
    return (
        _normalized(order.address) == _normalized(str(record.get("address", "")))
        and _same_market(order, record)
    )


def _same_market(order: FakeOrder, record: dict[str, Any]) -> bool:
    return _normalized(order.city) == _normalized(str(record.get("city", record.get("market", "")))) and _normalized(
        order.state
    ) == _normalized(str(record.get("state", "")))


def _same_property_type(order: FakeOrder, record: dict[str, Any]) -> bool:
    return _normalized(order.property_type) == _normalized(str(record.get("property_type", "")))


def _similar_size(order_size: int, candidate_size: int) -> bool:
    return candidate_size > 0 and _size_delta_percent(order_size, candidate_size) <= 25.0


def _size_delta_percent(order_size: int, candidate_size: int) -> float:
    if order_size <= 0:
        return 100.0
    return abs(order_size - candidate_size) / order_size * 100


def _comp_score(order: FakeOrder, comp: dict[str, Any], *, base_score: int) -> int:
    score = 0
    if _same_property_type(order, comp):
        score += base_score
    if _same_market(order, comp):
        score += 25
    if _similar_size(order.building_size_sf, int(comp.get("building_size_sf", 0))):
        score += 20
    return min(score, 100)


def _comp_explanation(order: FakeOrder, comp: dict[str, Any], comp_kind: str) -> str:
    reasons = []
    if _same_property_type(order, comp):
        reasons.append("same property type")
    if _same_market(order, comp):
        reasons.append("same synthetic market")
    if _similar_size(order.building_size_sf, int(comp.get("building_size_sf", 0))):
        reasons.append("similar building size")
    return f"Verified synthetic {comp_kind} comparable matched on {', '.join(reasons)}."


def _market_indicator_score(order: FakeOrder, indicator: dict[str, Any]) -> int:
    score = 0
    if _same_property_type(order, indicator):
        score += 55
    if _normalized(order.city) == _normalized(str(indicator.get("market", ""))) and _normalized(order.state) == _normalized(
        str(indicator.get("state", ""))
    ):
        score += 35
    return score


def _market_indicator_explanation(order: FakeOrder, indicator: dict[str, Any]) -> str:
    reasons = []
    if _same_property_type(order, indicator):
        reasons.append("property type")
    if _normalized(order.city) == _normalized(str(indicator.get("market", ""))) and _normalized(order.state) == _normalized(
        str(indicator.get("state", ""))
    ):
        reasons.append("synthetic market")
    return f"Verified synthetic market indicator matched on {' and '.join(reasons)}."


def _normalized(value: str) -> str:
    return " ".join(value.lower().replace(",", " ").split())
