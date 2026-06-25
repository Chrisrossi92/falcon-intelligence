import cardViewedAuditEvent from "../../../tests/fixtures/synthetic_audit_events/card-viewed-audit-event-v1.json";
import evidenceOpenedAuditEvent from "../../../tests/fixtures/synthetic_audit_events/evidence-opened-audit-event-v1.json";
import historicalCompAuditEvent from "../../../tests/fixtures/synthetic_audit_events/historical-comp-justification-audit-event-v1.json";
import passportDetailAuditEvent from "../../../tests/fixtures/synthetic_audit_events/passport-detail-opened-audit-event-v1.json";
import { formatLabel } from "./mapWorkspaceData";
import type { EvidencePreview } from "./evidenceData";

type AuditEvent = {
  event_code: string;
  match_id?: string;
  metadata?: Record<string, string | number>;
  order_id: string;
  tenant_id: string;
  timestamp: string;
  user_id: string;
};

export type AuditTimelineEvent = {
  actor: string;
  eventCode: string;
  matchId: string;
  summary: string;
  timestamp: string;
  verificationStatus: string;
};

export type AuditPreview = {
  contextRows: Array<{ label: string; value: string }>;
  events: AuditTimelineEvent[];
  message: string;
  title: string;
};

const auditEvents = [
  cardViewedAuditEvent,
  evidenceOpenedAuditEvent,
  historicalCompAuditEvent,
  passportDetailAuditEvent
] as AuditEvent[];

export function buildAuditPreview(evidence: EvidencePreview): AuditPreview {
  const matchingEvents = auditEvents.filter((event) => eventMatchesEvidence(event, evidence));

  return {
    contextRows: [
      { label: "Supporting evidence", value: evidence.evidenceId },
      { label: "Passport", value: evidence.passportId },
      { label: "Source/report", value: evidence.sourceDocumentId },
      { label: "Review handoff", value: evidence.auditHandoff.eventCode }
    ],
    events: matchingEvents
      .map((event) => toTimelineEvent(event))
      .sort((first, second) => Date.parse(first.timestamp) - Date.parse(second.timestamp)),
    message:
      matchingEvents.length > 0
        ? "Review events are shown from committed synthetic snapshots. Production persistence is not enabled."
        : "No matching review event exists for this supporting evidence in the current preview.",
    title: `Review history for ${evidence.title}`
  };
}

export function buildAuditUnavailablePreview(evidence: EvidencePreview): AuditPreview {
  return {
    contextRows: [
      { label: "Supporting evidence", value: evidence.evidenceId },
      { label: "Passport", value: evidence.passportId },
      { label: "Source/report", value: evidence.sourceDocumentId },
      { label: "Reason", value: "Synthetic limitation" }
    ],
    events: [],
    message: "Review history is not available in the current preview.",
    title: `Review history for ${evidence.title}`
  };
}

function eventMatchesEvidence(event: AuditEvent, evidence: EvidencePreview) {
  const metadata = event.metadata ?? {};

  return (
    event.match_id === evidence.passportId ||
    metadata.passport_id === evidence.passportId ||
    metadata.evidence_id === evidence.evidenceId
  );
}

function toTimelineEvent(event: AuditEvent): AuditTimelineEvent {
  const metadata = event.metadata ?? {};

  return {
    actor: event.user_id,
    eventCode: formatLabel(event.event_code),
    matchId: event.match_id ?? String(metadata.passport_id ?? metadata.selected_passport_id ?? "Not present"),
    summary: buildSummary(event),
    timestamp: event.timestamp,
    verificationStatus: formatLabel(String(metadata.status ?? metadata.searchable_status ?? "metadata_only"))
  };
}

function buildSummary(event: AuditEvent) {
  const metadata = event.metadata ?? {};

  if (metadata.detail_type === "evidence_link") {
    return `Supporting evidence opened for ${metadata.evidence_id}.`;
  }

  if (metadata.detail_type === "data_passport") {
    return `Passport opened with ${metadata.evidence_link_count} supporting evidence item.`;
  }

  if (metadata.audit_reason === "wrote_justification") {
    return String(metadata.justification);
  }

  if (metadata.selected_passport_id) {
    return `Firm intelligence card viewed for passport ${metadata.selected_passport_id}.`;
  }

  return "Preview review event recorded.";
}
