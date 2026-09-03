import { type FormEvent, useMemo, useState } from "react";
import {
  evidenceLocatorLabel,
  formatReviewLabel,
  formatReviewValue,
  localIntakeReviewData,
  type ReviewCandidate,
  type ReviewConflict,
  type ReviewState
} from "./localIntakeReviewData";

type QuickView = "all" | "needs_attention" | "unresolved_conflicts" | "missing_critical";
type DecisionDraft = { candidateId: string; action: "correct" | "reject" } | null;

const unreviewedStates: ReviewState[] = ["extracted_candidate", "unresolved_conflict"];
const needsAttentionStates: ReviewState[] = [...unreviewedStates, "deferred"];

export function LocalIntakeReviewWorkspace() {
  const [candidates, setCandidates] = useState<Record<string, ReviewCandidate>>(() =>
    Object.fromEntries(
      localIntakeReviewData.topics.flatMap((topic) => topic.candidates).map((candidate) => [candidate.candidate_id, candidate])
    )
  );
  const [conflicts, setConflicts] = useState<Record<string, ReviewConflict>>(() =>
    Object.fromEntries(localIntakeReviewData.conflicts.map((conflict) => [conflict.conflict_id, conflict]))
  );
  const [topicFilter, setTopicFilter] = useState("all");
  const [stateFilter, setStateFilter] = useState("all");
  const [quickView, setQuickView] = useState<QuickView>("all");
  const [expandedEvidence, setExpandedEvidence] = useState<Set<string>>(() => new Set());
  const [decisionDraft, setDecisionDraft] = useState<DecisionDraft>(null);
  const [conflictDraft, setConflictDraft] = useState<string | null>(null);
  const [isAddFactOpen, setIsAddFactOpen] = useState(false);
  const [manualFacts, setManualFacts] = useState<Array<{ fieldKey: string; label: string; value: string; reason: string }>>([]);
  const [briefVisible, setBriefVisible] = useState(false);
  const [statusMessage, setStatusMessage] = useState("AIR-backed synthetic review loaded.");

  const allCandidates = useMemo(() => Object.values(candidates), [candidates]);
  const reviewedCount = allCandidates.filter(
    (candidate) => !unreviewedStates.includes(candidate.state)
  ).length;
  const percentComplete = allCandidates.length ? Math.round((reviewedCount / allCandidates.length) * 100) : 100;
  const unresolvedConflictIds = new Set(
    Object.values(conflicts)
      .filter((conflict) => conflict.status === "unresolved")
      .map((conflict) => conflict.conflict_id)
  );
  const missingCriticalFields = new Set(
    localIntakeReviewData.missing_critical_information.flatMap((issue) => issue.field_keys)
  );

  const visibleTopics = localIntakeReviewData.topics
    .filter((topic) => topicFilter === "all" || topic.topic_key === topicFilter)
    .map((topic) => ({
      ...topic,
      candidates: topic.candidates
        .map((candidate) => candidates[candidate.candidate_id])
        .filter((candidate) => {
          if (stateFilter !== "all" && candidate.state !== stateFilter) return false;
          if (quickView === "needs_attention") return needsAttentionStates.includes(candidate.state);
          if (quickView === "unresolved_conflicts") {
            return candidate.conflict_ids.some((id) => unresolvedConflictIds.has(id));
          }
          if (quickView === "missing_critical") return missingCriticalFields.has(candidate.field_key);
          return true;
        })
    }))
    .filter((topic) => topic.candidates.length > 0);

  function applyDecision(candidateId: string, state: ReviewState, reason: string, correctedValue?: string) {
    setCandidates((current) => ({
      ...current,
      [candidateId]: {
        ...current[candidateId],
        ...(correctedValue !== undefined
          ? {
              original_value: current[candidateId].original_value ?? current[candidateId].value,
              value: correctedValue
            }
          : {}),
        state,
        latest_review: {
          action: stateToAction(state),
          actor_name: "Current synthetic appraiser",
          actor_role: "appraiser",
          occurred_at: "Local preview event",
          reason: correctedValue ? `${reason} Corrected value: ${correctedValue}` : reason
        }
      }
    }));
    setStatusMessage(`${formatReviewLabel(state)} event staged using AIR review semantics.`);
  }

  function handleAccept(candidateId: string) {
    applyDecision(candidateId, "accepted", "Accepted after appraiser review.");
  }

  function handleDefer(candidateId: string) {
    applyDecision(candidateId, "deferred", "Deferred for later appraiser review.");
  }

  function handleDecisionSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!decisionDraft) return;
    const form = new FormData(event.currentTarget);
    const reason = String(form.get("reason") ?? "").trim();
    const correctedValue = String(form.get("correctedValue") ?? "").trim();
    if (!reason || (decisionDraft.action === "correct" && !correctedValue)) return;
    applyDecision(
      decisionDraft.candidateId,
      decisionDraft.action === "correct" ? "corrected" : "rejected",
      reason,
      decisionDraft.action === "correct" ? correctedValue : undefined
    );
    setDecisionDraft(null);
  }

  function handleConflictSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!conflictDraft) return;
    const form = new FormData(event.currentTarget);
    const selectedCandidateId = String(form.get("selectedCandidate") ?? "");
    const reason = String(form.get("reason") ?? "").trim();
    const conflict = conflicts[conflictDraft];
    if (!selectedCandidateId || !reason || !conflict.candidate_ids.includes(selectedCandidateId)) return;
    setCandidates((current) => {
      const next = { ...current };
      for (const candidateId of conflict.candidate_ids) {
        next[candidateId] = {
          ...next[candidateId],
          state: candidateId === selectedCandidateId ? "accepted" : "rejected",
          latest_review: {
            action: candidateId === selectedCandidateId ? "candidate_verified" : "candidate_rejected",
            actor_name: "Current synthetic appraiser",
            actor_role: "appraiser",
            occurred_at: "Local preview event",
            reason
          }
        };
      }
      return next;
    });
    setConflicts((current) => ({
      ...current,
      [conflictDraft]: { ...current[conflictDraft], status: "resolved", reason }
    }));
    setConflictDraft(null);
    setStatusMessage("Conflict resolution staged as one acceptance and explicit competing rejections.");
  }

  function handleAddFact(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const fieldKey = String(form.get("fieldKey") ?? "").trim();
    const label = String(form.get("label") ?? "").trim();
    const value = String(form.get("value") ?? "").trim();
    const reason = String(form.get("reason") ?? "").trim();
    if (!fieldKey.includes(".") || !label || !value || !reason) return;
    setManualFacts((current) => [...current, { fieldKey, label, value, reason }]);
    setIsAddFactOpen(false);
    setStatusMessage("Appraiser-entered fact staged with explicit review provenance.");
  }

  function focusNextUnreviewed() {
    const next = allCandidates.find((candidate) => unreviewedStates.includes(candidate.state));
    if (!next) {
      setStatusMessage("No unreviewed candidate remains in this local preview state.");
      return;
    }
    setTopicFilter("all");
    setStateFilter("all");
    setQuickView("all");
    const focusCandidate = () => document.getElementById(`candidate-${next.candidate_id}`)?.focus();
    focusCandidate();
    requestAnimationFrame(focusCandidate);
  }

  return (
    <div className="intake-shell">
      <aside className="intake-sidebar" aria-label="Falcon navigation">
        <div className="intake-brand">FALCON</div>
        <span className="intake-module">INTELLIGENCE</span>
        <nav>
          <span>Orders</span>
          <span className="active">Intake review</span>
          <span>Property library</span>
        </nav>
        <p>Synthetic local workflow</p>
      </aside>

      <main className="intake-main">
        <header className="intake-header">
          <div>
            <p className="intake-eyebrow">Local Intake Review · AIR V1</p>
            <h1>{localIntakeReviewData.assignment.label}</h1>
            <p>{localIntakeReviewData.assignment.local_assignment_key}</p>
          </div>
          <div className="intake-header-actions">
            <button type="button" className="secondary" onClick={() => setIsAddFactOpen(true)}>Add fact</button>
            <button
              type="button"
              onClick={() => {
                setStatusMessage("Canonical AIR refresh requested from the local review event adapter.");
                setBriefVisible(true);
              }}
            >
              Assemble / refresh AIR
            </button>
          </div>
        </header>

        <section className="intake-status-strip" aria-label="Review progress">
          <div>
            <strong>{percentComplete}%</strong>
            <span>{reviewedCount} of {allCandidates.length} candidates reviewed</span>
          </div>
          <progress value={reviewedCount} max={allCandidates.length} aria-label="Candidate review progress" />
          <div className="intake-status-pills">
            <span className={`status-pill ${localIntakeReviewData.readiness.overall_status}`}>
              Readiness: {formatReviewLabel(localIntakeReviewData.readiness.overall_status)}
            </span>
            <span className="status-pill attention">
              {Object.values(conflicts).filter((item) => item.status === "unresolved").length} unresolved conflicts
            </span>
            <span className="status-pill attention">
              {localIntakeReviewData.missing_critical_information.length} critical gaps
            </span>
          </div>
          <p className="intake-live-status" role="status">{statusMessage}</p>
        </section>

        <section className="intake-overview" aria-labelledby="assignment-overview-title">
          <div className="section-heading">
            <div>
              <p className="intake-eyebrow">Current canonical facts</p>
              <h2 id="assignment-overview-title">Assignment overview</h2>
            </div>
            <span>AIR schema {localIntakeReviewData.semantic_source.air_schema_version}</span>
          </div>
          <dl className="overview-grid">
            {localIntakeReviewData.assignment.overview.slice(0, 8).map((fact) => (
              <div key={fact.fact_id}>
                <dt>{fact.label}</dt>
                <dd>{formatReviewValue(fact.value, fact.unit)}</dd>
                <span>{formatReviewLabel(fact.professional_boundary)}</span>
              </div>
            ))}
          </dl>
        </section>

        <div className="intake-workspace-grid">
          <section className="intake-review-panel" aria-labelledby="candidate-review-title">
            <div className="section-heading">
              <div>
                <p className="intake-eyebrow">Evidence-led decisions</p>
                <h2 id="candidate-review-title">Review extracted candidates</h2>
              </div>
              <button type="button" className="secondary compact" onClick={focusNextUnreviewed}>Next unreviewed</button>
            </div>

            <div className="quick-views" aria-label="Attention views">
              {([
                ["all", "All candidates"],
                ["needs_attention", "Needs attention"],
                ["unresolved_conflicts", "Unresolved conflicts"],
                ["missing_critical", "Missing critical"]
              ] as Array<[QuickView, string]>).map(([value, label]) => (
                <button
                  type="button"
                  key={value}
                  className={quickView === value ? "active" : ""}
                  aria-pressed={quickView === value}
                  onClick={() => setQuickView(value)}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="review-filters">
              <label>
                Topic
                <select value={topicFilter} onChange={(event) => setTopicFilter(event.target.value)}>
                  <option value="all">All topics</option>
                  {localIntakeReviewData.topics.map((topic) => (
                    <option value={topic.topic_key} key={topic.topic_key}>{topic.label}</option>
                  ))}
                </select>
              </label>
              <label>
                Review state
                <select value={stateFilter} onChange={(event) => setStateFilter(event.target.value)}>
                  <option value="all">All states</option>
                  {(["extracted_candidate", "unresolved_conflict", "accepted", "corrected", "rejected", "deferred"] as ReviewState[]).map((state) => (
                    <option value={state} key={state}>{formatReviewLabel(state)}</option>
                  ))}
                </select>
              </label>
            </div>

            {quickView === "missing_critical" && (
              <MissingCriticalPanel />
            )}

            <div className="candidate-topics">
              {visibleTopics.length ? visibleTopics.map((topic) => (
                <section className="candidate-topic" key={topic.topic_key} aria-labelledby={`topic-${topic.topic_key}`}>
                  <div className="topic-title">
                    <h3 id={`topic-${topic.topic_key}`}>{topic.label}</h3>
                    <span>{topic.candidates.length}</span>
                  </div>
                  {topic.candidates.map((candidate) => (
                    <CandidateCard
                      key={candidate.candidate_id}
                      candidate={candidate}
                      expanded={expandedEvidence.has(candidate.candidate_id)}
                      conflicts={candidate.conflict_ids.map((id) => conflicts[id]).filter(Boolean)}
                      onToggleEvidence={() => setExpandedEvidence((current) => toggleSet(current, candidate.candidate_id))}
                      onAccept={() => handleAccept(candidate.candidate_id)}
                      onCorrect={() => setDecisionDraft({ candidateId: candidate.candidate_id, action: "correct" })}
                      onReject={() => setDecisionDraft({ candidateId: candidate.candidate_id, action: "reject" })}
                      onDefer={() => handleDefer(candidate.candidate_id)}
                      onResolve={(conflictId) => setConflictDraft(conflictId)}
                    />
                  ))}
                </section>
              )) : (
                <div className="empty-review-state" role="status">
                  <h3>No candidate rows match this view.</h3>
                  <p>Missing fields can exist without an extracted candidate. Review the critical gap list or reset filters.</p>
                  <button type="button" className="secondary compact" onClick={() => { setQuickView("all"); setStateFilter("all"); setTopicFilter("all"); }}>Reset view</button>
                </div>
              )}
            </div>
          </section>

          <aside className="intake-attention-rail">
            <ReadinessPanel />
            <ConflictPanel conflicts={Object.values(conflicts)} candidates={candidates} onResolve={setConflictDraft} />
            {manualFacts.length > 0 && (
              <section className="rail-card" aria-labelledby="manual-facts-title">
                <h2 id="manual-facts-title">Appraiser-entered facts</h2>
                {manualFacts.map((fact) => (
                  <div className="manual-fact" key={`${fact.fieldKey}-${fact.value}`}>
                    <strong>{fact.label}</strong>
                    <span>{fact.value}</span>
                    <small>{fact.fieldKey} · {fact.reason}</small>
                  </div>
                ))}
              </section>
            )}
          </aside>
        </div>

        <section className="brief-controls" aria-label="Assignment brief actions">
          <div>
            <p className="intake-eyebrow">Appraisal-production handoff</p>
            <h2>Assignment / Property Brief V1</h2>
            <p>Generated only from current AIR facts, issues, evidence, and reference-only leads.</p>
          </div>
          <div className="intake-header-actions">
            <button type="button" onClick={() => setBriefVisible(true)}>Generate / review brief</button>
            <ExportLinks />
          </div>
        </section>

        {briefVisible && <BriefPanel />}
      </main>

      {decisionDraft && (
        <DecisionDialog draft={decisionDraft} candidate={candidates[decisionDraft.candidateId]} onCancel={() => setDecisionDraft(null)} onSubmit={handleDecisionSubmit} />
      )}
      {conflictDraft && (
        <ConflictDialog conflict={conflicts[conflictDraft]} candidates={candidates} onCancel={() => setConflictDraft(null)} onSubmit={handleConflictSubmit} />
      )}
      {isAddFactOpen && <AddFactDialog onCancel={() => setIsAddFactOpen(false)} onSubmit={handleAddFact} />}
    </div>
  );
}

function CandidateCard({
  candidate,
  conflicts,
  expanded,
  onAccept,
  onCorrect,
  onReject,
  onDefer,
  onResolve,
  onToggleEvidence
}: {
  candidate: ReviewCandidate;
  conflicts: ReviewConflict[];
  expanded: boolean;
  onAccept: () => void;
  onCorrect: () => void;
  onReject: () => void;
  onDefer: () => void;
  onResolve: (conflictId: string) => void;
  onToggleEvidence: () => void;
}) {
  const evidence = candidate.evidence[0];
  const unresolved = conflicts.find((conflict) => conflict.status === "unresolved");
  return (
    <article className={`candidate-card state-${candidate.state}`} id={`candidate-${candidate.candidate_id}`} tabIndex={-1}>
      <div className="candidate-main">
        <div>
          <div className="candidate-label-line">
            <h4>{candidate.label}</h4>
            {candidate.material && <span className="material-badge">Material</span>}
            {unresolved && <span className="conflict-badge">Conflict</span>}
          </div>
          <code>{candidate.field_key}</code>
          <p className="candidate-value">{formatReviewValue(candidate.value, candidate.unit)}</p>
          {candidate.original_value !== undefined && (
            <p className="latest-review">
              <strong>Original observation:</strong>{" "}
              {formatReviewValue(candidate.original_value, candidate.unit)}
            </p>
          )}
        </div>
        <span className={`review-state ${candidate.state}`}>{formatReviewLabel(candidate.state)}</span>
      </div>

      <div className="candidate-source-line">
        <span><strong>{evidence.source_document}</strong></span>
        <span>{evidenceLocatorLabel(evidence.locator)}</span>
        <span>{evidence.extraction_method}</span>
        <span>{formatReviewLabel(candidate.machine_confidence)} confidence</span>
      </div>

      {candidate.latest_review && (
        <p className="latest-review"><strong>Latest decision:</strong> {candidate.latest_review.reason}</p>
      )}

      <div className="candidate-actions">
        <button type="button" onClick={onAccept}>Accept</button>
        <button type="button" className="secondary" onClick={onCorrect}>Correct</button>
        <button type="button" className="danger" onClick={onReject}>Reject</button>
        <button type="button" className="secondary" onClick={onDefer}>Defer</button>
        {unresolved && <button type="button" className="attention" onClick={() => onResolve(unresolved.conflict_id)}>Resolve conflict</button>}
        <button type="button" className="link-button" aria-expanded={expanded} onClick={onToggleEvidence}>
          {expanded ? "Hide evidence detail" : `Evidence (${candidate.evidence.length})`}
        </button>
      </div>

      {expanded && (
        <div className="evidence-detail">
          {candidate.evidence.map((item) => (
            <dl key={item.evidence_id}>
              <div><dt>Source</dt><dd>{item.source_document}</dd></div>
              <div><dt>Location</dt><dd>{evidenceLocatorLabel(item.locator)}</dd></div>
              <div><dt>Method</dt><dd>{item.extraction_method}</dd></div>
              <div><dt>Quality</dt><dd>{formatReviewLabel(item.quality)}</dd></div>
              <div><dt>Evidence ID</dt><dd><code>{item.evidence_id}</code></dd></div>
            </dl>
          ))}
        </div>
      )}
    </article>
  );
}

function MissingCriticalPanel() {
  return (
    <section className="missing-critical" aria-labelledby="missing-critical-title">
      <h3 id="missing-critical-title">Missing critical information</h3>
      {localIntakeReviewData.missing_critical_information.map((issue) => (
        <div key={issue.issue_id}>
          <strong>{issue.field_keys.join(", ")}</strong>
          <span>{issue.message}</span>
        </div>
      ))}
    </section>
  );
}

function ReadinessPanel() {
  return (
    <section className="rail-card" aria-labelledby="readiness-title">
      <p className="intake-eyebrow">Blocking vs. nonblocking</p>
      <h2 id="readiness-title">Readiness</h2>
      <div className="readiness-list">
        {localIntakeReviewData.readiness.areas.map((area) => (
          <div key={area.area}>
            <span>{formatReviewLabel(area.area)}</span>
            <strong className={area.status}>{formatReviewLabel(area.status)}</strong>
            <small>{area.issue_ids.length} issue(s)</small>
          </div>
        ))}
      </div>
      <h3>Current blockers</h3>
      <ul>
        {localIntakeReviewData.readiness.issues.filter((issue) => issue.severity === "blocking").map((issue) => (
          <li key={issue.issue_id}>{issue.message}</li>
        ))}
      </ul>
    </section>
  );
}

function ConflictPanel({ conflicts, candidates, onResolve }: { conflicts: ReviewConflict[]; candidates: Record<string, ReviewCandidate>; onResolve: (id: string) => void }) {
  return (
    <section className="rail-card" aria-labelledby="conflicts-title">
      <h2 id="conflicts-title">Conflicts</h2>
      {conflicts.map((conflict) => (
        <div className="rail-conflict" key={conflict.conflict_id}>
          <div><strong>{conflict.field_key}</strong><span className={`review-state ${conflict.status}`}>{formatReviewLabel(conflict.status)}</span></div>
          <p>{conflict.candidate_ids.map((id) => formatReviewValue(candidates[id].value)).join(" ↔ ")}</p>
          <small>{conflict.reason}</small>
          {conflict.status === "unresolved" && <button type="button" className="attention compact" onClick={() => onResolve(conflict.conflict_id)}>Resolve conflict</button>}
        </div>
      ))}
    </section>
  );
}

function BriefPanel() {
  const brief = localIntakeReviewData.brief;
  return (
    <section className="brief-panel" aria-labelledby="brief-title">
      <div className="section-heading">
        <div>
          <p className="intake-eyebrow">Brief v{brief.brief_version} · AIR schema {brief.air_schema_version}</p>
          <h2 id="brief-title">Assignment / Property Brief</h2>
        </div>
        <span className={`status-pill ${brief.readiness_status}`}>{formatReviewLabel(brief.readiness_status)}</span>
      </div>
      <div className="brief-grid">
        <BriefFacts title="Assignment synopsis" facts={brief.assignment_synopsis} />
        <BriefFacts title="Subject synopsis" facts={brief.subject_synopsis} />
        <section>
          <h3>Issues requiring attention</h3>
          {brief.issues_requiring_attention.map((issue) => (
            <div className={`brief-issue ${issue.severity}`} key={issue.issue_id}>
              <strong>{formatReviewLabel(issue.area)}</strong>
              <p>{issue.message}</p>
            </div>
          ))}
        </section>
        <section>
          <h3>Comparable and market leads</h3>
          {brief.comparable_and_market_leads.map((lead) => (
            <div className="brief-lead" key={lead.reference_id}>
              <strong>{formatReviewLabel(lead.lead_type)}</strong>
              <span>{lead.reference_id}</span>
              <small>{formatReviewLabel(lead.selection_status)} · reference only</small>
            </div>
          ))}
          <p className="boundary-note">Extraction does not constitute professional comparable selection.</p>
        </section>
        <section className="brief-evidence-section">
          <h3>Evidence summary</h3>
          {brief.evidence_summary.map((item) => (
            <div className="brief-evidence" key={item.evidence_id}>
              <strong>{item.source_document}</strong>
              <span>{evidenceLocatorLabel(item.locator)} · {item.extraction_method}</span>
              <code>{item.evidence_id}</code>
            </div>
          ))}
        </section>
        <section className="professional-boundary">
          <h3>Professional boundary</h3>
          <ul>{brief.professional_boundary.map((item) => <li key={item}>{item}</li>)}</ul>
        </section>
      </div>
    </section>
  );
}

function BriefFacts({ title, facts }: { title: string; facts: typeof localIntakeReviewData.brief.assignment_synopsis }) {
  return (
    <section>
      <h3>{title}</h3>
      <dl className="brief-facts">
        {facts.map((fact) => (
          <div key={fact.fact_id}>
            <dt>{fact.label}</dt>
            <dd>{formatReviewValue(fact.value, fact.unit)}</dd>
            <span>{formatReviewLabel(fact.professional_boundary)}</span>
          </div>
        ))}
      </dl>
    </section>
  );
}

function ExportLinks() {
  const airJson = `${JSON.stringify(localIntakeReviewData.air, null, 2)}\n`;
  const briefJson = `${JSON.stringify(localIntakeReviewData.brief, null, 2)}\n`;
  return (
    <div className="export-links" aria-label="Local deterministic exports">
      <a download="assignment-intelligence-record-v1.json" href={dataUri("application/json", airJson)}>AIR JSON</a>
      <a download="assignment-property-brief-v1.json" href={dataUri("application/json", briefJson)}>Brief JSON</a>
      <a download="assignment-property-brief-v1.md" href={dataUri("text/markdown", localIntakeReviewData.brief_markdown)}>Markdown</a>
    </div>
  );
}

function DecisionDialog({ draft, candidate, onCancel, onSubmit }: { draft: NonNullable<DecisionDraft>; candidate: ReviewCandidate; onCancel: () => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void }) {
  return (
    <div className="dialog-backdrop">
      <section className="review-dialog" role="dialog" aria-modal="true" aria-labelledby="decision-dialog-title">
        <h2 id="decision-dialog-title">{draft.action === "correct" ? "Correct candidate" : "Reject candidate"}</h2>
        <p><strong>{candidate.label}:</strong> {formatReviewValue(candidate.value, candidate.unit)}</p>
        <form onSubmit={onSubmit}>
          {draft.action === "correct" && <label>Corrected value<input name="correctedValue" required autoFocus /></label>}
          <label>Reason<textarea name="reason" required autoFocus={draft.action === "reject"} /></label>
          <div className="dialog-actions"><button type="button" className="secondary" onClick={onCancel}>Cancel</button><button type="submit">Save decision</button></div>
        </form>
      </section>
    </div>
  );
}

function ConflictDialog({ conflict, candidates, onCancel, onSubmit }: { conflict: ReviewConflict; candidates: Record<string, ReviewCandidate>; onCancel: () => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void }) {
  return (
    <div className="dialog-backdrop">
      <section className="review-dialog" role="dialog" aria-modal="true" aria-labelledby="conflict-dialog-title">
        <h2 id="conflict-dialog-title">Resolve conflict</h2>
        <p>{conflict.field_key}</p>
        <form onSubmit={onSubmit}>
          <fieldset><legend>Select the supported value</legend>{conflict.candidate_ids.map((id, index) => (
            <label className="radio-row" key={id}><input type="radio" name="selectedCandidate" value={id} required defaultChecked={index === 0} /><span>{formatReviewValue(candidates[id].value)}</span></label>
          ))}</fieldset>
          <label>Resolution reason<textarea name="reason" required /></label>
          <div className="dialog-actions"><button type="button" className="secondary" onClick={onCancel}>Cancel</button><button type="submit">Resolve conflict</button></div>
        </form>
      </section>
    </div>
  );
}

function AddFactDialog({ onCancel, onSubmit }: { onCancel: () => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void }) {
  return (
    <div className="dialog-backdrop">
      <section className="review-dialog" role="dialog" aria-modal="true" aria-labelledby="add-fact-title">
        <h2 id="add-fact-title">Add appraiser-entered fact</h2>
        <form onSubmit={onSubmit}>
          <label>AIR field key<input name="fieldKey" pattern=".+\..+" placeholder="subject.condition" required autoFocus /></label>
          <label>Field label<input name="label" placeholder="Condition" required /></label>
          <label>Value<input name="value" required /></label>
          <label>Reason and provenance<textarea name="reason" required /></label>
          <div className="dialog-actions"><button type="button" className="secondary" onClick={onCancel}>Cancel</button><button type="submit">Add fact</button></div>
        </form>
      </section>
    </div>
  );
}

function toggleSet(current: Set<string>, value: string) {
  const next = new Set(current);
  if (next.has(value)) next.delete(value);
  else next.add(value);
  return next;
}

function stateToAction(state: ReviewState) {
  return {
    accepted: "candidate_verified",
    corrected: "candidate_corrected",
    rejected: "candidate_rejected",
    deferred: "candidate_deferred",
    extracted_candidate: "candidate_observed",
    unresolved_conflict: "candidate_observed"
  }[state];
}

function dataUri(mime: string, value: string) {
  return `data:${mime};charset=utf-8,${encodeURIComponent(value)}`;
}
