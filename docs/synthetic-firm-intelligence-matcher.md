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

Run the full local suite after installing the dev extra:

```bash
PYTHONPATH=src python3 -m compileall -q src scripts tests
PYTHONPATH=src python3 scripts/smoke_synthetic_fixtures.py
PYTHONPATH=src python3 scripts/smoke_synthetic_intelligence_matcher.py
PYTHONPATH=src python3 -m pytest
```

## Future Falcon Order Matching

In a future Falcon/Supabase implementation, this module can map to the order intelligence loop described in `docs/falcon-order-intelligence-loop.md`. Production matching must remain tenant-scoped, appraiser-reviewed, permission-aware, and backed by verified firm intelligence records with provenance and audit history.
