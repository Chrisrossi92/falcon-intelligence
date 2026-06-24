"""Local in-memory contract boundary for future Falcon card API/RPC."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from falcon_intel.intelligence_card import build_firm_intelligence_card
from falcon_intel.intelligence_matcher import (
    FakeOrder,
    load_synthetic_verified_intelligence,
    match_firm_intelligence,
)
from falcon_intel.schema_registry import FALCON_CARD_API_RESPONSE_SCHEMA_VERSION


DEFAULT_SYNTHETIC_INTELLIGENCE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "synthetic_verified_intelligence"
    / "verified-intelligence.json"
)
REQUIRED_ORDER_FIELDS = (
    "order_id",
    "tenant_id",
    "address",
    "city",
    "state",
    "property_type",
    "building_size_sf",
    "client",
)


@dataclass(frozen=True)
class FalconCardBoundaryResponse:
    """In-memory stand-in for a future Falcon Intelligence API/RPC response."""

    status: str
    order_id: str | None
    tenant_id: str | None
    schema_version: str = FALCON_CARD_API_RESPONSE_SCHEMA_VERSION
    card: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "order_id": self.order_id,
            "tenant_id": self.tenant_id,
            "schema_version": self.schema_version,
        }
        if self.card is not None:
            payload["card"] = self.card
        if self.error is not None:
            payload["error"] = self.error
        return payload


def build_falcon_intelligence_card_response(
    order_payload: dict[str, Any],
    *,
    synthetic_intelligence_path: str | Path = DEFAULT_SYNTHETIC_INTELLIGENCE_PATH,
) -> dict[str, Any]:
    """Return a synthetic v1 Firm Intelligence card for a Falcon-style order payload."""

    missing_fields = [
        field
        for field in REQUIRED_ORDER_FIELDS
        if field not in order_payload or order_payload[field] in (None, "")
    ]
    order_id = str(order_payload["order_id"]) if order_payload.get("order_id") else None
    tenant_id = str(order_payload["tenant_id"]) if order_payload.get("tenant_id") else None
    if missing_fields:
        return FalconCardBoundaryResponse(
            status="missing_required_input",
            order_id=order_id,
            tenant_id=tenant_id,
            error={
                "code": "missing_required_input",
                "message": "Falcon order payload is missing required fields.",
                "missing_fields": missing_fields,
            },
        ).to_dict()

    intelligence = load_synthetic_verified_intelligence(synthetic_intelligence_path)
    matcher_output = match_firm_intelligence(
        FakeOrder(
            address=str(order_payload["address"]),
            city=str(order_payload["city"]),
            state=str(order_payload["state"]),
            property_type=str(order_payload["property_type"]),
            building_size_sf=int(order_payload["building_size_sf"]),
            client=str(order_payload["client"]),
            borrower_contact=(
                str(order_payload["borrower_contact"])
                if order_payload.get("borrower_contact")
                else None
            ),
        ),
        intelligence,
    )
    card = build_firm_intelligence_card(matcher_output, intelligence).to_dict()
    return FalconCardBoundaryResponse(
        status="ok",
        order_id=order_id,
        tenant_id=tenant_id,
        card=card,
    ).to_dict()
