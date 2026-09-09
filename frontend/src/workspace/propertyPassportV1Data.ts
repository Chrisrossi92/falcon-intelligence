import { type TableRow } from "./mapWorkspaceData";

export type PassportFactStatus = "verified" | "probable" | "conflicting" | "missing" | "needs_review";
export type PassportFactConfidence = "high" | "medium" | "low" | "missing" | "conflicting";

export type PassportEvidenceReference = {
  method: string;
  sourceHint: string;
  sourceLabel: string;
  sourceReference: string;
  sourceType: string;
};

export type PassportVerifiedFact = {
  confidence: PassportFactConfidence;
  evidence: PassportEvidenceReference[];
  fieldName: string;
  label: string;
  notes: string;
  status: PassportFactStatus;
  value: string;
};

export type KnowledgeObjectReadiness = "ready" | "probable" | "needs_review" | "blocked";

export type KnowledgeObjectPreview = {
  confidence: "high" | "medium" | "low";
  conflictingFields: string[];
  displayLabel: string;
  missingRequiredFields: string[];
  notes: string;
  objectType: "Property Object" | "Report Object" | "Client/User Object" | "Personnel Object" | "Open Issues";
  readiness: KnowledgeObjectReadiness;
  sourceFacts: string[];
};

export type MemoryGraphPreview = {
  graphReadiness: KnowledgeObjectReadiness;
  nodeCount: number;
  relationshipCount: number;
  relationshipChips: string[];
  summary: string;
  unresolvedWarnings: string[];
};

export type PropertyPassportV1Preview = {
  facts: PassportVerifiedFact[];
  identity: Array<{ label: string; value: string }>;
  knowledgeObjects: KnowledgeObjectPreview[];
  memoryGraph: MemoryGraphPreview;
  readiness: {
    detail: string;
    state: "ready" | "needs_review" | "blocked" | "missing_critical_fields";
    title: string;
  };
  summarySentences: string[];
};

const baseEvidence: PassportEvidenceReference[] = [
  {
    method: "Agreement rule",
    sourceHint: "page 1",
    sourceLabel: "Synthetic report cover metadata",
    sourceReference: "synthetic-final-report:cover",
    sourceType: "extracted_metadata"
  },
  {
    method: "Deterministic filename phrase",
    sourceHint: "filename",
    sourceLabel: "Synthetic final report filename",
    sourceReference: "synthetic-final-report:filename",
    sourceType: "filename"
  }
];

const reviewEvidence: PassportEvidenceReference[] = [
  {
    method: "Missing rule",
    sourceHint: "verification ledger",
    sourceLabel: "Synthetic verification ledger",
    sourceReference: "synthetic-verification:reviewer_name",
    sourceType: "verification_ledger"
  }
];

const conflictEvidence: PassportEvidenceReference[] = [
  {
    method: "Conflict rule",
    sourceHint: "page 1",
    sourceLabel: "Synthetic report cover metadata",
    sourceReference: "synthetic-final-report:intended_user:1",
    sourceType: "extracted_metadata"
  },
  {
    method: "Conflict rule",
    sourceHint: "page 2",
    sourceLabel: "Synthetic certification metadata",
    sourceReference: "synthetic-final-report:intended_user:2",
    sourceType: "extracted_metadata"
  }
];

const defaultFacts: PassportVerifiedFact[] = [
  {
    confidence: "high",
    evidence: baseEvidence,
    fieldName: "property_address",
    label: "Property address",
    notes: "Verified by agreement between extracted cover metadata and filename context.",
    status: "verified",
    value: "100 Sample Industrial Avenue"
  },
  {
    confidence: "high",
    evidence: baseEvidence,
    fieldName: "report_type",
    label: "Report type",
    notes: "Verified by agreement between report title and filename.",
    status: "verified",
    value: "Restricted appraisal report"
  },
  {
    confidence: "medium",
    evidence: [baseEvidence[0]],
    fieldName: "client",
    label: "Client",
    notes: "Single-source candidate is available and remains probable until another source agrees.",
    status: "probable",
    value: "Example Bank"
  },
  {
    confidence: "conflicting",
    evidence: conflictEvidence,
    fieldName: "intended_user",
    label: "Intended user",
    notes: "Two candidate values disagree. Falcon does not choose between them in this preview.",
    status: "conflicting",
    value: "Conflicting candidates"
  },
  {
    confidence: "high",
    evidence: baseEvidence,
    fieldName: "effective_date",
    label: "Effective date",
    notes: "Verified by deterministic label and cover metadata agreement.",
    status: "verified",
    value: "June 1, 2026"
  },
  {
    confidence: "high",
    evidence: baseEvidence,
    fieldName: "appraiser_name",
    label: "Appraiser",
    notes: "Verified by synthetic certification metadata in this preview.",
    status: "verified",
    value: "Synthetic appraiser"
  },
  {
    confidence: "missing",
    evidence: reviewEvidence,
    fieldName: "reviewer_name",
    label: "Reviewer",
    notes: "No reviewer candidate was present. Falcon did not fabricate one.",
    status: "missing",
    value: "Missing"
  },
  {
    confidence: "low",
    evidence: [reviewEvidence[0]],
    fieldName: "inspection_date",
    label: "Inspection date",
    notes: "One candidate needs human review before promotion.",
    status: "needs_review",
    value: "Needs review"
  }
];

const factsByRowId: Record<string, PassportVerifiedFact[]> = {
  "synthetic-map-airport-warehouse-001": [
    {
      ...defaultFacts[0],
      value: "1750 Example Airport Cargo Road"
    },
    {
      ...defaultFacts[1],
      value: "Appraisal report"
    },
    {
      ...defaultFacts[2],
      value: "Example Logistics Bank"
    },
    defaultFacts[3],
    defaultFacts[4],
    defaultFacts[5],
    defaultFacts[6],
    defaultFacts[7]
  ],
  "synthetic-map-current-subject-001": defaultFacts
};

export function buildPropertyPassportV1Preview(row: TableRow): PropertyPassportV1Preview {
  const facts = factsByRowId[row.id] ?? buildFallbackFacts(row);
  const counts = countFactStatuses(facts);
  const hasConflict = counts.conflicting > 0;
  const missingCritical = facts.some(
    (fact) => ["property_address", "report_type", "effective_date"].includes(fact.fieldName) && fact.status === "missing"
  );
  const readiness = hasConflict
    ? {
        detail: "Resolve conflicting verified fact candidates before creating Knowledge Objects.",
        state: "blocked" as const,
        title: "Blocked by conflicts"
      }
    : missingCritical
      ? {
          detail: "Critical identity fields are missing and must be verified first.",
          state: "missing_critical_fields" as const,
          title: "Missing critical fields"
        }
      : counts.needs_review > 0 || counts.missing > 0
        ? {
            detail: "Core identity is usable, but the record still has review work before promotion.",
            state: "needs_review" as const,
            title: "Needs review before knowledge creation"
          }
        : {
            detail: "Verified facts are sufficient for a future Knowledge Object creation workflow.",
            state: "ready" as const,
            title: "Ready for knowledge object creation"
          };

  const knowledgeObjects = buildKnowledgeObjectPreview(facts);

  return {
    facts,
    identity: [
      { label: "Property address", value: valueFor(facts, "property_address", `${row.address}, ${row.city}, ${row.state}`) },
      { label: "Property type", value: valueFor(facts, "property_type", row.property_type) },
      { label: "Report type", value: valueFor(facts, "report_type", row.record_type) },
      { label: "Client", value: valueFor(facts, "client", "Missing") },
      { label: "Intended user", value: valueFor(facts, "intended_user", "Needs review") },
      { label: "Intended use", value: valueFor(facts, "intended_use", "Preview assignment context") },
      { label: "Appraiser", value: valueFor(facts, "appraiser_name", "Synthetic appraiser") },
      { label: "Reviewer", value: valueFor(facts, "reviewer_name", "Missing") },
      { label: "Effective date", value: valueFor(facts, "effective_date", "Missing") },
      { label: "Report date", value: valueFor(facts, "report_date", "Missing") },
      { label: "Inspection date", value: valueFor(facts, "inspection_date", "Needs review") }
    ],
    knowledgeObjects,
    memoryGraph: buildMemoryGraphPreview(knowledgeObjects),
    readiness,
    summarySentences: [
      `Falcon has verified ${counts.verified} fact${counts.verified === 1 ? "" : "s"} for this property record.`,
      counts.probable > 0 ? `Falcon has ${counts.probable} probable fact${counts.probable === 1 ? "" : "s"} waiting for stronger support.` : "Falcon has no probable facts in this preview.",
      counts.conflicting > 0 ? "Falcon found a conflict in the intended user field." : "Falcon found no conflicting fields in this preview.",
      counts.missing > 0 ? "Falcon is missing reviewer information." : "Falcon has no missing fields in this preview.",
      readiness.title === "Ready for knowledge object creation"
        ? "This record is ready for future Knowledge Object creation."
        : readiness.detail
    ]
  };
}

export function countFactStatuses(facts: PassportVerifiedFact[]) {
  return facts.reduce(
    (counts, fact) => ({ ...counts, [fact.status]: counts[fact.status] + 1 }),
    {
      conflicting: 0,
      missing: 0,
      needs_review: 0,
      probable: 0,
      verified: 0
    } satisfies Record<PassportFactStatus, number>
  );
}

function buildFallbackFacts(row: TableRow): PassportVerifiedFact[] {
  const address = `${row.address}, ${row.city}, ${row.state}`;

  return [
    {
      confidence: row.verification_status === "verified" ? "high" : "medium",
      evidence: baseEvidence,
      fieldName: "property_address",
      label: "Property address",
      notes: "Synthetic workspace row and Passport context agree on the address.",
      status: row.verification_status === "verified" ? "verified" : "probable",
      value: address
    },
    {
      confidence: row.verification_status === "verified" ? "high" : "medium",
      evidence: [baseEvidence[0]],
      fieldName: "property_type",
      label: "Property type",
      notes: "Synthetic workspace classification is available for preview only.",
      status: row.verification_status === "verified" ? "verified" : "probable",
      value: row.property_type
    },
    {
      confidence: "missing",
      evidence: reviewEvidence,
      fieldName: "reviewer_name",
      label: "Reviewer",
      notes: "Reviewer metadata is not available in this synthetic record.",
      status: "missing",
      value: "Missing"
    }
  ];
}

function valueFor(facts: PassportVerifiedFact[], fieldName: string, fallback: string) {
  return facts.find((fact) => fact.fieldName === fieldName)?.value ?? fallback;
}

function buildKnowledgeObjectPreview(facts: PassportVerifiedFact[]): KnowledgeObjectPreview[] {
  const address = factFor(facts, "property_address");
  const reportType = factFor(facts, "report_type");
  const effectiveDate = factFor(facts, "effective_date");
  const client = factFor(facts, "client");
  const intendedUser = factFor(facts, "intended_user");
  const appraiser = factFor(facts, "appraiser_name");
  const reviewer = factFor(facts, "reviewer_name");
  const issueFacts = facts.filter((fact) => ["conflicting", "missing", "needs_review"].includes(fact.status));

  return [
    {
      confidence: statusIsUsable(address?.status) ? "high" : "low",
      conflictingFields: fieldNames([address], "conflicting"),
      displayLabel: address?.value ?? "Property object needs address review",
      missingRequiredFields: requiredMissing([address]),
      notes: "Property identity can be promoted when the address is verified or probable and not conflicting.",
      objectType: "Property Object",
      readiness: address?.status === "conflicting" ? "blocked" : statusIsUsable(address?.status) ? "ready" : "needs_review",
      sourceFacts: fieldNames([address])
    },
    {
      confidence: statusIsUsable(reportType?.status) && statusIsUsable(effectiveDate?.status) ? "high" : "low",
      conflictingFields: fieldNames([reportType, effectiveDate], "conflicting"),
      displayLabel: `${reportType?.value ?? "Report"} object`,
      missingRequiredFields: requiredMissing([reportType, effectiveDate]),
      notes: "Report identity depends on report type and effective date before later insight work relies on it.",
      objectType: "Report Object",
      readiness: fieldNames([reportType, effectiveDate], "conflicting").length
        ? "blocked"
        : statusIsUsable(reportType?.status) && statusIsUsable(effectiveDate?.status)
          ? "ready"
          : "needs_review",
      sourceFacts: fieldNames([reportType, effectiveDate])
    },
    {
      confidence: statusIsUsable(client?.status) && statusIsUsable(intendedUser?.status) ? "medium" : "low",
      conflictingFields: fieldNames([client, intendedUser], "conflicting"),
      displayLabel: client?.value ?? "Client/User object needs review",
      missingRequiredFields: requiredMissing([client, intendedUser]),
      notes: "Client and intended-user disagreements stay reviewable until an operator resolves them.",
      objectType: "Client/User Object",
      readiness: statusIsUsable(client?.status) && statusIsUsable(intendedUser?.status) ? "ready" : "needs_review",
      sourceFacts: fieldNames([client, intendedUser])
    },
    {
      confidence: statusIsUsable(appraiser?.status) ? "medium" : "low",
      conflictingFields: fieldNames([appraiser, reviewer], "conflicting"),
      displayLabel: appraiser?.value ?? "Personnel object needs review",
      missingRequiredFields: requiredMissing([appraiser, reviewer]),
      notes: "Personnel remains probable when appraiser is known but reviewer metadata is missing.",
      objectType: "Personnel Object",
      readiness: fieldNames([appraiser, reviewer], "conflicting").length
        ? "blocked"
        : statusIsUsable(appraiser?.status) && !statusIsUsable(reviewer?.status)
          ? "probable"
          : statusIsUsable(appraiser?.status) && statusIsUsable(reviewer?.status)
            ? "ready"
            : "needs_review",
      sourceFacts: fieldNames([appraiser, reviewer])
    },
    {
      confidence: issueFacts.length ? "low" : "high",
      conflictingFields: issueFacts.filter((fact) => fact.status === "conflicting").map((fact) => fact.label),
      displayLabel: "Review queue",
      missingRequiredFields: issueFacts.filter((fact) => fact.status === "missing").map((fact) => fact.label),
      notes: issueFacts.length
        ? "Open issues preserve the fields that must be reviewed before durable knowledge promotion."
        : "No open issues were surfaced by this synthetic preview.",
      objectType: "Open Issues",
      readiness: issueFacts.some((fact) => fact.status === "conflicting") ? "blocked" : issueFacts.length ? "needs_review" : "ready",
      sourceFacts: issueFacts.map((fact) => fact.label)
    }
  ];
}

function factFor(facts: PassportVerifiedFact[], fieldName: string) {
  return facts.find((fact) => fact.fieldName === fieldName);
}

function statusIsUsable(status: PassportFactStatus | undefined) {
  return status === "verified" || status === "probable";
}

function fieldNames(facts: Array<PassportVerifiedFact | undefined>, status?: PassportFactStatus) {
  return facts.filter((fact): fact is PassportVerifiedFact => Boolean(fact) && (!status || fact.status === status)).map((fact) => fact.label);
}

function requiredMissing(facts: Array<PassportVerifiedFact | undefined>) {
  return facts.filter((fact) => !fact || !statusIsUsable(fact.status)).map((fact) => fact?.label ?? "Required fact");
}

function buildMemoryGraphPreview(objects: KnowledgeObjectPreview[]): MemoryGraphPreview {
  const graphReadiness = calculateGraphReadiness(objects);
  const objectByType = new Map(objects.map((object) => [object.objectType, object]));
  const chips = ["PROPERTY_HAS_REPORT", "PROPERTY_HAS_VERIFIED_IDENTITY", "REPORT_SUPPORTS_PROPERTY_PASSPORT"];
  if (objectByType.has("Client/User Object")) {
    chips.push("REPORT_FOR_CLIENT");
  }
  if (objectByType.get("Client/User Object")?.readiness === "ready") {
    chips.push("REPORT_HAS_INTENDED_USER");
  }
  if (objectByType.get("Personnel Object")?.sourceFacts.includes("Appraiser")) {
    chips.push("REPORT_PREPARED_BY_APPRAISER");
  }
  if (objectByType.get("Personnel Object")?.sourceFacts.includes("Reviewer")) {
    chips.push("REPORT_REVIEWED_BY_REVIEWER");
  }
  if (objectByType.get("Open Issues")?.readiness !== "ready") {
    chips.push("REPORT_HAS_OPEN_ISSUE");
  }

  const unresolvedWarnings = objects
    .filter((object) => object.readiness === "blocked" || object.readiness === "needs_review")
    .map((object) => `${object.objectType}: ${object.missingRequiredFields.length} missing, ${object.conflictingFields.length} conflicts`);

  return {
    graphReadiness,
    nodeCount: objects.length,
    relationshipCount: chips.length,
    relationshipChips: chips,
    summary: `This property memory connects ${objects.length} local object candidates through ${chips.length} deterministic relationship${chips.length === 1 ? "" : "s"}.`,
    unresolvedWarnings
  };
}

function calculateGraphReadiness(objects: KnowledgeObjectPreview[]): KnowledgeObjectReadiness {
  const readiness = new Set(objects.map((object) => object.readiness));
  if (readiness.has("blocked")) {
    return "blocked";
  }
  if (readiness.has("needs_review")) {
    return "needs_review";
  }
  if (readiness.has("probable")) {
    return "probable";
  }
  return "ready";
}
