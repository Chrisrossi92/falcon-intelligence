import { type TableRow } from "./mapWorkspaceData";
import { type PassportPreview } from "./passportData";

export type CorrectionAuditEventPreview = {
  actor: string;
  event: string;
  timestamp: string;
};

export type CorrectionAuditPreview = {
  actor: string;
  confidenceAfter: number;
  confidenceBefore: number;
  correctedValue: string;
  events: CorrectionAuditEventPreview[];
  fieldKey: string;
  fieldLabel: string;
  originalActor: string;
  originalValue: string;
  reason: string;
  reviewStatus: "Approved" | "Needs Review" | "Rejected";
  supportingEvidence: string;
  timestamp: string;
};

const correctionAudits: CorrectionAuditPreview[] = [
  {
    actor: "Chris",
    confidenceAfter: 88,
    confidenceBefore: 58,
    correctedValue: "4,800 SF",
    events: [
      {
        actor: "Chad",
        event: "Original comparable GBA entered as 4,200 SF.",
        timestamp: "2026-06-24T14:05:00+00:00"
      },
      {
        actor: "Chris",
        event: "Correction submitted based on auditor record.",
        timestamp: "2026-06-25T15:20:00+00:00"
      },
      {
        actor: "Chris",
        event: "Supporting Evidence added: Synthetic auditor property record card.",
        timestamp: "2026-06-25T15:24:00+00:00"
      },
      {
        actor: "Chris",
        event: "Correction approved; Current Value resolves to 4,800 SF.",
        timestamp: "2026-06-25T15:30:00+00:00"
      }
    ],
    fieldKey: "improvements.gba_sf",
    fieldLabel: "Gross Building Area",
    originalActor: "Chad",
    originalValue: "4,200 SF",
    reason: "based on auditor",
    reviewStatus: "Approved",
    supportingEvidence: "Synthetic auditor property record card",
    timestamp: "2026-06-25T15:30:00+00:00"
  }
];

const correctionAuditByPassportId: Record<string, CorrectionAuditPreview> = {
  "synthetic-passport-sale-industrial-1": correctionAudits[0]
};

const subjectProfileCorrection: CorrectionAuditPreview = {
  actor: "Chris",
  confidenceAfter: 82,
  confidenceBefore: 76,
  correctedValue: "50,000 SF",
  events: [
    {
      actor: "Chad",
      event: "Subject building area imported from synthetic intake notes.",
      timestamp: "2026-06-24T13:10:00+00:00"
    },
    {
      actor: "Chris",
      event: "Subject field reviewed against synthetic property card.",
      timestamp: "2026-06-25T14:45:00+00:00"
    }
  ],
  fieldKey: "improvements.gba_sf",
  fieldLabel: "Subject Gross Building Area",
  originalActor: "Chad",
  originalValue: "50,000 SF",
  reason: "confirmed against synthetic subject profile record",
  reviewStatus: "Needs Review",
  supportingEvidence: "Synthetic subject profile property card",
  timestamp: "2026-06-25T14:45:00+00:00"
};

export function buildCorrectionAuditPreview(
  row: TableRow,
  passport: PassportPreview | null
): CorrectionAuditPreview | null {
  if (passport?.identity.passportId && correctionAuditByPassportId[passport.identity.passportId]) {
    return correctionAuditByPassportId[passport.identity.passportId];
  }

  if (row.record_type === "current_subject") {
    return subjectProfileCorrection;
  }

  return null;
}
