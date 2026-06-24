"""End-to-end synthetic Falcon Intelligence workflow orchestration."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from falcon_intel.audit import build_card_viewed_event
from falcon_intel.falcon_api_contract import (
    DEFAULT_SYNTHETIC_INTELLIGENCE_PATH,
    build_falcon_intelligence_card_response,
)
from falcon_intel.falcon_evidence_contract import build_falcon_evidence_open_response
from falcon_intel.falcon_passport_contract import build_falcon_passport_detail_response
from falcon_intel.permission_policy import (
    FalconRoleCode,
    can_open_evidence_link,
    can_view_intelligence_card,
    can_view_passport_detail,
)


DEFAULT_SYNTHETIC_PASSPORT_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "synthetic_data_passports"
    / "data-passports.json"
)


@dataclass(frozen=True)
class SyntheticIntelligenceWorkflowResult:
    """Synthetic end-to-end workflow result for local validation."""

    status: str
    role: str
    order_id: str
    tenant_id: str
    user_id: str
    card: dict[str, Any]
    selected_match: dict[str, Any]
    card_permission: dict[str, Any]
    passport_permission: dict[str, Any]
    passport_response: dict[str, Any]
    selected_evidence_link: dict[str, Any]
    evidence_permission: dict[str, Any]
    evidence_response: dict[str, Any]
    suggested_audit_events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_synthetic_intelligence_workflow(
    order_payload: dict[str, Any],
    *,
    user_id: str,
    role: FalconRoleCode | str = FalconRoleCode.APPRAISER,
    synthetic_intelligence_path: str | Path = DEFAULT_SYNTHETIC_INTELLIGENCE_PATH,
    synthetic_passport_path: str | Path = DEFAULT_SYNTHETIC_PASSPORT_PATH,
) -> SyntheticIntelligenceWorkflowResult:
    """Run the synthetic card to passport to evidence trust workflow."""

    active_role = FalconRoleCode(role)
    order_id = str(order_payload["order_id"])
    tenant_id = str(order_payload["tenant_id"])

    card_permission = can_view_intelligence_card(active_role).to_dict()
    if not card_permission["allowed"]:
        raise PermissionError(card_permission["reason_code"])

    card_response = build_falcon_intelligence_card_response(
        order_payload,
        synthetic_intelligence_path=synthetic_intelligence_path,
    )
    if card_response["status"] != "ok":
        raise ValueError(f"Card response failed: {card_response['status']}")
    card = card_response["card"]
    selected_match = _select_top_match_with_passport(card)

    card_audit_event = build_card_viewed_event(
        tenant_id=tenant_id,
        order_id=order_id,
        user_id=user_id,
        metadata={
            "schema_version": card["schema_version"],
            "selected_passport_id": selected_match["passport_id"],
            "top_match_source_id": selected_match["source_id"],
        },
    ).to_dict()

    passport_permission = can_view_passport_detail(active_role).to_dict()
    if not passport_permission["allowed"]:
        raise PermissionError(passport_permission["reason_code"])

    passport_response = build_falcon_passport_detail_response(
        {
            "tenant_id": tenant_id,
            "order_id": order_id,
            "user_id": user_id,
            "passport_id": selected_match["passport_id"],
        },
        synthetic_passport_path=synthetic_passport_path,
    )
    if passport_response["status"] != "ok":
        raise ValueError(f"Passport response failed: {passport_response['status']}")
    selected_evidence_link = passport_response["passport"]["evidence_links"][0]

    evidence_permission = can_open_evidence_link(
        active_role,
        selected_evidence_link["access_level"],
    ).to_dict()
    if not evidence_permission["allowed"]:
        raise PermissionError(evidence_permission["reason_code"])

    evidence_response = build_falcon_evidence_open_response(
        {
            "tenant_id": tenant_id,
            "order_id": order_id,
            "user_id": user_id,
            "passport_id": selected_match["passport_id"],
            "evidence_id": selected_evidence_link["evidence_id"],
        },
        synthetic_passport_path=synthetic_passport_path,
    )
    if evidence_response["status"] != "ok":
        raise ValueError(f"Evidence response failed: {evidence_response['status']}")

    return SyntheticIntelligenceWorkflowResult(
        status="ok",
        role=active_role.value,
        order_id=order_id,
        tenant_id=tenant_id,
        user_id=user_id,
        card=card,
        selected_match=selected_match,
        card_permission=card_permission,
        passport_permission=passport_permission,
        passport_response=passport_response,
        selected_evidence_link=selected_evidence_link,
        evidence_permission=evidence_permission,
        evidence_response=evidence_response,
        suggested_audit_events=[
            card_audit_event,
            passport_response["suggested_audit_event"],
            evidence_response["suggested_audit_event"],
        ],
    )


def _select_top_match_with_passport(card: dict[str, Any]) -> dict[str, Any]:
    for match in card.get("top_match_cards", []):
        if match.get("passport_id"):
            return match
    raise ValueError("Card does not include a top match with passport_id.")
