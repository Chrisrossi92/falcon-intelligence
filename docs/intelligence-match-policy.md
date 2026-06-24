# Intelligence Match Policy

This document defines how Falcon Intelligence should score, rank, warn, and explain matches shown in the future Falcon "Firm Intelligence Found" card. It is documentation-only. It does not authorize real data access, OneDrive access, report parsing, extraction, OCR, embeddings, or ingestion.

## Policy Status

Current implementation is synthetic-only. The current matcher and UI card schema are prototype scaffolding for future policy-aligned behavior. Production scoring must use tenant-scoped verified intelligence, appraiser-reviewed provenance, and auditable permission checks.

## Match Categories

The card may surface these match categories:

| Category | Purpose | Strong signals | Example explanation |
| --- | --- | --- | --- |
| Same subject | Identify prior work on the same property. | Exact normalized address, parcel, or verified property ID match. | "Prior verified assignment for the same subject property." |
| Nearby assignments | Surface prior work in the local area. | Same property, parcel proximity, distance band, submarket, or same neighborhood. | "Prior assignment in the same submarket within the local search radius." |
| Same client | Show prior work for the ordering client or borrower/contact. | Same verified client ID, normalized client name, same borrower/contact, or affiliated entity. | "Prior assignment for the same verified client." |
| Same property type | Find relevant firm knowledge for the asset class. | Matching verified property type and subtype. | "Verified assignment shares the same property type." |
| Similar size | Find comparable scale assignments or comps. | Building size within a policy-defined band, such as plus or minus 25%. | "Building size is within the policy size band." |
| Sale comps | Surface verified sale evidence. | Verified sale comp, same or nearby market, matching type/subtype, recent sale date. | "Verified sale comp matches on type, market, and size." |
| Lease comps | Surface verified lease evidence. | Verified lease comp, same or nearby market, matching type/subtype, recent lease date. | "Verified lease comp matches on type, market, and size." |
| Market indicators | Surface verified market context. | Same market/submarket, same property type, current date range, sufficient source count. | "Verified market indicator matches this market and property type." |

Stable category identifiers are defined in `src/falcon_intel/match_policy.py`. Future UI/API code should use these identifiers instead of display labels:

- `same_subject_property`
- `nearby_prior_assignments`
- `same_client`
- `same_property_type`
- `similar_building_size`
- `verified_sale_comps`
- `verified_lease_comps`
- `relevant_market_indicators`

## Scoring Principles

Scores are routing aids. They should help prioritize review, not decide valuation relevance.

Baseline scoring guidance:

- Same subject match: highest score when identity is verified by property ID, parcel, or normalized exact address.
- Verified comparable match: high score when property type, subtype, geography, size, and date all align.
- Nearby assignment: medium to high score depending on proximity and property-type fit.
- Same client: medium to high score as a workflow clue, but not valuation evidence by itself.
- Same property type: medium score unless supported by geography, subtype, size, or verified comparable status.
- Similar size: medium score when size is close; lower score when it is the only signal.
- Market indicator: score should reflect market match, property type, date range, source count, and confidence.

Scores should be explained with visible reasons. A user should be able to see why a match appeared without reverse-engineering the algorithm.

## Ranking Rules

Ranking should apply these rules in order:

1. Strongest evidence first: same subject and verified comparable evidence outrank loose metadata similarities.
2. Verified over suggested: verified records outrank suggested, unreviewed, rejected, or archived records.
3. Fresh over stale: current records outrank stale or historical records. Stale records should remain visible only when policy allows and warnings are clear.
4. Reviewed over unreviewed: reviewer-approved or appraiser-confirmed records outrank unreviewed extraction candidates.
5. Closer geography over broader market: same property, parcel, and local submarket outrank citywide, regional, or broad market matches.
6. More matching dimensions outrank fewer dimensions: type plus size plus geography outranks type alone.
7. Higher source quality outranks lower source quality: verified sale confirmation or signed lease evidence outranks informal notes or unverified metadata.

Rejected records should not appear in ordinary card output. Archived records should appear only through explicit archive review flows.

## Warning Rules

Warnings should be visible before a user relies on a match.

| Warning | When to show | Expected user effect |
| --- | --- | --- |
| Historical/stale comp | Comparable or indicator is beyond stale policy, old effective date, or market conditions have changed. | Require review and, when selected, justification. |
| Conflicting data | Same property or comp has conflicting verified facts, unresolved field conflicts, or superseded values. | Require evidence review before reuse. |
| Low confidence | Match score is low, key dimensions are weak, or evidence quality is limited. | De-emphasize and require careful review. |
| Unreviewed extraction | Record came from a suggested or extracted state without appraiser/reviewer approval. | Do not allow ordinary reuse until verification. |
| Different property subtype | Property type matches broadly, but subtype differs materially. | Show subtype difference and lower rank/score. |

Warnings should not be hidden inside tooltips only. They should be surfaced on the card row or detail panel with a clear code and human-readable explanation.

Stable warning identifiers include:

- `synthetic_preview_only`
- `appraiser_review_required`
- `stale_data_present`
- `stale`
- `conflicting_data`
- `low_confidence`
- `unreviewed_extraction`
- `different_property_subtype`

## Explanation Requirements

Each match should explain:

- Why it matched.
- Which dimensions contributed to score.
- Verification status.
- Freshness or stale status.
- Whether evidence is available.
- Any material limitation, subtype mismatch, or conflict.

Good explanations are short and concrete:

- "Verified sale comp matched on industrial property type, Sampleton market, and similar building size."
- "Prior assignment matched the same synthetic client but differs by property type."
- "Market indicator matched property type and market, but date range is historical."

Explanations must not imply a valuation conclusion.

## Appraiser Action Prompts

The card may offer these prompts:

| Prompt | Purpose | Audit expectation |
| --- | --- | --- |
| Use as reference | Keep the item visible as background context. | Audit optional unless tenant policy requires it. |
| Open evidence | Inspect provenance, data passport, source metadata, or approved evidence view. | Audit required. |
| Mark not relevant | Remove or down-rank the match for this order. | Audit required with optional reason. |
| Select for report consideration | Add comp/fact to the appraiser's working set for review. | Audit required. This is not final report use. |
| Justify historical comp use | Record why a stale or historical comp remains relevant. | Audit required; reviewer approval may be required by policy. |

Prompts should make the appraiser's responsibility explicit. The UI should avoid language that suggests automatic selection, automatic conclusions, or automatic report writing.

Stable action identifiers include:

- `review_top_matches`
- `confirm_relevance`
- `evaluate_comparable_reuse`
- `continue_standard_research`
- `use_as_reference`
- `open_evidence`
- `mark_not_relevant`
- `select_for_report_consideration`
- `justify_historical_comp_use`

## Audit Events

Falcon should create audit events for:

- `viewed_match`: user viewed a match row or detail panel.
- `opened_evidence`: user opened supporting evidence, data passport, or provenance detail.
- `selected_comp_fact`: user selected a comp, fact, or indicator for report consideration.
- `rejected_match`: user marked a match not relevant.
- `wrote_justification`: user entered justification for historical/stale comp use or policy override.

These event names are stable audit identifiers and should be used by future Falcon UI/API work.

Minimum audit context:

- Tenant/company ID.
- Order ID.
- User ID and role.
- Match category.
- Source entity ID and type.
- Card schema version.
- Match score and warnings shown.
- Action result.
- Timestamp.
- Justification text when required.

Audit events should be append-only. Selecting, rejecting, or justifying a match should not mutate the underlying verified intelligence record.

## Guardrails

Required guardrails:

- Matches are assistive.
- No automatic valuation conclusion may be generated from a match.
- No automatic report section, adjustment, value opinion, or comp selection may be generated from a match.
- The appraiser remains responsible for professional judgment.
- Every surfaced fact must be traceable to verified records and provenance.
- Source evidence must be permission-limited and tenant-scoped.
- Client-facing users must not see internal firm intelligence.
- Real report contents must not be read or summarized unless a future approved extraction and evidence-preview workflow exists.

## Current Synthetic Implementation

The current synthetic matcher uses simple structured-field scoring and deterministic UI card serialization. It is useful for schema and workflow testing only. Production policy implementation must add real tenant-scoped verification status, stale-date policy, conflict detection, subtype handling, reviewer status, evidence links, and audit persistence before it can govern live Falcon recommendations.

## Code Stability

Policy codes are stable integration identifiers. Display labels may change for UX clarity, but code values should not be renamed casually. If a code must be replaced, add a new code, document the migration, update the UI card snapshot deliberately, and preserve compatibility until Falcon consumers have migrated.

See `docs/falcon-integration-contract.md` for the Falcon API/RPC contract.
See `docs/data-confidence-provenance-model.md` for broader confidence and provenance dimensions.
