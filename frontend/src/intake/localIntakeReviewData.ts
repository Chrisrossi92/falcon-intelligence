import workspaceFixture from "../../../tests/fixtures/synthetic_intake_review/local-intake-review-workspace-v1.json";

export type ReviewState =
  | "extracted_candidate"
  | "unresolved_conflict"
  | "accepted"
  | "corrected"
  | "rejected"
  | "deferred";

export type EvidenceLocator = {
  page_number: number | null;
  section: string | null;
  table: string | null;
  cell: string | null;
  paragraph: string | null;
  region: string | null;
};

export type ReviewEvidence = {
  evidence_id: string;
  source_document: string;
  safe_reference: string;
  locator: EvidenceLocator;
  extraction_method: string;
  confidence: string;
  quality: string;
};

export type ReviewCandidate = {
  candidate_id: string;
  field_key: string;
  label: string;
  value: unknown;
  original_value?: unknown;
  normalized_value: string;
  value_type: string;
  unit: string | null;
  material: boolean;
  machine_verification_status: string;
  machine_confidence: string;
  state: ReviewState;
  conflict_ids: string[];
  latest_review: {
    action: string;
    actor_name: string;
    actor_role: string;
    occurred_at: string;
    reason: string;
  } | null;
  evidence: ReviewEvidence[];
  available_actions: string[];
};

export type ReviewTopic = {
  topic_key: string;
  label: string;
  candidates: ReviewCandidate[];
};

export type BriefFact = {
  fact_id: string;
  field_key: string;
  label: string;
  value: unknown;
  value_type: string;
  unit: string | null;
  fact_state: string;
  origin: string;
  professional_boundary: string;
  evidence_ids: string[];
};

export type BriefIssue = {
  issue_id: string;
  area: string;
  issue_type: string;
  severity: string;
  field_keys: string[];
  related_ids: string[];
  message: string;
};

export type BriefLead = {
  reference_id: string;
  lead_type: string;
  relationship: string;
  selection_status: string;
  freshness: string;
  evidence_ids: string[];
  notes: string[];
};

export type AssignmentBrief = {
  brief_format: string;
  brief_version: string;
  air_schema_version: string;
  air_record_id: string;
  air_record_version: number;
  generated_at: string;
  assignment_synopsis: BriefFact[];
  assignment_contacts: Array<Record<string, string>>;
  subject_synopsis: BriefFact[];
  ownership_references: Array<Record<string, string>>;
  issues_requiring_attention: BriefIssue[];
  evidence_summary: Array<{
    evidence_id: string;
    fact_ids: string[];
    source_document: string;
    safe_reference: string;
    locator: EvidenceLocator;
    extraction_method: string;
    confidence: string;
    quality: string;
    freshness: string;
  }>;
  comparable_and_market_leads: BriefLead[];
  readiness_status: string;
  readiness_areas: Array<{ area: string; status: string; issue_ids: string[] }>;
  professional_conclusions: Array<Record<string, unknown>>;
  professional_boundary: string[];
};

export type ReviewConflict = {
  conflict_id: string;
  field_key: string;
  candidate_ids: string[];
  evidence_ids: string[];
  status: "resolved" | "unresolved";
  material: boolean;
  reason: string;
  resolution_event_ids: string[];
};

export type LocalIntakeReviewWorkspaceData = {
  schema_version: string;
  workspace_type: string;
  semantic_source: {
    canonical_model: string;
    air_schema_version: string;
    air_record_id: string;
    air_record_version: number;
    adapter_mode: string;
  };
  assignment: {
    label: string;
    local_assignment_key: string;
    lifecycle_state: string;
    overview: BriefFact[];
  };
  review_progress: {
    total_candidates: number;
    reviewed_candidates: number;
    percent_complete: number;
    counts: Record<string, number>;
  };
  topics: ReviewTopic[];
  conflicts: ReviewConflict[];
  readiness: {
    overall_status: string;
    blocking_issue_ids: string[];
    nonblocking_issue_ids: string[];
    areas: Array<{
      area: string;
      status: string;
      required_field_keys: string[];
      current_fact_ids: string[];
      issue_ids: string[];
    }>;
    issues: BriefIssue[];
  };
  missing_critical_information: BriefIssue[];
  air: Record<string, unknown>;
  brief: AssignmentBrief;
  brief_markdown: string;
  export_formats: string[];
  guardrail: string;
};

export const localIntakeReviewData = workspaceFixture as LocalIntakeReviewWorkspaceData;

export function formatReviewValue(value: unknown, unit?: string | null) {
  const rendered =
    typeof value === "string"
      ? value
      : JSON.stringify(value, null, typeof value === "object" ? 2 : undefined);
  return unit ? `${rendered} ${unit.replaceAll("_", " ")}` : rendered;
}

export function formatReviewLabel(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function evidenceLocatorLabel(locator: EvidenceLocator) {
  const parts = [
    locator.page_number ? `Page ${locator.page_number}` : null,
    locator.section,
    locator.table ? `Table ${locator.table}` : null,
    locator.cell ? `Cell ${locator.cell}` : null,
    locator.paragraph ? `Paragraph ${locator.paragraph}` : null,
    locator.region
  ].filter(Boolean);
  return parts.join(" · ") || "Source-level locator";
}
