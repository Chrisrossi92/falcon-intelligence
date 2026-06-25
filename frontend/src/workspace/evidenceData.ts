import evidenceOpenSnapshot from "../../../tests/fixtures/synthetic_api_envelopes/falcon-evidence-open-api-response-v1.json";
import { formatLabel } from "./mapWorkspaceData";
import type { EvidenceLink, PassportPreview } from "./passportData";

type EvidenceOpenSnapshot = {
  evidence_id: string;
  evidence_summary: EvidenceLink & {
    has_future_anchor: boolean;
    source_document_id: string;
  };
  order_id: string;
  passport_id: string;
  status: string;
  suggested_audit_event?: {
    event_code: string;
    match_id: string;
    metadata: Record<string, string>;
    order_id: string;
    tenant_id: string;
    timestamp: string;
    user_id: string;
  };
  tenant_id: string;
  user_id: string;
};

export type EvidencePreview = {
  auditHandoff: {
    eventCode: string;
    isAvailable: boolean;
    message: string;
  };
  confidenceContext: string;
  evidenceId: string;
  openStatus: string;
  passportId: string;
  provenanceRows: Array<{ label: string; value: string }>;
  sourceDocumentId: string;
  sourceDocumentType: string;
  title: string;
  unavailableMessage: string;
};

const evidenceOpen = evidenceOpenSnapshot as EvidenceOpenSnapshot;

export function buildEvidencePreview(evidence: EvidenceLink, passport: PassportPreview): EvidencePreview {
  if (evidence.evidence_id === evidenceOpen.evidence_id && passport.identity.passportId === evidenceOpen.passport_id) {
    return fromEvidenceOpenContract(passport);
  }

  return {
    auditHandoff: {
      eventCode: "Not present in current evidence-open contract",
      isAvailable: false,
      message: "Review history is not available for this supporting evidence in the current preview."
    },
    confidenceContext: passport.confidenceSummary,
    evidenceId: evidence.evidence_id,
    openStatus: formatLabel(evidence.status),
    passportId: passport.identity.passportId,
    provenanceRows: [
      { label: "Access level", value: formatLabel(evidence.access_level) },
      { label: "Supporting evidence status", value: formatLabel(evidence.status) },
      { label: "Passport", value: passport.identity.passportId },
      { label: "Tenant", value: evidence.tenant_id ?? passport.identity.tenantId }
    ],
    sourceDocumentId: "Not available in this preview record",
    sourceDocumentType: formatLabel(evidence.source_document_type),
    title: evidence.display_label,
    unavailableMessage: "This supporting evidence is metadata-only in the current preview."
  };
}

export function buildEvidenceUnavailablePreview(evidence: EvidenceLink, passport: PassportPreview): EvidencePreview {
  return {
    auditHandoff: {
      eventCode: "Unavailable in preview state",
      isAvailable: false,
      message: "Review history remains unavailable because this supporting evidence could not be opened."
    },
    confidenceContext: passport.confidenceSummary,
    evidenceId: evidence.evidence_id,
    openStatus: "Unavailable",
    passportId: passport.identity.passportId,
    provenanceRows: [
      { label: "Access level", value: formatLabel(evidence.access_level) },
      { label: "Supporting evidence status", value: "Unavailable" },
      { label: "Passport", value: passport.identity.passportId }
    ],
    sourceDocumentId: "Unavailable from current workspace",
    sourceDocumentType: formatLabel(evidence.source_document_type),
    title: evidence.display_label,
    unavailableMessage: "This supporting evidence cannot be opened from the current workspace."
  };
}

function fromEvidenceOpenContract(passport: PassportPreview): EvidencePreview {
  const summary = evidenceOpen.evidence_summary;

  return {
    auditHandoff: {
      eventCode: evidenceOpen.suggested_audit_event?.event_code ?? "Not present",
      isAvailable: Boolean(evidenceOpen.suggested_audit_event),
      message: "Review history is available for this supporting evidence."
    },
    confidenceContext: passport.confidenceSummary,
    evidenceId: evidenceOpen.evidence_id,
    openStatus: formatLabel(evidenceOpen.status),
    passportId: evidenceOpen.passport_id,
    provenanceRows: [
      { label: "Access level", value: formatLabel(summary.access_level) },
      { label: "Supporting evidence status", value: formatLabel(summary.status) },
      { label: "Future anchor", value: summary.has_future_anchor ? "Available" : "Not available" },
      { label: "Order", value: evidenceOpen.order_id },
      { label: "Tenant", value: evidenceOpen.tenant_id },
      { label: "User", value: evidenceOpen.user_id }
    ],
    sourceDocumentId: summary.source_document_id,
    sourceDocumentType: formatLabel(summary.source_document_type),
    title: summary.display_label,
    unavailableMessage: "This supporting evidence cannot open a source document from the current workspace."
  };
}
