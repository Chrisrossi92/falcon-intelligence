# Synthetic Firm Intelligence Matcher

The synthetic firm intelligence matcher is the first local prototype for a future Falcon "Firm Intelligence Found" card.

It accepts a fake new order seed with:

- Address.
- City.
- State.
- Property type.
- Building size.
- Client.
- Optional borrower/contact.

The matcher compares that order only against committed synthetic verified intelligence fixtures under `tests/fixtures/synthetic_verified_intelligence/`. It does not use OneDrive, real assignments, report files, source documents, extracted text, OCR output, embeddings, or document content.

## Match Groups

The matcher returns stable groups for a future card:

- `same_subject_property`
- `nearby_prior_assignments`
- `same_property_type`
- `similar_building_size`
- `same_client`
- `verified_sale_comps`
- `verified_lease_comps`
- `relevant_market_indicators`

Each match includes:

- Source ID.
- Source type.
- Score from 0 to 100.
- Human-readable explanation.
- Compact structured details from the synthetic fixture.

Scores are simple routing signals. They are not valuation conclusions and should not be used automatically.

## Safety Boundary

The matcher requires every fixture record to be marked:

- `synthetic_fixture: true`
- `verification_status: verified`

The matcher rejects fixture records containing prohibited source-content fields such as `report_text` or `source_file_path`.

Current implementation guardrails:

- Synthetic fixture data only.
- No real OneDrive data.
- No report parsing.
- No file content reads.
- No OCR.
- No embeddings.
- No appraisal conclusions.

## Local Validation

Run the matcher smoke validation:

```bash
PYTHONPATH=src python3 scripts/smoke_synthetic_intelligence_matcher.py
```

Preview the future card shape from the CLI:

```bash
PYTHONPATH=src python3 -m falcon_intel.cli intelligence-card \
  --address "1000 Example Industrial Way" \
  --city "Sampleton" \
  --state "ST" \
  --property-type "industrial" \
  --building-size-sf 50000 \
  --client "Synthetic Lender A"
```

The CLI output is the UI-facing card schema with headline, order summary, match group summaries, top match cards, confidence/provenance summary, warnings, and recommended actions.

## UI Card Schema

The stable UI-facing schema is produced by `build_firm_intelligence_card`.

Example shape:

```json
{
  "schema_version": "1",
  "headline": "Firm Intelligence Found: 17 synthetic matches across 8 groups.",
  "order_summary": {
    "address": "1000 Example Industrial Way",
    "city": "Sampleton",
    "state": "ST",
    "property_type": "industrial",
    "building_size_sf": 50000,
    "client": "Synthetic Lender A"
  },
  "match_group_summaries": [
    {
      "group": "same_subject_property",
      "label": "Same Subject Property",
      "count": 1,
      "top_score": 100
    }
  ],
  "top_match_cards": [
    {
      "group": "same_subject_property",
      "source_id": "synthetic-assignment-industrial-alpha",
      "source_type": "assignment",
      "title": "Prior subject property",
      "score": 100,
      "explanation": "Exact synthetic address, city, and state match.",
      "confidence_label": "high",
      "provenance": {
        "verification_status": "verified",
        "synthetic_fixture": true,
        "record_type": "assignment",
        "source_id": "synthetic-assignment-industrial-alpha"
      },
      "stale_data_flags": [],
      "details": {
        "property_type": "industrial",
        "building_size_sf": 50000
      }
    }
  ],
  "confidence_provenance_summary": {
    "total_matches": 17,
    "verified_match_count": 16,
    "synthetic_fixture_only": true,
    "highest_score": 100,
    "source_fixture_kind": "synthetic_verified_intelligence",
    "source_fixture_version": "1"
  },
  "warnings": [
    {
      "code": "synthetic_preview_only",
      "severity": "info",
      "message": "Synthetic preview only; do not use as production firm intelligence."
    }
  ],
  "recommended_actions": [
    {
      "code": "review_top_matches",
      "label": "Review top matches",
      "reason": "Synthetic verified intelligence matches were found for this fake order."
    }
  ]
}
```

Stale data flags are currently fixture-driven. A synthetic record can mark `stale_after` as `expired` to surface a `stale` flag and a card-level `stale_data_present` warning. Future production stale logic must use verified dates and firm policy.

## Versioned UI Snapshot

The committed v1 UI card snapshot lives at:

```text
tests/fixtures/synthetic_ui_cards/firm-intelligence-card-v1.json
```

The snapshot is generated only from the fake order used in tests and the synthetic verified intelligence fixture. It is intended for future frontend and Falcon integration work to detect schema drift.

Snapshot tests compare the current serializer output exactly against this file. If a card schema change is intentional, update the serializer, update the docs, regenerate the snapshot deliberately, and review the JSON diff before committing. Do not update the snapshot just to make tests pass.

Run the full local suite after installing the dev extra:

```bash
PYTHONPATH=src python3 -m compileall -q src scripts tests
PYTHONPATH=src python3 scripts/smoke_synthetic_fixtures.py
PYTHONPATH=src python3 scripts/smoke_synthetic_intelligence_matcher.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_schema.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_snapshot.py
PYTHONPATH=src python3 scripts/smoke_intelligence_card_cli.py
PYTHONPATH=src python3 -m pytest
```

## Future Falcon Order Matching

In a future Falcon/Supabase implementation, this module can map to the order intelligence loop described in `docs/falcon-order-intelligence-loop.md`. Production matching must remain tenant-scoped, appraiser-reviewed, permission-aware, and backed by verified firm intelligence records with provenance and audit history.
