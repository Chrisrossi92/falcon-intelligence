import { type TableRow } from "./mapWorkspaceData";
import { type PassportPreview } from "./passportData";

export type TrustState = "high" | "needs_verification" | "conflicting" | "stale";

export type InsightEvidencePreview = {
  evidenceType: string;
  relationship: string;
  sourceLabel: string;
};

export type InsightRelationshipChain = {
  fact: string;
  knowledge: string;
  insight: string;
  recommendation: string;
};

export type InsightPreview = {
  confidenceState: TrustState;
  evidence: InsightEvidencePreview[];
  explanation: string;
  freshnessCue: string;
  id: string;
  relatedFacts: string[];
  relationshipChain: InsightRelationshipChain;
  recommendation: string;
  title: string;
  verificationCue: string;
};

type InsightSeed = Omit<InsightPreview, "evidence"> & {
  evidence?: InsightEvidencePreview[];
};

const defaultEvidence: InsightEvidencePreview[] = [
  {
    evidenceType: "Source metadata",
    relationship: "Supports the selected Passport and verified fact summary.",
    sourceLabel: "Synthetic source report metadata"
  }
];

const insightSeedsByRowId: Record<string, InsightSeed[]> = {
  "synthetic-map-current-subject-001": [
    {
      id: "subject-cost-approach-stability",
      title: "Physical profile supports a conservative cost review",
      explanation:
        "The selected subject has verified building profile context, so cost approach changes should be checked against the existing physical facts.",
      relatedFacts: ["Industrial property", "Verified subject Passport", "Building profile evidence available"],
      confidenceState: "high",
      freshnessCue: "Current order context",
      verificationCue: "Verified knowledge",
      recommendation: "Review cost approach assumptions before changing depreciation.",
      relationshipChain: {
        fact: "Verified industrial subject profile",
        knowledge: "Property profile is available for the active order",
        insight: "Physical assumptions can be checked before cost approach edits",
        recommendation: "Review cost approach assumptions before changing depreciation"
      }
    },
    {
      id: "subject-evidence-route",
      title: "Supporting evidence is ready for review",
      explanation:
        "The Passport has a metadata-backed evidence link, giving the operator a clear path from selected property to source context.",
      relatedFacts: ["1 supporting evidence item", "Passport available", "Review history available"],
      confidenceState: "high",
      freshnessCue: "Evidence available",
      verificationCue: "Review path available",
      recommendation: "Open the Passport before relying on the subject profile.",
      relationshipChain: {
        fact: "Passport has one evidence link",
        knowledge: "Source metadata supports the selected knowledge record",
        insight: "The trust chain can be reviewed without opening source documents",
        recommendation: "Open the Passport before relying on the subject profile"
      }
    },
    {
      id: "subject-market-context",
      title: "Nearby industrial records may provide context",
      explanation:
        "The workspace contains nearby verified industrial assignments and comps that can orient the appraiser before deeper analysis.",
      relatedFacts: ["Industrial workspace context", "Nearby verified records", "Synthetic map relationship"],
      confidenceState: "needs_verification",
      freshnessCue: "Preview-only relationship",
      verificationCue: "Needs appraisal review",
      recommendation: "Compare nearby industrial records only after checking their evidence and dates.",
      relationshipChain: {
        fact: "Nearby industrial records appear in the workspace",
        knowledge: "The firm has related industrial knowledge in the same synthetic market",
        insight: "Prior work may help orient the current assignment",
        recommendation: "Compare nearby records only after checking their evidence and dates"
      }
    }
  ],
  "synthetic-map-airport-warehouse-001": [
    {
      id: "airport-depreciation-stability",
      title: "Physical profile appears stable enough for depreciation review",
      explanation:
        "The verified building-area record and source metadata suggest the property profile can anchor a careful depreciation check.",
      relatedFacts: ["50,000 sf building area", "Industrial warehouse use", "Verified source metadata"],
      confidenceState: "high",
      freshnessCue: "Verified source metadata",
      verificationCue: "Verified knowledge",
      recommendation: "Review cost approach before altering depreciation assumptions.",
      relationshipChain: {
        fact: "Building profile is verified in the synthetic Passport",
        knowledge: "Industrial warehouse physical profile is available for review",
        insight: "Depreciation changes should be tested against stable physical assumptions",
        recommendation: "Review cost approach before altering depreciation assumptions"
      },
      evidence: [
        {
          evidenceType: "Source report metadata",
          relationship: "Supports the verified building profile used by the insight.",
          sourceLabel: "Synthetic industrial assignment source metadata"
        },
        {
          evidenceType: "Review history",
          relationship: "Shows the preview path for accountability review.",
          sourceLabel: "Synthetic Passport opened event"
        }
      ]
    },
    {
      id: "airport-income-check",
      title: "Income assumptions should be checked against occupancy context",
      explanation:
        "The selected warehouse has industrial context but no live rent roll in this preview, so income changes should be treated as review work.",
      relatedFacts: ["Industrial warehouse", "Income support not opened", "Evidence remains metadata-only"],
      confidenceState: "needs_verification",
      freshnessCue: "Income source unavailable in preview",
      verificationCue: "Needs verification",
      recommendation: "Review rent roll before updating income assumptions.",
      relationshipChain: {
        fact: "Warehouse use is visible, but rent roll detail is not available",
        knowledge: "Income support is incomplete in the preview layer",
        insight: "Income assumptions should not be updated from workspace context alone",
        recommendation: "Review rent roll before updating income assumptions"
      }
    },
    {
      id: "airport-zoning-narrative",
      title: "Prior location narrative should not stand in for zoning confirmation",
      explanation:
        "Airport-district context may be useful, but zoning is not verified as a standalone knowledge object in this preview.",
      relatedFacts: ["Airport District", "Prior report context", "No zoning Passport shown"],
      confidenceState: "needs_verification",
      freshnessCue: "Zoning freshness unknown",
      verificationCue: "Needs verification",
      recommendation: "Confirm zoning before relying on prior narrative.",
      relationshipChain: {
        fact: "Airport District location is visible",
        knowledge: "Location context exists without a verified zoning object",
        insight: "Prior narrative may not be enough for zoning reliance",
        recommendation: "Confirm zoning before relying on prior narrative"
      }
    },
    {
      id: "airport-evidence-boundary",
      title: "Evidence is strong enough to review, not to automate",
      explanation:
        "The preview shows a traceable evidence path, but it intentionally stops before source-document content or automated conclusions.",
      relatedFacts: ["1 supporting evidence item", "Review history available", "No source preview"],
      confidenceState: "high",
      freshnessCue: "Evidence path available",
      verificationCue: "Synthetic review history",
      recommendation: "Open supporting evidence to confirm why the knowledge is trusted.",
      relationshipChain: {
        fact: "Supporting evidence exists for the selected Passport",
        knowledge: "The selected property has a reviewable trust chain",
        insight: "The operator can inspect trust before acting",
        recommendation: "Open supporting evidence to confirm why the knowledge is trusted"
      }
    }
  ],
  "synthetic-map-historical-comp-001": [
    {
      id: "historical-comp-stale",
      title: "Historical comparable needs freshness review",
      explanation:
        "The office sale comp is retained as historical knowledge, but the stale flag means reuse should require date and market context review.",
      relatedFacts: ["Historical comp", "Stale flag", "Verified status"],
      confidenceState: "stale",
      freshnessCue: "Stale evidence",
      verificationCue: "Verified but stale",
      recommendation: "Reuse prior comparable only after checking sale date and freshness.",
      relationshipChain: {
        fact: "Historical office sale comp is marked stale",
        knowledge: "The comp remains firm knowledge but is not current by default",
        insight: "Reuse may be risky without updated market context",
        recommendation: "Reuse prior comparable only after checking sale date and freshness"
      }
    },
    {
      id: "historical-comp-market-shift",
      title: "Market context may have shifted",
      explanation:
        "Historical records can orient the reviewer, but stale market evidence should not be treated as current support.",
      relatedFacts: ["Historical status", "Office property type", "Prior evidence available"],
      confidenceState: "stale",
      freshnessCue: "Historical record",
      verificationCue: "Needs reverification for reuse",
      recommendation: "Request updated market support before using this comp in analysis.",
      relationshipChain: {
        fact: "Office comp is historical",
        knowledge: "Prior comparable knowledge exists in the firm record",
        insight: "Market relevance may have changed",
        recommendation: "Request updated market support before using this comp in analysis"
      }
    },
    {
      id: "historical-comp-evidence",
      title: "Evidence supports history, not current reliance",
      explanation:
        "The evidence path can explain why the record exists, but it does not make the older transaction current.",
      relatedFacts: ["Evidence link available", "Historical status", "Stale flag"],
      confidenceState: "conflicting",
      freshnessCue: "Evidence age conflict",
      verificationCue: "Requires reviewer judgment",
      recommendation: "Document why the historical comp remains relevant before reuse.",
      relationshipChain: {
        fact: "Evidence exists for a stale record",
        knowledge: "The firm has prior support for the comp",
        insight: "Source support and current relevance are separate trust questions",
        recommendation: "Document why the historical comp remains relevant before reuse"
      }
    }
  ],
  "synthetic-map-lease-comp-001": [
    {
      id: "lease-rent-roll-check",
      title: "Lease evidence should drive income updates",
      explanation:
        "The lease comp is verified, but income assumptions should still be checked against lease support before reuse.",
      relatedFacts: ["Verified lease comp", "Lease-support metadata", "Industrial property type"],
      confidenceState: "high",
      freshnessCue: "Verified lease support",
      verificationCue: "Verified knowledge",
      recommendation: "Review rent roll before updating income assumptions.",
      relationshipChain: {
        fact: "Verified industrial lease comp is available",
        knowledge: "Lease knowledge can support income review",
        insight: "Income updates should trace back to lease support",
        recommendation: "Review rent roll before updating income assumptions"
      }
    },
    {
      id: "lease-terms-review",
      title: "Lease terms need context before comparison",
      explanation:
        "The preview shows lease knowledge, but expense structure and concessions remain professional review items.",
      relatedFacts: ["Lease comp", "Verified status", "Supporting evidence count"],
      confidenceState: "needs_verification",
      freshnessCue: "Terms require review",
      verificationCue: "Needs appraiser review",
      recommendation: "Check concessions and expense basis before comparing rent.",
      relationshipChain: {
        fact: "Lease comparable is verified",
        knowledge: "Rent evidence exists for the industrial context",
        insight: "Lease economics may not be directly comparable without terms",
        recommendation: "Check concessions and expense basis before comparing rent"
      }
    },
    {
      id: "lease-evidence-route",
      title: "Evidence route is available before reuse",
      explanation:
        "The operator can inspect supporting evidence before deciding whether the lease comp belongs in the current analysis.",
      relatedFacts: ["Evidence link available", "Passport available", "Verified lease record"],
      confidenceState: "high",
      freshnessCue: "Evidence available",
      verificationCue: "Verified knowledge",
      recommendation: "Open supporting evidence before reusing the lease comparable.",
      relationshipChain: {
        fact: "Lease comp has supporting evidence",
        knowledge: "Evidence-backed lease knowledge is available",
        insight: "Reuse can begin with a traceable review path",
        recommendation: "Open supporting evidence before reusing the lease comparable"
      }
    }
  ],
  "synthetic-map-sale-comp-001": [
    {
      id: "sale-date-freshness",
      title: "Sale comparable is usable only after date review",
      explanation:
        "The sale comp is verified in the preview, but transaction timing still controls whether it is appropriate for the current assignment.",
      relatedFacts: ["Verified sale comp", "Comparable-support metadata", "Synthetic sale record"],
      confidenceState: "high",
      freshnessCue: "Sale date should be checked",
      verificationCue: "Verified knowledge",
      recommendation: "Reuse prior comparable only after checking sale date and freshness.",
      relationshipChain: {
        fact: "Verified industrial sale comp exists",
        knowledge: "The firm has reusable sale comparable knowledge",
        insight: "Freshness controls whether the comp is appropriate now",
        recommendation: "Reuse prior comparable only after checking sale date and freshness"
      }
    },
    {
      id: "sale-adjustment-check",
      title: "Adjustment logic should stay tied to evidence",
      explanation:
        "A verified comp can help the appraiser, but adjustments should be reviewed against property differences and evidence.",
      relatedFacts: ["Verified comparable", "Supporting evidence", "Industrial property context"],
      confidenceState: "needs_verification",
      freshnessCue: "Adjustment context not verified in preview",
      verificationCue: "Needs appraiser judgment",
      recommendation: "Review adjustment rationale before reusing the comp.",
      relationshipChain: {
        fact: "Comparable support exists",
        knowledge: "Sale comp is part of firm intelligence",
        insight: "Adjustment reuse requires professional context",
        recommendation: "Review adjustment rationale before reusing the comp"
      }
    },
    {
      id: "sale-evidence-confidence",
      title: "Evidence-backed comparable is ready for inspection",
      explanation:
        "The preview can explain why the comparable surfaced by connecting the comp, Passport, evidence, and review path.",
      relatedFacts: ["Passport available", "1 evidence item", "Verified status"],
      confidenceState: "high",
      freshnessCue: "Evidence path available",
      verificationCue: "Verified knowledge",
      recommendation: "Open supporting evidence before selecting the comparable.",
      relationshipChain: {
        fact: "Verified comp has one evidence item",
        knowledge: "The comp has a traceable Passport",
        insight: "Trust can be inspected before selection",
        recommendation: "Open supporting evidence before selecting the comparable"
      }
    }
  ]
};

export function buildInsightPreview(row: TableRow, passport: PassportPreview | null): InsightPreview[] {
  const seeds = insightSeedsByRowId[row.id] ?? buildFallbackSeeds(row, passport);

  return seeds.map((seed) => ({
    ...seed,
    evidence: seed.evidence ?? buildEvidencePreviewRows(row, passport)
  }));
}

function buildFallbackSeeds(row: TableRow, passport: PassportPreview | null): InsightSeed[] {
  const hasPassport = Boolean(passport);
  const hasEvidence = (passport?.evidenceLinks.length ?? row.evidence_link_count) > 0;
  const confidenceState: TrustState = row.stale_flag
    ? "stale"
    : row.verification_status === "verified"
      ? "high"
      : "needs_verification";

  return [
    {
      id: `${row.id}-verification-route`,
      title: hasPassport ? "Knowledge record has a review path" : "Knowledge needs verification before use",
      explanation: hasPassport
        ? "The selected record can be reviewed through its Passport, evidence metadata, and review context."
        : "The selected record is visible for workspace context but is not presented as verified firm knowledge.",
      relatedFacts: [row.display_label, row.record_type, row.verification_status],
      confidenceState,
      freshnessCue: row.stale_flag ? "Stale evidence" : "Freshness not flagged",
      verificationCue: hasPassport ? "Passport available" : "Needs verification",
      recommendation: hasPassport
        ? "Open the Passport before relying on this knowledge."
        : "Verify facts before using this record for appraisal work.",
      relationshipChain: {
        fact: `${row.display_label} appears in the synthetic workspace`,
        knowledge: hasPassport ? "Passport-backed knowledge is available" : "Knowledge is not verified for reuse",
        insight: hasPassport ? "The trust chain can be inspected" : "The record should remain context only",
        recommendation: hasPassport
          ? "Open the Passport before relying on this knowledge"
          : "Verify facts before using this record for appraisal work"
      }
    },
    {
      id: `${row.id}-evidence-route`,
      title: hasEvidence ? "Supporting evidence can be inspected" : "Supporting evidence is not available",
      explanation: hasEvidence
        ? "Evidence metadata is available to explain why the selected knowledge exists."
        : "No evidence metadata is available in the preview, so confidence should remain limited.",
      relatedFacts: [`${row.evidence_link_count} evidence item(s)`, row.property_type, row.status],
      confidenceState: hasEvidence ? confidenceState : "needs_verification",
      freshnessCue: hasEvidence ? "Evidence path available" : "Evidence unavailable",
      verificationCue: row.verification_status === "verified" ? "Verified record" : "Unverified record",
      recommendation: hasEvidence
        ? "Open supporting evidence before taking the next workflow step."
        : "Attach or verify supporting evidence before reuse.",
      relationshipChain: {
        fact: hasEvidence ? "Evidence metadata exists" : "Evidence metadata is absent",
        knowledge: hasEvidence ? "The selected record has support context" : "The record lacks review support",
        insight: hasEvidence ? "Trust can be inspected" : "The record should not drive recommendations",
        recommendation: hasEvidence
          ? "Open supporting evidence before taking the next workflow step"
          : "Attach or verify supporting evidence before reuse"
      }
    },
    {
      id: `${row.id}-operator-next-step`,
      title: "Operator action remains the control point",
      explanation:
        "The preview surfaces review guidance, but the appraiser or reviewer decides whether to inspect, verify, reuse, or defer.",
      relatedFacts: ["Synthetic preview", "No production action", "No automated conclusion"],
      confidenceState: "needs_verification",
      freshnessCue: "Preview-only guidance",
      verificationCue: "Operator review required",
      recommendation: "Use the recommendation as a review cue, not as a conclusion.",
      relationshipChain: {
        fact: "The selected record is preview data",
        knowledge: "Workspace context can guide review",
        insight: "Guidance should not become an automated conclusion",
        recommendation: "Use the recommendation as a review cue, not as a conclusion"
      }
    }
  ];
}

function buildEvidencePreviewRows(row: TableRow, passport: PassportPreview | null): InsightEvidencePreview[] {
  if (!passport?.evidenceLinks.length) {
    return row.evidence_link_count > 0
      ? defaultEvidence
      : [
          {
            evidenceType: "Evidence unavailable",
            relationship: "No source support is attached in this preview record.",
            sourceLabel: "No supporting evidence in synthetic preview"
          }
        ];
  }

  return passport.evidenceLinks.map((evidence) => ({
    evidenceType: evidence.source_document_type,
    relationship: "Supports the selected knowledge record and the insight confidence cue.",
    sourceLabel: evidence.display_label
  }));
}
