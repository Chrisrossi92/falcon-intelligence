# Intelligence Workspace Falcon Shell Integration

This document begins V2C: Falcon Shell Integration / Design System Extension for Falcon Intelligence. It is documentation-only. It does not authorize React UI, backend architecture, schema changes, real data access, OneDrive access, extraction, OCR, embeddings, source-document preview, production database/auth, or production map provider integration.

Falcon Intelligence should feel like a premium Intelligence module inside Falcon, not a separate product. It should inherit the Falcon shell and extend it only where spatial intelligence, provenance, evidence, and audit require new workspace patterns.

## Falcon Intelligence UX Commandments

These are non-negotiable UI principles for Falcon Intelligence:

1. The map is the primary workspace, not decoration.
2. Every fact must lead to its evidence.
3. Every piece of evidence must lead to its audit history.
4. Never replace an appraiser's judgment with AI output.
5. Drawers preserve context; pages discard it.
6. The interface should feel operational, not analytical.
7. Users should always know where they are, what they know, and why they know it.
8. If trust and visual simplicity conflict, trust wins.
9. Intelligence supports Falcon's workflow; it never competes with it.
10. When in doubt, make the interface quieter, not busier.

## Falcon Shell Alignment

Falcon Intelligence should run inside the inherited Falcon shell. The user should feel they are still working in Falcon, with Intelligence acting as a premium internal knowledge module that extends the appraisal workflow.

### Inherited Shell

Use the same shell structure, spacing discipline, typography direction, navigation behavior, and restrained visual tone as Falcon Core. Intelligence should not introduce a separate app chrome, separate brand system, or novelty AI interface.

The shell should preserve:

- Stable sidebar location.
- Familiar top navigation behavior.
- Existing account, tenant, and role context placement.
- Falcon-style page/workspace titles.
- Operational density where professional review requires it.
- Drawer-based progressive disclosure.

### Sidebar Placement

The future Falcon sidebar should place Intelligence as a first-class module after core work-management areas:

```text
Dashboard
Orders
Calendar
Clients

Intelligence

Administration
```

Inside Intelligence, the module navigation should remain:

```text
Overview
Map
Subjects
Sales
Leases
Reports
Market
```

Map is the primary workspace. Overview should summarize state and workflow, but Map is where users orient, inspect, select, and open provenance.

### Top Navigation Behavior

Top navigation should preserve Falcon's global context rather than becoming a map-toolbar replacement.

Expected behavior:

- Keep tenant, user, and role context in the normal Falcon shell position.
- Keep workspace title and current module context visible.
- Keep global navigation stable when drawers open.
- Avoid adding a second product-level nav inside the map.
- Use contextual controls in the workspace header, filter rail, layer panel, or table toolbar instead of crowding the top shell.

### Workspace Labels

Workspace labels should be clear and operational:

- "Intelligence / Map"
- "Verified Knowledge"
- "Passport"
- "Evidence"
- "Audit History"
- "Permission Restricted"
- "Reviewer Pending"
- "Stale"

Avoid labels that imply automation or conclusion:

- "AI Insights"
- "Smart Answers"
- "Best Comps"
- "Auto Verified"
- "Predicted Value"

### Restrained Visual System

Falcon Intelligence should use a restrained visual system:

- Neutral shell palette inherited from Falcon.
- Small, meaningful status accents.
- Dense professional data where required.
- Compact drawers and tables.
- Clear disabled and restricted states.
- Confidence and verification treatment that is visible but not dominant.

Avoid:

- Gimmicky AI gradients.
- Glowing badges or animated trust indicators.
- Wall-of-cards dashboard patterns.
- Marketing-style hero panels.
- Decorative map art that competes with the actual workspace.
- Overly colorful layer states that make verification status hard to read.

## Component Reuse / Extension / New Component Matrix

| Component | Status | Notes |
| --- | --- | --- |
| Top navigation | Reuse | Same Falcon shell behavior. It should preserve tenant, role, and global workspace context. |
| Sidebar | Reuse/extend | Adds Intelligence section and Intelligence subnavigation without changing Core navigation behavior. |
| Cards | Reuse sparingly | Useful for compact summaries, but avoid dashboard walls and repeated card grids as the primary workspace. |
| Tables | Extend | Adds synchronized map behavior, selected-row coordination, stale indicators, verification states, and evidence/passport affordances. |
| Drawers | Extend | Supports Passport, Evidence, and Audit drawers while preserving map/table context. |
| Search | Extend | Adds Intelligence-aware filtering/search over synthetic workspace records without implying production retrieval or embeddings. |
| Status badges | Extend | Supports Verified, AI Suggested, Reviewer Approved, Reviewer Pending, Stale, Permission Restricted, Evidence Unavailable, and Preview Blocked states. |
| Map canvas | New | Primary Intelligence workspace for spatial orientation and property/comparable context. Current work remains synthetic/provider-free. |
| Layer panel | New | Future GIS-style layer controls for Subjects, Sales, Leases, Reports, Verified Knowledge, AI Suggestions, Reviewer Flags, Market Areas, and Comparable Clusters. |
| Property marker | New | Verification-aware geospatial markers that distinguish selected, verified, stale, suggested, permission-limited, and disabled records. |
| Context bar | New | Persistent plain-language explanation of the current workspace knowledge context. |

New components must extend Falcon's design language. They should not introduce a second visual system.

## Visual Hierarchy

Use this hierarchy for Falcon Intelligence workspace composition:

```text
Falcon Shell
-> Workspace Header
-> Intelligence Workspace
-> Filter Rail / Map / Layers
-> Bottom Intelligence Table
-> Context Drawers
-> Passport / Evidence / Audit
```

Hierarchy rules:

- Falcon Shell remains the outer product frame.
- Workspace Header names the current Intelligence surface and selected scope.
- Intelligence Workspace owns the map, filters, table, layers, and context bar.
- Filter Rail / Map / Layers provide orientation and scope control.
- Bottom Intelligence Table provides dense record review and synchronization with the map.
- Context Drawers preserve map/table context while progressively disclosing detail.
- Passport / Evidence / Audit are nested trust surfaces, not standalone destinations.

## Context Bar

The Context Bar is a future UI concept for Falcon Intelligence. It is a compact, persistent, plain-language sentence that explains where the user is in the firm's knowledge.

It is not breadcrumbs. Breadcrumbs explain navigation path. The Context Bar explains current knowledge context.

Examples:

- Northwest Industrial Market - 48 Verified Properties - 126 Comparable Sales
- 1420 Commerce Drive - 6 Verified Facts - 14 Related Assignments
- Floor Area - Verified - Reviewer Approved - Source: Report 2024-118
- Floor Area - Last Approved May 12, 2025 by Pam Casper

Behavior:

- Updates when the map selection changes.
- Updates when the table selection changes.
- Updates when a passport opens.
- Updates when evidence is selected.
- Updates when audit history is in focus.
- Remains compact and visible while drawers open.
- Uses plain language before icons or badges.
- Avoids confidence language unless it comes from the current contract or approved future source.

Placement:

- Prefer placement below the Workspace Header and above the map/table workspace.
- It may compress or truncate at small widths, but it should not wrap into a distracting paragraph.
- It should remain subordinate to the workspace title and primary map surface.

Content rules:

- Use verified counts only when they are available from the current workspace data.
- Do not show restricted facts, source labels, or audit identities to users without access.
- Do not imply a fact is searchable if verification or reviewer approval is incomplete.
- Do not turn the Context Bar into a chat-style answer.
- Do not use it to announce AI conclusions.

Design tone:

- Calm.
- Compact.
- Falcon-like.
- Useful for orientation.
- Quieter than alerts, stronger than incidental helper text.

## Design-System Extension Rules

Before adding a new Intelligence component, decide whether Falcon already has a reusable equivalent:

1. Reuse existing Falcon shell and controls when behavior is identical.
2. Extend existing components when Intelligence adds provenance, permission, stale, or map synchronization behavior.
3. Add new components only for genuinely new Intelligence workspace needs, such as map canvas, layer panel, property marker, and context bar.

Extension should be narrow. A table with synchronized map selection is still a Falcon table. A drawer with evidence metadata is still a Falcon drawer. A status badge with reviewer pending state is still a Falcon status badge.

## Non-Goals

This V2C milestone does not include:

- React UI implementation.
- New backend architecture.
- Schema changes.
- Real extraction.
- OCR.
- Embeddings.
- OneDrive access.
- Source-document preview.
- Production auth or production database.
- Production map provider integration.
- AI-generated conclusions.
- Client-visible Intelligence surfaces.

## V2C Completion Criteria

V2C is complete when:

- Falcon Intelligence UX Commandments are documented.
- Falcon shell alignment is documented.
- Component reuse, extension, and new component boundaries are documented.
- Canonical visual hierarchy is documented.
- Context Bar concept is documented.
- Existing V2A and V2B constraints remain intact.
- No React UI, backend architecture, schema changes, real extraction, OCR, embeddings, source preview, OneDrive access, production auth/database, or production map provider work is added.

