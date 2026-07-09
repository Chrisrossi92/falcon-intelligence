# Falcon Intelligence Architecture Index

This directory contains permanent Falcon Intelligence architecture foundations. These documents are documentation-only and do not authorize OCR, embeddings, extraction, OneDrive integration, Supabase changes, production APIs, source-document preview, report ingestion, or real report processing.

## Canonical Foundation

- `FALCON_INTELLIGENCE_ENGINE.md`: canonical lifecycle from Documents to Facts to Knowledge to Insights to Recommendations to Actions.
- `FALCON_KNOWLEDGE_MODEL.md`: canonical object model for appraisal knowledge.
- `FALCON_INSIGHT_ENGINE.md`: reusable framework for creating insights, recommendations, and operator actions from verified knowledge.
- `FALCON_CONFIDENCE_MODEL.md`: trust architecture for confidence, evidence, conflicts, freshness, verification, and explainability.
- `FALCON_HISTORICAL_INTAKE_PIPELINE.md`: local-only inventory and staging approach for historical orders and reports before any future extraction.
- `FALCON_HISTORICAL_KNOWLEDGE_EXTRACTION.md`: local-only deterministic Phase 1 metadata extraction from likely final reports after intake.
- `FALCON_VERIFICATION_ENGINE.md`: deterministic promotion boundary from candidate metadata to explainable Verified Facts.
- `FALCON_KNOWLEDGE_OBJECT_BUILDER.md`: local deterministic bridge from Verified Facts into Knowledge Object candidates before any future Memory Graph.
- `FALCON_MEMORY_GRAPH.md`: local deterministic graph prototype connecting Knowledge Objects into institutional memory.
- `FALCON_PROPERTY_PASSPORT.md`: preview-only operator surface for property-centered Verified Fact ledgers.

## Foundational Principle

All future AI and intelligence capabilities should declare where they operate in this hierarchy:

```text
Documents
-> Facts
-> Knowledge
-> Insights
-> Recommendations
-> Actions
```

Future implementation documents, UI contracts, data models, and production gates should align with these foundations before adding behavior.
