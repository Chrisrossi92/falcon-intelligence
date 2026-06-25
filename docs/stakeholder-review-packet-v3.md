# Falcon Intelligence Stakeholder Review Packet V3

This packet supports a guided stakeholder review of the current Falcon Intelligence internal preview. It is documentation-only and does not authorize UI changes, feature expansion, schema changes, backend architecture, production map provider integration, real data access, source preview, extraction, OCR, embeddings, OneDrive access, production authentication, or production database work.

Use this packet with appraisers, reviewers, owners, and admins to evaluate comprehension, trust, and workflow value before expanding the product surface.

## 1. Purpose

Falcon Intelligence is being reviewed as an internal synthetic preview. The goal is not to prove production readiness. The goal is to learn whether stakeholders understand the trust workflow and believe it could save time in future appraisal work.

The preview should help reviewers answer:

- Do users understand what Falcon Intelligence is for?
- Do users know what to click first?
- Does the Map to Knowledge Summary to Passport to Evidence to Audit Timeline chain make sense?
- Does the experience feel like Falcon rather than a separate AI dashboard?
- Does the trust model feel defensible?
- Would this be faster than digging through old reports or prior workfiles?

The reviewer should guide the walkthrough. Do not present this as a finished product or a self-serve production pilot.

## 2. Non-Goals Disclaimer

State this clearly before the walkthrough:

- No real reports are used.
- No OCR is used.
- No extraction is used.
- No OneDrive access is used.
- No production database or authentication is used.
- No source document preview exists.
- No production map provider is integrated.
- All data is synthetic, local, and committed for preview/testing only.
- Evidence is metadata-only.
- Audit Timeline is synthetic fixture-backed history only, not production audit persistence.
- Falcon Intelligence assists appraisers and reviewers. It does not make valuation conclusions.

Suggested opening language:

> This is a synthetic internal preview. We are reviewing whether the workflow makes sense and whether the trust model feels useful. We are not reviewing real data, source documents, extraction, OCR, OneDrive, production permissions, or production maps.

## 3. Demo Script

### Step 1: Open Intelligence Workspace

Show the Falcon shell with Intelligence selected.

Say:

> Falcon Core manages work. Falcon Intelligence remembers verified institutional knowledge from prior work. This workspace is the Map view, intended to become the primary place to explore firm knowledge spatially.

Ask observers to note what they would click first before prompting them.

### Step 2: Explain the Map-First Concept

Point to the map, table, Context Bar, filter rail, and layer panel.

Say:

> The map is the primary workspace. The table explains the map. The Context Bar explains where we are in the firm's knowledge. The layer controls are preview-only toggles for different kinds of intelligence.

Watch whether they look at the map or table first.

### Step 3: Select a Property From the Map

Click a map marker.

Show:

- Marker selected state.
- Matching table row selected state.
- Context Bar update.
- Knowledge Summary update.

Say:

> Selection is synchronized. Choosing a property on the map selects the matching table row and updates the Knowledge Summary.

### Step 4: Show Knowledge Summary

Point out:

- Property identity.
- Trust status.
- Verified fact count.
- Evidence count.
- Audit activity.
- Last review/verification metadata if present.
- Open Passport action.

Say:

> The Knowledge Summary answers what we know at a glance and whether there is support behind it. It does not replace appraiser judgment.

Ask:

> Before opening Passport, do you understand whether this property has useful firm knowledge?

### Step 5: Open Passport

Click Open Passport.

Show sections:

- Identity.
- Verified Knowledge.
- Evidence.
- Verification / Review.
- Related Work.

Say:

> Passport is the property's trust record. It is meant to feel like opening the case file for the selected knowledge record.

Ask:

> Does this give you the right level of detail after the summary?

### Step 6: Open Evidence

Click Open evidence in Passport.

Show sections:

- Evidence Summary.
- Source Metadata.
- Trust Context.
- Audit Handoff.

Say:

> Evidence explains why the knowledge is trusted. In this preview it is metadata-only. It does not open a source report or preview document contents.

Ask:

> Does metadata-only evidence still help you decide whether the fact is worth trusting or reviewing further?

### Step 7: Open Audit Timeline

Click Open audit.

Show sections:

- Timeline Summary.
- Chronological Timeline.
- Current Status.

Say:

> Audit Timeline is the accountability trail. It should answer who changed the knowledge, when, and what happened. These events are synthetic fixtures, not production audit history.

Ask:

> Would this support defensibility or review accountability?

### Step 8: Close Drawers Back to Map

Close Audit, then Evidence, then Passport.

Show:

- Evidence remains after closing Audit.
- Passport remains after closing Evidence.
- Map/table/Knowledge Summary selection remains after closing Passport.

Say:

> Drawers preserve context. The user should not lose the property or workspace state while inspecting trust details.

### Step 9: Toggle Layers

Toggle:

- Subjects.
- Verified Knowledge.
- Evidence Available.
- Reviewer/Audit Activity.

Say:

> Layers are preview-only controls showing how future intelligence layers may affect map markers, badges, or visibility.

Watch for confusion about whether layers filter, annotate, or both.

### Step 10: Show States If Useful

Use the preview-only state simulator only if the stakeholder understands it is internal tooling.

Show selectively:

- Stale data.
- Permission denied.
- Evidence unavailable.
- Audit unavailable.

Say:

> Trust is the product, so bad states must be explicit. The preview shows how unavailable, stale, or restricted knowledge should look without leaking facts.

Do not dwell on the simulator unless the stakeholder is evaluating risk or product operations.

## 4. Stakeholder Questions

### For Appraisers

- Would this help you remember prior work?
- Does the Knowledge Summary tell you enough before opening Passport?
- Does Passport feel like the right place for a full property trust record?
- Does Evidence explain why a fact is trusted?
- Does Audit help with defensibility?
- Would this feel faster than searching old reports or workfiles?
- What feels confusing?
- What would make you stop trusting the information?
- What would you want surfaced earlier?
- What would you hide until later?

### For Reviewers

- Does the audit/review flow feel accountable?
- What verification status matters most?
- What would you need before approving firm knowledge?
- Does the Audit Timeline answer who changed knowledge, when, and what happened?
- Does Evidence provide enough support before source preview exists?
- What stale, conflicting, or incomplete states would you need to see?
- Where should reviewer approval appear?
- What language could imply too much certainty?

### For Owners/Admins

- Does this feel like a premium Falcon module?
- Does it feel connected to Falcon rather than separate?
- Would this save time across future assignments?
- What would make it worth paying for?
- What roles should be allowed to see Passport, Evidence, and Audit?
- What risk controls are mandatory before production?
- Would metadata-only evidence be useful before source preview exists?
- What would block firm adoption?

## 5. Observation Checklist

Capture during the walkthrough:

- First thing they click.
- Whether they understand the map/table relationship.
- Whether they notice the Context Bar.
- Whether they understand Knowledge Summary.
- Whether they understand why Passport matters.
- Whether they understand Evidence is metadata-only.
- Whether they understand Audit proves accountability, not valuation correctness.
- Whether Passport/Evidence/Audit flow makes sense.
- Whether they can recover context after opening drawers.
- Where they hesitate.
- Where they ask for source documents.
- Where they ask about permissions.
- Where they ask about reviewer approval.
- Whether they confuse synthetic data with real firm data.
- Whether they describe the product as memory, search, map, audit, AI, report lookup, comp tool, or something else.
- Words they use to describe value.
- Words they use to describe risk.

## 6. Pass/Fail Criteria Before V4

Pass signals:

- User understands the trust chain without heavy explanation.
- User can explain why the map matters.
- User can explain what the Knowledge Summary means.
- User can explain why Passport matters.
- User can explain why Evidence matters.
- User can explain what Audit proves.
- User does not mistake synthetic metadata for live source documents.
- User sees Falcon Intelligence as connected to Falcon, not a separate app.
- User understands that appraiser judgment remains final.
- User believes the workflow could be faster than digging through old reports.

Fail signals:

- User cannot identify what to click first.
- User thinks Falcon Intelligence is making valuation conclusions.
- User thinks Evidence opens source documents.
- User thinks Audit means reviewer approval when the fixture does not support that.
- User ignores the map and treats the product as only a table.
- User cannot explain why Passport is different from Knowledge Summary.
- User loses context after drawers open.
- User sees the preview as generic AI dashboard behavior.
- User cannot name a time-saving use case.
- User does not trust the verification/evidence/audit language.

Minimum bar before V4 implementation expansion:

- At least one appraiser and one reviewer can explain the trust chain in their own words.
- At least one owner/admin can explain why this belongs inside Falcon.
- No reviewer mistakes the preview for production data or source-document access.
- The team identifies no fatal terminology issue around Knowledge Summary, Passport, Evidence, or Audit Timeline.

## 7. Feedback Capture Template

Use one copy per stakeholder.

```text
Reviewer name:
Role:
Date:

Walkthrough notes:

First thing they clicked:

Did they understand map/table synchronization?

Did they notice the Context Bar?

Did they understand Knowledge Summary?

Did they understand Passport?

Did they understand Evidence is metadata-only?

Did they understand Audit Timeline?

Confusion points:

Strongest value moment:

Biggest concern:

Must-fix before pilot:

Nice-to-have:

Quotes / exact wording they used:

Go / no-go recommendation:

Follow-up owner:
```

## 8. Recommended Next Decision

After stakeholder review, decide one of the following:

1. Refine UX.
   Choose this if stakeholders understand the concept but stumble on wording, hierarchy, map emphasis, layer behavior, or drawer scanability.

2. Begin V4 production metadata pilot planning.
   Choose this only if stakeholders understand the trust chain, value the workflow, and do not confuse the preview with source-document access or valuation automation.

3. Pause for more design.
   Choose this if Passport, Evidence, Audit, or the map-first model does not make sense without heavy explanation.

4. Prepare Falcon Core integration plan.
   Choose this if the workflow is understood and stakeholders agree the next risk is placement inside Falcon Core rather than more standalone preview work.

Recommended default:

Run the guided review, collect feedback, then refine UX and begin V4 planning in parallel. Do not start real data, source preview, extraction, OCR, embeddings, OneDrive, production auth, production database, or production map provider work until the existing readiness gates explicitly allow it.
