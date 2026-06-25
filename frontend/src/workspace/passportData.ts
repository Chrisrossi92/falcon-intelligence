import dataPassportFixture from "../../../tests/fixtures/synthetic_data_passports/data-passports.json";
import passportDrawerSnapshot from "../../../tests/fixtures/synthetic_ui_passports/passport-detail-drawer-v1.json";
import verifiedIntelligenceFixture from "../../../tests/fixtures/synthetic_verified_intelligence/verified-intelligence.json";
import { formatLabel, type TableRow } from "./mapWorkspaceData";

export type EvidenceLink = {
  access_level: string;
  display_label: string;
  evidence_id: string;
  source_document_type: string;
  status: string;
  tenant_id?: string;
};

type PassportRecord = {
  audit_event_ids?: string[];
  confidence_dimensions?: Record<string, string>;
  confidence_summary?: string;
  display_label?: string;
  display_value?: string;
  fact_id?: string;
  fact_type?: string;
  passport_id: string;
  reviewed_at?: string | null;
  reviewed_by?: string | null;
  searchable_status?: string;
  tenant_id?: string;
  verified_at?: string | null;
  verified_by?: string | null;
  verification_status?: string;
  evidence_links?: EvidenceLink[];
};

type DrawerSnapshot = {
  audit_event_ids: string[];
  confidence_dimensions: Record<string, string>;
  evidence_links_summary: EvidenceLink[];
  fact_summary: {
    display_label: string;
    display_value: string;
    fact_type: string;
  };
  passport_identity: {
    assignment_id: string;
    fact_id: string;
    passport_id: string;
    tenant_id: string;
  };
  searchable_status: string;
  verification_review_summary: {
    reviewed_at: string;
    reviewed_by: string;
    verification_status: string;
    verified_at: string;
    verified_by: string;
  };
  warnings: Array<{
    code: string;
    message: string;
    severity: string;
  }>;
};

type VerifiedRecord = {
  address?: string;
  assignment_type?: string;
  building_size_sf?: number;
  city?: string;
  client?: string;
  effective_date?: string;
  id: string;
  passport?: {
    confidence_summary?: string;
    evidence_links?: EvidenceLink[];
    passport_id: string;
    searchable_status?: string;
  };
  property_type?: string;
  record_type?: string;
  state?: string;
  verification_status?: string;
};

type VerifiedIntelligenceFixture = {
  assignments?: VerifiedRecord[];
  lease_comps?: VerifiedRecord[];
  market_indicators?: VerifiedRecord[];
  sale_comps?: VerifiedRecord[];
};

export type PassportPreview = {
  auditEventIds: string[];
  confidenceDimensions: Record<string, string>;
  confidenceSummary: string;
  evidenceLinks: EvidenceLink[];
  factLabel: string;
  factType: string;
  factValue: string;
  identity: {
    assignmentId: string;
    factId: string;
    passportId: string;
    tenantId: string;
  };
  relatedContext: Array<{ label: string; value: string }>;
  review: {
    reviewedAt: string;
    reviewedBy: string;
    verificationStatus: string;
    verifiedAt: string;
    verifiedBy: string;
  };
  searchableStatus: string;
  warnings: string[];
};

const drawerSnapshot = passportDrawerSnapshot as DrawerSnapshot;
const dataPassports = dataPassportFixture as { passports: PassportRecord[] };
const verifiedIntelligence = verifiedIntelligenceFixture as VerifiedIntelligenceFixture;

export function buildPassportPreview(row: TableRow): PassportPreview | null {
  if (!row.passport_id) {
    return null;
  }

  if (row.passport_id === drawerSnapshot.passport_identity.passport_id) {
    return fromDrawerSnapshot(row);
  }

  const fullPassport = dataPassports.passports.find((passport) => passport.passport_id === row.passport_id);
  if (fullPassport) {
    return fromPassportRecord(row, fullPassport, findRelatedRecord(row.passport_id));
  }

  const relatedRecord = findRelatedRecord(row.passport_id);
  if (relatedRecord?.passport) {
    return fromVerifiedRecord(row, relatedRecord);
  }

  return null;
}

function fromDrawerSnapshot(row: TableRow): PassportPreview {
  return {
    auditEventIds: drawerSnapshot.audit_event_ids,
    confidenceDimensions: drawerSnapshot.confidence_dimensions,
    confidenceSummary: row.confidence_summary,
    evidenceLinks: drawerSnapshot.evidence_links_summary,
    factLabel: drawerSnapshot.fact_summary.display_label,
    factType: drawerSnapshot.fact_summary.fact_type,
    factValue: drawerSnapshot.fact_summary.display_value,
    identity: {
      assignmentId: drawerSnapshot.passport_identity.assignment_id,
      factId: drawerSnapshot.passport_identity.fact_id,
      passportId: drawerSnapshot.passport_identity.passport_id,
      tenantId: drawerSnapshot.passport_identity.tenant_id
    },
    relatedContext: buildRelatedContext(row, findRelatedRecord(row.passport_id)),
    review: {
      reviewedAt: drawerSnapshot.verification_review_summary.reviewed_at,
      reviewedBy: drawerSnapshot.verification_review_summary.reviewed_by,
      verificationStatus: drawerSnapshot.verification_review_summary.verification_status,
      verifiedAt: drawerSnapshot.verification_review_summary.verified_at,
      verifiedBy: drawerSnapshot.verification_review_summary.verified_by
    },
    searchableStatus: drawerSnapshot.searchable_status,
    warnings: drawerSnapshot.warnings.map((warning) => warning.message)
  };
}

function fromPassportRecord(
  row: TableRow,
  passport: PassportRecord,
  relatedRecord: VerifiedRecord | undefined
): PassportPreview {
  return {
    auditEventIds: passport.audit_event_ids ?? [],
    confidenceDimensions: passport.confidence_dimensions ?? {},
    confidenceSummary: row.confidence_summary,
    evidenceLinks: passport.evidence_links ?? [],
    factLabel: passport.display_label ?? row.display_label,
    factType: passport.fact_type ?? row.record_type,
    factValue: passport.display_value ?? row.confidence_summary,
    identity: {
      assignmentId: relatedRecord?.id ?? "Synthetic assignment context unavailable",
      factId: passport.fact_id ?? "Synthetic fact id unavailable",
      passportId: passport.passport_id,
      tenantId: passport.tenant_id ?? "Synthetic tenant unavailable"
    },
    relatedContext: buildRelatedContext(row, relatedRecord),
    review: {
      reviewedAt: passport.reviewed_at ?? "Not available in preview",
      reviewedBy: passport.reviewed_by ?? "Not available in preview",
      verificationStatus: passport.verification_status ?? row.verification_status,
      verifiedAt: passport.verified_at ?? "Not available in preview",
      verifiedBy: passport.verified_by ?? "Not available in preview"
    },
    searchableStatus: passport.searchable_status ?? "unknown",
    warnings: ["Synthetic passport detail only; no source document preview is available in this workspace."]
  };
}

function fromVerifiedRecord(row: TableRow, relatedRecord: VerifiedRecord): PassportPreview {
  const passport = relatedRecord.passport;

  return {
    auditEventIds: [],
    confidenceDimensions: {},
    confidenceSummary: passport?.confidence_summary ?? row.confidence_summary,
    evidenceLinks: passport?.evidence_links ?? [],
    factLabel: `${row.display_label} passport`,
    factType: relatedRecord.record_type ?? row.record_type,
    factValue: row.confidence_summary,
    identity: {
      assignmentId: relatedRecord.id,
      factId: "Not present in synthetic verified-intelligence contract",
      passportId: passport?.passport_id ?? row.passport_id ?? "Passport unavailable",
      tenantId: passport?.evidence_links?.[0]?.tenant_id ?? "Synthetic tenant unavailable"
    },
    relatedContext: buildRelatedContext(row, relatedRecord),
    review: {
      reviewedAt: "Not available in preview",
      reviewedBy: "Not available in preview",
      verificationStatus: relatedRecord.verification_status ?? row.verification_status,
      verifiedAt: "Not available in preview",
      verifiedBy: "Not available in preview"
    },
    searchableStatus: passport?.searchable_status ?? "unknown",
    warnings: ["Passport preview is derived from existing synthetic verified-intelligence records."]
  };
}

function findRelatedRecord(passportId: string | null): VerifiedRecord | undefined {
  if (!passportId) {
    return undefined;
  }

  return [
    ...(verifiedIntelligence.assignments ?? []),
    ...(verifiedIntelligence.sale_comps ?? []),
    ...(verifiedIntelligence.lease_comps ?? []),
    ...(verifiedIntelligence.market_indicators ?? [])
  ].find((record) => record.passport?.passport_id === passportId);
}

function buildRelatedContext(row: TableRow, relatedRecord: VerifiedRecord | undefined) {
  return [
    { label: "Selected property", value: `${row.address}, ${row.city}, ${row.state}` },
    { label: "Record type", value: formatLabel(row.record_type) },
    { label: "Property type", value: formatLabel(row.property_type) },
    { label: "Related assignment", value: relatedRecord?.id ?? "Not present in synthetic context" },
    {
      label: "Assignment context",
      value: relatedRecord?.assignment_type ?? relatedRecord?.record_type ?? row.record_type
    }
  ];
}
