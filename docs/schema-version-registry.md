# Schema Version Registry

Falcon Intelligence keeps a lightweight schema version registry for UI and local API/RPC contract objects. The registry lives in `src/falcon_intel/schema_registry.py` and is synthetic-only.

This registry does not authorize real appraisal data, OneDrive access, report parsing, extraction, OCR, embeddings, or source-document preview.

## Current Schemas

| Schema | Current version | Snapshot fixture | Intended consumer |
| --- | --- | --- | --- |
| `firm_intelligence_found_card` | `1` | `tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json` | Falcon internal Order Detail, New Order intake, and Assignment workspace UI. |
| `passport_detail_drawer` | `1` | `tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json` | Falcon internal passport detail drawer. |
| `falcon_evidence_open_response` | `1` | `tests/fixtures/synthetic_api_envelopes/falcon-evidence-open-api-response-v1.json` | Falcon internal evidence metadata and audit handoff flow. |
| `falcon_card_api_response` | `1` | `tests/fixtures/synthetic_api_envelopes/falcon-card-api-response-v1.json` | Future Falcon API/RPC client for Firm Intelligence card retrieval. |
| `falcon_passport_detail_api_response` | `1` | `tests/fixtures/synthetic_api_envelopes/falcon-passport-detail-api-response-v1.json` | Future Falcon API/RPC client for passport detail lookup. |
| `audit_event_envelope` | `1` | `tests/fixtures/synthetic_audit_events/` | Future Falcon audit persistence and internal compliance handoff. |

The API response schema versions describe the response envelopes. Nested UI objects keep their own schema versions. For example, `build_falcon_intelligence_card_response` returns a `schema_version` for the Falcon response envelope and a separate `card.schema_version` for the Firm Intelligence Found card.

Passport detail, evidence-open, and audit event snapshots include suggested audit payloads. Their generated audit timestamps are normalized to `synthetic-dynamic-timestamp` so snapshot tests detect schema drift without depending on wall-clock time.

## Registry Constants

Use these constants instead of hard-coded version strings:

- `FIRM_INTELLIGENCE_CARD_SCHEMA_VERSION`
- `PASSPORT_DETAIL_DRAWER_SCHEMA_VERSION`
- `FALCON_EVIDENCE_OPEN_RESPONSE_SCHEMA_VERSION`
- `FALCON_CARD_API_RESPONSE_SCHEMA_VERSION`
- `FALCON_PASSPORT_DETAIL_API_RESPONSE_SCHEMA_VERSION`
- `AUDIT_EVENT_ENVELOPE_SCHEMA_VERSION`

Current serializers and contract wrappers source versions from the registry constants.

## Breaking Change Rules

Create a new schema version when any of these change:

- A required field is removed.
- A field is renamed.
- A field type changes.
- A field's meaning, units, status semantics, or enum values change.
- A consumer must change code to keep working.

The following are usually backward-compatible:

- Adding a new optional field.
- Adding a new optional warning or metadata block that existing consumers can ignore.
- Clarifying documentation without changing payload shape or semantics.

## Snapshot Rules

UI-facing schemas with committed snapshots must be updated deliberately.

When a schema change is intentional:

1. Update the relevant registry constant only if the schema version changes.
2. Regenerate or add the matching fixture snapshot.
3. Review the JSON diff.
4. Update tests and smoke validation.
5. Update this document and the Falcon integration notes.

Do not overwrite snapshots as a side effect of unrelated work.

## Safety Boundary

All current registry entries refer to synthetic/local contract objects. They must not point at real source files, OneDrive paths, report contents, extracted text, OCR outputs, embeddings, vector stores, or databases.
