# Intelligence Map Workspace Contract

This document defines a synthetic/local contract for a future Falcon Intelligence Map Workspace. It does not authorize real data access, OneDrive access, extraction, OCR, embeddings, source-document preview, Google Maps API integration, or production map services.

## UI Concept

The future workspace should combine filters, a scrollable intelligence table, and a map:

- Left filter sidebar: property type, record type, status, verification status, stale flag, city, and state.
- Top scrollable table: active orders, assignments, comps, current subject records, and verified intelligence records.
- Bottom interactive map: pins for the same filtered records shown in the table.
- Table filters update map pins immediately.
- Map pin selection highlights the matching table row.
- Table row selection zooms to and highlights the matching map pin.

The current implementation is a data contract only. It does not render a UI and does not call Google Maps or any other map provider.

The stable v1 UI response snapshot lives at:

```text
tests/fixtures/synthetic_ui_map_workspace/map-workspace-response-v1.json
```

## Synthetic Fixture

Synthetic map records live at:

```text
tests/fixtures/synthetic_map_workspace/map-records.json
```

The fixture includes:

- Active order.
- Completed assignment.
- Verified sale comp.
- Verified lease comp.
- Historical comp.
- Current subject.

All addresses and coordinates are fake synthetic data.

## Record Model

The local `SyntheticMapRecord` model includes:

- `id`
- `record_type`
- `display_label`
- `address`
- `city`
- `state`
- `latitude`
- `longitude`
- `property_type`
- `status`
- `verification_status`
- `confidence_summary`
- `passport_id`
- `evidence_link_count`
- `stale_flag`

## Filters

`filter_map_records` supports:

- `property_type`
- `record_type`
- `status`
- `verification_status`
- `stale_flag`
- `city`
- `state`

Filters are exact-match and case-insensitive for string fields. `stale_flag` is a boolean filter.

## UI Response Serializer

`build_map_workspace_response` returns:

- `schema_version`: current UI response schema version.
- `table_rows`: filtered records for the top table.
- `map_pins`: filtered map pin summaries.
- `selected_record`: selected record detail when the selected ID is in the filtered result set.
- `result_counts`: total records, filtered count, pin count, stale count, and counts by record type.
- `available_filters`: available filter values derived from the full synthetic fixture.

Selection behavior:

- If `selected_record_id` matches a filtered record, that table row and map pin include `is_selected: true`.
- If `selected_record_id` is outside the filtered set, `selected_record` is `null` and no row or pin is selected.

Snapshot behavior:

- The committed v1 snapshot uses an industrial filter and selected sale comp.
- Snapshot tests compare the current serializer output exactly against the fixture.
- Update the snapshot only when a map workspace schema change is intentional and reviewed.

## Safety Boundary

The map workspace contract is synthetic/local only:

- No real addresses or client data.
- No OneDrive access.
- No report reading.
- No extraction, OCR, embeddings, or source-document preview.
- No Google Maps API implementation.
- No production database or tenant auth.

Future production work must use tenant-scoped records, production auth, audit logging, and an approved map provider policy before showing real locations.
