"""Schema version registry for synthetic Falcon Intelligence contracts."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


FIRM_INTELLIGENCE_CARD_SCHEMA_VERSION = "1"
PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION = "1"
FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION = "1"
FALCON_CARD_API_RESPONSE_SCHEMA_VERSION = "1"
FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION = "1"


class SchemaName(StrEnum):
    """Stable schema identifiers for UI/API contract objects."""

    FIRM_INTELLIGENCE_CARD = "firm_intelligence_found_card"
    PASSPORT_DETAIL_DRAWER = "passport_detail_drawer"
    FALCON_EVIDENCE_OPEN_RESPONSE = "falcon_evidence_open_response"
    FALCON_CARD_API_RESPONSE = "falcon_card_api_response"
    FALCON_PASSPORT_DETAIL_API_RESPONSE = "falcon_passport_detail_api_response"


@dataclass(frozen=True)
class SchemaRegistryEntry:
    """One schema version entry for future Falcon integration work."""

    schema_name: str
    current_version: str
    fixture_snapshot_path: str | None
    breaking_change_rules: list[str]
    backward_compatibility_notes: str
    intended_consumer: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_BREAKING_CHANGE_RULES = [
    "Removing, renaming, or changing the type of a required field requires a new schema version.",
    "Changing the meaning, units, enum values, or status semantics of an existing field requires a new schema version.",
    "Adding optional fields is backward-compatible when existing fields keep their meaning.",
    "Snapshot fixtures must be updated deliberately when a UI-facing schema version changes.",
]


SCHEMA_REGISTRY: dict[SchemaName, SchemaRegistryEntry] = {
    SchemaName.FIRM_INTELLIGENCE_CARD: SchemaRegistryEntry(
        schema_name=SchemaName.FIRM_INTELLIGENCE_CARD.value,
        current_version=FIRM_INTELLIGENCE_CARD_SCHEMA_VERSION,
        fixture_snapshot_path="tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json",
        breaking_change_rules=_BREAKING_CHANGE_RULES,
        backward_compatibility_notes=(
            "Falcon UI consumers may add support for optional fields without breaking v1. "
            "Any required field removal or semantic change must produce a new snapshot and version."
        ),
        intended_consumer="Falcon internal Order Detail, New Order intake, and Assignment workspace UI.",
    ),
    SchemaName.PASSPORT_DETAIL_DRAWER: SchemaRegistryEntry(
        schema_name=SchemaName.PASSPORT_DETAIL_DRAWER.value,
        current_version=PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION,
        fixture_snapshot_path="tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json",
        breaking_change_rules=_BREAKING_CHANGE_RULES,
        backward_compatibility_notes=(
            "Drawer consumers should treat new optional summary fields as additive. "
            "Evidence opening remains metadata-only until the production readiness gate passes."
        ),
        intended_consumer="Falcon internal passport detail drawer.",
    ),
    SchemaName.FALCON_EVIDENCE_OPEN_RESPONSE: SchemaRegistryEntry(
        schema_name=SchemaName.FALCON_EVIDENCE_OPEN_RESPONSE.value,
        current_version=FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION,
        fixture_snapshot_path=None,
        breaking_change_rules=_BREAKING_CHANGE_RULES,
        backward_compatibility_notes=(
            "The response is a local contract wrapper only. Optional metadata may be added, "
            "but status names and required identity fields must remain stable for v1."
        ),
        intended_consumer="Falcon internal evidence metadata and audit handoff flow.",
    ),
    SchemaName.FALCON_CARD_API_RESPONSE: SchemaRegistryEntry(
        schema_name=SchemaName.FALCON_CARD_API_RESPONSE.value,
        current_version=FALCON_CARD_API_RESPONSE_SCHEMA_VERSION,
        fixture_snapshot_path=None,
        breaking_change_rules=_BREAKING_CHANGE_RULES,
        backward_compatibility_notes=(
            "The API boundary version describes the response envelope. "
            "The nested card has its own schema_version and snapshot."
        ),
        intended_consumer="Future Falcon API/RPC client for Firm Intelligence card retrieval.",
    ),
    SchemaName.FALCON_PASSPORT_DETAIL_API_RESPONSE: SchemaRegistryEntry(
        schema_name=SchemaName.FALCON_PASSPORT_DETAIL_API_RESPONSE.value,
        current_version=FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION,
        fixture_snapshot_path=None,
        breaking_change_rules=_BREAKING_CHANGE_RULES,
        backward_compatibility_notes=(
            "The API boundary version describes the response envelope. "
            "Full passport detail and drawer schemas remain separate contracts."
        ),
        intended_consumer="Future Falcon API/RPC client for passport detail lookup.",
    ),
}


def get_schema_registry_entry(schema_name: SchemaName | str) -> SchemaRegistryEntry:
    """Return one schema registry entry by stable schema name."""

    key = schema_name if isinstance(schema_name, SchemaName) else SchemaName(str(schema_name))
    return SCHEMA_REGISTRY[key]


def schema_registry_to_dict() -> dict[str, dict[str, Any]]:
    """Serialize the registry for docs, tests, and future tooling."""

    return {
        schema_name.value: entry.to_dict()
        for schema_name, entry in SCHEMA_REGISTRY.items()
    }
