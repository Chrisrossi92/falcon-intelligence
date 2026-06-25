import { type KeyboardEvent, type RefObject, useEffect, useMemo, useRef, useState } from "react";
import {
  coordinatePlanePosition,
  findSelectedRow,
  formatLabel,
  getInitialSelectedId,
  mapWorkspaceData,
  type MapPin,
  type TableRow
} from "./mapWorkspaceData";
import { buildAuditPreview, buildAuditUnavailablePreview, type AuditPreview } from "./auditData";
import {
  buildCorrectionAuditPreview,
  type CorrectionAuditPreview
} from "./correctionAuditData";
import { buildEvidencePreview, buildEvidenceUnavailablePreview, type EvidencePreview } from "./evidenceData";
import { buildPassportPreview, type EvidenceLink, type PassportPreview } from "./passportData";

type WorkspacePreviewState =
  | "content"
  | "loading"
  | "empty"
  | "permissionDenied"
  | "stale"
  | "noResults"
  | "evidenceUnavailable"
  | "auditUnavailable"
  | "error";

type LayerKey = "subjects" | "verifiedKnowledge" | "reports" | "evidenceAvailable" | "auditActivity";

type LayerState = Record<LayerKey, boolean>;

type WorkspaceFilters = {
  auditActivity: "" | "available" | "unavailable";
  evidenceAvailable: "" | "available" | "unavailable";
  propertyType: string;
  recordStatus: string;
  search: string;
  verificationStatus: string;
};

const workspaceStateOptions: Array<{ value: WorkspacePreviewState; label: string }> = [
  { value: "permissionDenied", label: "Permission denied" },
  { value: "error", label: "Error" },
  { value: "loading", label: "Loading" },
  { value: "empty", label: "Empty" },
  { value: "stale", label: "Stale data" },
  { value: "noResults", label: "No results" },
  { value: "content", label: "Content available" },
  { value: "evidenceUnavailable", label: "Supporting evidence unavailable" },
  { value: "auditUnavailable", label: "Review history unavailable" }
];

const blockingStates: WorkspacePreviewState[] = ["permissionDenied", "error", "loading", "empty", "noResults"];
const contentVisibleStates: WorkspacePreviewState[] = ["content", "stale", "evidenceUnavailable", "auditUnavailable"];
const defaultLayers: LayerState = {
  auditActivity: true,
  evidenceAvailable: true,
  reports: true,
  subjects: true,
  verifiedKnowledge: true
};

const defaultWorkspaceFilters: WorkspaceFilters = {
  auditActivity: "",
  evidenceAvailable: "",
  propertyType: "",
  recordStatus: "",
  search: "",
  verificationStatus: ""
};

const futureLayers = ["Sales", "Leases", "Market Areas", "Comparable Clusters", "AI Suggestions"];

type WorkspaceNotice = {
  badge: string;
  detail: string;
  message: string;
  role: "status" | "alert";
  title: string;
};

function getWorkspaceNotice(state: WorkspacePreviewState): WorkspaceNotice {
  switch (state) {
    case "permissionDenied":
      return {
        badge: "Restricted",
        detail: "Restricted properties, supporting evidence, and review history are not shown in this preview state.",
        message: "Access to internal intelligence is controlled by firm policy.",
        role: "alert",
        title: "Falcon Intelligence is not available for your role."
      };
    case "error":
      return {
        badge: "Error",
        detail: "Use reset to return to the preview workspace.",
        message: "Falcon Intelligence could not load the preview records.",
        role: "alert",
        title: "Workspace intelligence is unavailable."
      };
    case "loading":
      return {
        badge: "Loading",
        detail: "No verified records, confidence values, or result totals are shown until data resolves.",
        message: "Verified records, filters, and map locations are being prepared.",
        role: "status",
        title: "Loading workspace intelligence."
      };
    case "empty":
      return {
        badge: "Empty",
        detail: "Facts become searchable only after verification and permission checks.",
        message: "No eligible preview assignments or verified facts are available to this workspace yet.",
        role: "status",
        title: "No verified intelligence is available yet."
      };
    case "noResults":
      return {
        badge: "No results",
        detail: "Adjust or reset filters to broaden the workspace view.",
        message: "The current search and filters do not match any preview properties.",
        role: "status",
        title: "No properties match the current view."
      };
    case "stale":
      return {
        badge: "Stale",
        detail: "Review verification dates, stale warnings, and supporting evidence before relying on these records.",
        message: "Workspace remains usable, but some intelligence may be out of date.",
        role: "status",
        title: "Some intelligence may be stale."
      };
    case "evidenceUnavailable":
      return {
        badge: "Supporting evidence unavailable",
        detail: "The drawer explains the limitation without showing a source document.",
        message: "Supporting evidence cannot be opened from the current workspace.",
        role: "status",
        title: "Supporting evidence is unavailable."
      };
    case "auditUnavailable":
      return {
        badge: "Review history unavailable",
        detail: "No review events are shown unless they exist in the preview records.",
        message: "Review history is not available for this record.",
        role: "status",
        title: "Review history is unavailable."
      };
    case "content":
    default:
      return {
        badge: "Available",
        detail: "Preview records are available.",
        message: "Preview records are available.",
        role: "status",
        title: "Records available."
      };
  }
}

function buildContextText({
  audit,
  evidence,
  filterNotice,
  hasUserSelectedProperty,
  isPassportOpen,
  isWorkspaceInteractive,
  layerNotice,
  passport,
  previewState,
  selectedRow,
  visibleRecordCount,
  workspaceNotice
}: {
  audit: AuditPreview | null;
  evidence: EvidencePreview | null;
  filterNotice: WorkspaceNotice | null;
  hasUserSelectedProperty: boolean;
  isPassportOpen: boolean;
  isWorkspaceInteractive: boolean;
  layerNotice: WorkspaceNotice | null;
  passport: PassportPreview | null;
  previewState: WorkspacePreviewState;
  selectedRow: TableRow;
  visibleRecordCount: number;
  workspaceNotice: WorkspaceNotice;
}) {
  if (!isWorkspaceInteractive) {
    return `${workspaceNotice.title} • ${workspaceNotice.message}`;
  }

  if (layerNotice) {
    return `${layerNotice.title} • ${visibleRecordCount} visible properties • Adjust layers to restore map context`;
  }

  if (filterNotice) {
    return `${filterNotice.title} • ${visibleRecordCount} visible properties • Reset filters to restore workspace context`;
  }

  if (audit) {
    return `${audit.title} • Review history • Accountability trail`;
  }

  if (evidence) {
    return `${evidence.title} • Supporting evidence • Source: ${evidence.sourceDocumentId}`;
  }

  if (isPassportOpen) {
    return `${selectedRow.display_label} • Passport open • ${passport?.factLabel ?? "Verified intelligence summary"}`;
  }

  if (previewState === "stale") {
    return `Falcon Intelligence Preview • Stale-data caution • Review provenance before relying on records`;
  }

  if (previewState === "evidenceUnavailable") {
    return `Falcon Intelligence Preview • Supporting evidence unavailable • No source document opened`;
  }

  if (previewState === "auditUnavailable") {
    return `Falcon Intelligence Preview • Review history unavailable • No review timeline implied`;
  }

  if (hasUserSelectedProperty) {
    const evidenceLabel = selectedRow.evidence_link_count === 1 ? "evidence item" : "evidence items";
    return `${selectedRow.display_label} • Knowledge Summary • ${formatLabel(selectedRow.verification_status)} property • ${selectedRow.evidence_link_count} ${evidenceLabel}`;
  }

  return `Falcon Intelligence Preview • ${mapWorkspaceData.result_counts.filtered_records} visible properties • Verified property knowledge preview`;
}

function getLayerNotice(isWorkspaceInteractive: boolean, rows: TableRow[]): WorkspaceNotice | null {
  if (!isWorkspaceInteractive || rows.length > 0) {
    return null;
  }

  return {
    badge: "Layer filtered",
    detail: "Layer settings are hiding the current preview properties. Turn Subjects back on to restore markers and rows.",
    message: "No properties are visible with the current layers.",
    role: "status",
    title: "No properties match the active layers."
  };
}

function getFilterNotice(
  isWorkspaceInteractive: boolean,
  hasFilteredLayerRows: boolean,
  rows: TableRow[],
  filters: WorkspaceFilters
): WorkspaceNotice | null {
  if (!isWorkspaceInteractive || !hasFilteredLayerRows || rows.length > 0 || !hasActiveWorkspaceFilters(filters)) {
    return null;
  }

  return {
    badge: "Filtered",
    detail: "Search or filter settings are hiding the current preview properties. Reset filters to restore markers and rows.",
    message: "No properties match the current search and filters.",
    role: "status",
    title: "No properties match the current view."
  };
}

function getSelectedHiddenNotice(
  isWorkspaceInteractive: boolean,
  isSelectedVisible: boolean,
  filters: WorkspaceFilters,
  layers: LayerState
): WorkspaceNotice | null {
  if (!isWorkspaceInteractive || isSelectedVisible) {
    return null;
  }

  const isFilterHidden = hasActiveWorkspaceFilters(filters);

  return {
    badge: isFilterHidden ? "Filter hidden" : "Layer hidden",
    detail: isFilterHidden
      ? "Reset filters to make the selected property available again."
      : "Reset layers to make the selected property available again.",
    message: isFilterHidden
      ? "The selected property is hidden by the current local search or filters."
      : "The selected property is hidden by the current layers.",
    role: "status",
    title: "Selection unavailable."
  };
}

function rowHasAuditActivity(row: TableRow) {
  return Boolean(buildPassportPreview(row)?.auditEventIds.length);
}

function getVerifiedFactCount(passport: PassportPreview | null) {
  return passport ? 1 : 0;
}

function getEvidenceCount(row: TableRow, passport: PassportPreview | null) {
  return passport?.evidenceLinks.length ?? row.evidence_link_count;
}

function getAuditActivityCount(row: TableRow, passport: PassportPreview | null) {
  return passport?.auditEventIds.length ?? (rowHasAuditActivity(row) ? 1 : 0);
}

function getLastReviewLabel(passport: PassportPreview | null) {
  if (passport?.review.reviewedAt) {
    return passport.review.reviewedBy
      ? `${passport.review.reviewedAt} by ${passport.review.reviewedBy}`
      : passport.review.reviewedAt;
  }

  if (passport?.review.verifiedAt) {
    return passport.review.verifiedBy
      ? `${passport.review.verifiedAt} by ${passport.review.verifiedBy}`
      : passport.review.verifiedAt;
  }

  return "Not available in preview";
}

function getKnowledgeTrustSentence(row: TableRow, passport: PassportPreview | null) {
  if (row.verification_status === "verified" && getEvidenceCount(row, passport) > 0) {
    return "This property contains verified institutional knowledge with supporting evidence available.";
  }

  if (row.verification_status === "verified") {
    return "This property contains verified institutional knowledge. Supporting evidence is not available in this preview.";
  }

  return "This property is not presented as verified knowledge in the current preview.";
}

function filterRowsByLayers(rows: TableRow[], layers: LayerState) {
  if (!layers.subjects) {
    return [];
  }

  return rows;
}

function hasActiveWorkspaceFilters(filters: WorkspaceFilters) {
  return Object.values(filters).some((value) => value !== "");
}

function filterRowsByWorkspaceFilters(rows: TableRow[], filters: WorkspaceFilters) {
  const search = filters.search.trim().toLowerCase();

  return rows.filter((row) => {
    const passport = buildPassportPreview(row);
    const searchableText = [
      row.display_label,
      row.address,
      row.city,
      row.property_type,
      row.status,
      row.verification_status,
      row.record_type
    ]
      .join(" ")
      .toLowerCase();

    return (
      (!search || searchableText.includes(search)) &&
      (!filters.propertyType || row.property_type === filters.propertyType) &&
      (!filters.verificationStatus || row.verification_status === filters.verificationStatus) &&
      (!filters.recordStatus || row.status === filters.recordStatus) &&
      (!filters.evidenceAvailable ||
        (filters.evidenceAvailable === "available" ? row.evidence_link_count > 0 : row.evidence_link_count === 0)) &&
      (!filters.auditActivity ||
        (filters.auditActivity === "available"
          ? Boolean(passport?.auditEventIds.length)
          : !passport?.auditEventIds.length))
    );
  });
}

function updateWorkspaceFilter<K extends keyof WorkspaceFilters>(
  filters: WorkspaceFilters,
  key: K,
  value: WorkspaceFilters[K]
) {
  return { ...filters, [key]: value };
}

export function IntelligenceWorkspacePreview() {
  const [selectedId, setSelectedId] = useState(() => getInitialSelectedId());
  const [hasUserSelectedProperty, setHasUserSelectedProperty] = useState(false);
  const [isPassportOpen, setIsPassportOpen] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidencePreview | null>(null);
  const [selectedAudit, setSelectedAudit] = useState<AuditPreview | null>(null);
  const [previewState, setPreviewState] = useState<WorkspacePreviewState>("content");
  const [layers, setLayers] = useState<LayerState>(defaultLayers);
  const [workspaceFilters, setWorkspaceFilters] = useState<WorkspaceFilters>(defaultWorkspaceFilters);
  const [isWorkflowGuidanceDismissed, setIsWorkflowGuidanceDismissed] = useState(false);
  const passportActionRef = useRef<HTMLButtonElement>(null);
  const passportCloseRef = useRef<HTMLButtonElement>(null);
  const evidenceCloseRef = useRef<HTMLButtonElement>(null);
  const auditCloseRef = useRef<HTMLButtonElement>(null);
  const selectedRow = findSelectedRow(selectedId);
  const pins = mapWorkspaceData.map_pins;
  const selectedPassport = buildPassportPreview(selectedRow);
  const selectedCorrectionAudit = buildCorrectionAuditPreview(selectedRow, selectedPassport);
  const isWorkspaceBlocked = blockingStates.includes(previewState);
  const isWorkspaceInteractive = contentVisibleStates.includes(previewState);
  const layerRows = isWorkspaceInteractive ? filterRowsByLayers(mapWorkspaceData.table_rows, layers) : [];
  const visibleRows = isWorkspaceInteractive ? filterRowsByWorkspaceFilters(layerRows, workspaceFilters) : [];
  const visibleRowIds = new Set(visibleRows.map((row) => row.id));
  const visiblePins = isWorkspaceInteractive ? pins.filter((pin) => visibleRowIds.has(pin.id)) : [];
  const isSelectedVisible = visibleRowIds.has(selectedId);
  const workspaceNotice = getWorkspaceNotice(previewState);
  const layerNotice = getLayerNotice(isWorkspaceInteractive, layerRows);
  const filterNotice = getFilterNotice(isWorkspaceInteractive, layerRows.length > 0, visibleRows, workspaceFilters);
  const activeNotice = filterNotice ?? layerNotice ?? workspaceNotice;
  const selectedHiddenNotice = getSelectedHiddenNotice(
    isWorkspaceInteractive,
    isSelectedVisible,
    workspaceFilters,
    layers
  );
  const selectionNotice = selectedHiddenNotice ?? activeNotice;

  const selectedPinLabel = useMemo(
    () =>
      isWorkspaceInteractive && isSelectedVisible
        ? pins.find((pin) => pin.id === selectedId)?.display_label ?? selectedRow.display_label
        : selectionNotice.title,
    [isSelectedVisible, isWorkspaceInteractive, pins, selectedId, selectedRow.display_label, selectionNotice.title]
  );

  function resetNestedDrawers() {
    setSelectedAudit(null);
    setSelectedEvidence(null);
    setIsPassportOpen(false);
  }

  function handleSelectProperty(id: string) {
    setSelectedId(id);
    setHasUserSelectedProperty(true);
  }

  function handleLayerChange(layer: LayerKey, value: boolean) {
    setLayers((current) => ({ ...current, [layer]: value }));
    resetNestedDrawers();
  }

  function handleClosePassport() {
    setSelectedEvidence(null);
    setSelectedAudit(null);
    setIsPassportOpen(false);
    requestAnimationFrame(() => passportActionRef.current?.focus());
  }

  function handleCloseEvidence() {
    setSelectedAudit(null);
    setSelectedEvidence(null);
    requestAnimationFrame(() => passportCloseRef.current?.focus());
  }

  function handleCloseAudit() {
    setSelectedAudit(null);
    requestAnimationFrame(() => evidenceCloseRef.current?.focus());
  }

  useEffect(() => {
    if (selectedAudit) {
      auditCloseRef.current?.focus();
      return;
    }

    if (selectedEvidence) {
      evidenceCloseRef.current?.focus();
      return;
    }

    if (isPassportOpen) {
      passportCloseRef.current?.focus();
    }
  }, [isPassportOpen, selectedAudit, selectedEvidence]);

  useEffect(() => {
    function handleEscape(event: globalThis.KeyboardEvent) {
      if (event.key !== "Escape") {
        return;
      }

      if (selectedAudit) {
        event.preventDefault();
        handleCloseAudit();
        return;
      }

      if (selectedEvidence) {
        event.preventDefault();
        handleCloseEvidence();
        return;
      }

      if (isPassportOpen) {
        event.preventDefault();
        handleClosePassport();
      }
    }

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isPassportOpen, selectedAudit, selectedEvidence]);

  const contextText = buildContextText({
    audit: selectedAudit,
    evidence: selectedEvidence,
    filterNotice,
    hasUserSelectedProperty,
    isPassportOpen,
    isWorkspaceInteractive,
    layerNotice,
    passport: selectedPassport,
    previewState,
    selectedRow,
    visibleRecordCount: visibleRows.length,
    workspaceNotice
  });

  return (
    <div
      className={[
        "falcon-shell",
        isPassportOpen ? "has-passport-drawer" : "",
        selectedEvidence ? "has-evidence-drawer" : "",
        selectedAudit ? "has-audit-drawer" : ""
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <aside className="falcon-sidebar" aria-label="Falcon navigation">
        <div className="falcon-brand">Falcon</div>
        <nav>
          {["Dashboard", "Orders", "Calendar", "Clients"].map((item) => (
            <span key={item}>{item}</span>
          ))}
          <span className="nav-active">Intelligence</span>
          <span>Administration</span>
        </nav>
      </aside>

      <main className="workspace-shell">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">Intelligence / Map</p>
            <h1>Map Workspace</h1>
            <p className="header-copy">
              Internal preview using approved synthetic records. Appraiser judgment remains final.
            </p>
          </div>
          <div className="workspace-summary" aria-label="Workspace summary">
            <strong>{isWorkspaceBlocked ? "—" : mapWorkspaceData.result_counts.filtered_records}</strong>
            <span>filtered records</span>
            <strong>{isWorkspaceBlocked ? "—" : mapWorkspaceData.result_counts.map_pins}</strong>
            <span>markers</span>
          </div>
          <PreviewStateControl
            value={previewState}
            onChange={(value) => {
              setPreviewState(value);
              resetNestedDrawers();
            }}
          />
        </header>

        <ContextBar text={contextText} />

        {isWorkspaceInteractive && !layerNotice && !hasUserSelectedProperty && !isWorkflowGuidanceDismissed && (
          <WorkflowGuidance onDismiss={() => setIsWorkflowGuidanceDismissed(true)} />
        )}

        {previewState === "stale" && (
          <WorkspaceBanner
            title="Some intelligence may be stale."
            message="Review verification dates, stale warnings, and supporting evidence before relying on these records."
          />
        )}

        <section className="workspace-body" aria-label="Synchronized intelligence workspace">
          <FilterRail
            disabled={previewState === "loading" || previewState === "permissionDenied"}
            filters={workspaceFilters}
            onChange={(key, value) =>
              setWorkspaceFilters((current) => updateWorkspaceFilter(current, key, value))
            }
            onReset={() => setWorkspaceFilters(defaultWorkspaceFilters)}
          />

          <div className="workspace-main">
            <section className="map-plane" aria-label="Synthetic coordinate plane">
              <div className="map-context">
                <span>{selectedPinLabel}</span>
                <span>{isWorkspaceInteractive ? formatLabel(selectedRow.verification_status) : workspaceNotice.badge}</span>
              </div>
              <div className="grid-lines" aria-hidden="true" />
              {visiblePins.map((pin) => (
                <MapMarker
                  key={pin.id}
                  pin={pin}
                  pins={visiblePins}
                  isSelected={pin.id === selectedId}
                  layers={layers}
                  row={findSelectedRow(pin.id)}
                  onSelect={handleSelectProperty}
                />
              ))}
              {(!isWorkspaceInteractive || layerNotice || filterNotice) && <WorkspaceStateMessage notice={activeNotice} />}
            </section>

            <SynchronizedTable
              layers={layers}
              rows={visibleRows}
              selectedId={selectedId}
              disabled={!isWorkspaceInteractive || Boolean(layerNotice)}
              stateNotice={activeNotice}
              onReset={
                previewState === "noResults" || previewState === "error"
                  ? () => setPreviewState("content")
                  : filterNotice
                    ? () => setWorkspaceFilters(defaultWorkspaceFilters)
                    : layerNotice
                    ? () => setLayers(defaultLayers)
                    : undefined
              }
              onSelect={handleSelectProperty}
            />
          </div>

          <div className="workspace-side-rail" aria-label="Layers and Knowledge Summary">
            <LayerPanel
              disabled={!isWorkspaceInteractive}
              layers={layers}
              onChange={handleLayerChange}
            />
            <KnowledgeSummary
              layers={layers}
              actionRef={passportActionRef}
              passport={selectedPassport}
              selectedRow={selectedRow}
              hasPassport={Boolean(selectedPassport) && isWorkspaceInteractive && isSelectedVisible}
              disabled={!isWorkspaceInteractive || !isSelectedVisible}
              notice={selectionNotice}
              onOpenPassport={() => setIsPassportOpen(true)}
            />
          </div>
        </section>
      </main>

      {isPassportOpen && (
        <PassportDrawer
          closeButtonRef={passportCloseRef}
          correctionAudit={selectedCorrectionAudit}
          passport={selectedPassport}
          selectedRow={selectedRow}
          onClose={handleClosePassport}
          onOpenEvidence={(evidence) => {
            if (selectedPassport) {
              setSelectedAudit(null);
              setSelectedEvidence(
                previewState === "evidenceUnavailable"
                  ? buildEvidenceUnavailablePreview(evidence, selectedPassport)
                  : buildEvidencePreview(evidence, selectedPassport)
              );
            }
          }}
        />
      )}

      {isPassportOpen && selectedEvidence && (
        <EvidenceDrawer
          closeButtonRef={evidenceCloseRef}
          evidence={selectedEvidence}
          onClose={handleCloseEvidence}
          onOpenAudit={() =>
            setSelectedAudit(
              previewState === "auditUnavailable"
                ? buildAuditUnavailablePreview(selectedEvidence)
                : buildAuditPreview(selectedEvidence)
            )
          }
        />
      )}

      {isPassportOpen && selectedEvidence && selectedAudit && (
        <AuditDrawer audit={selectedAudit} closeButtonRef={auditCloseRef} onClose={handleCloseAudit} />
      )}
    </div>
  );
}

function PreviewStateControl({
  value,
  onChange
}: {
  value: WorkspacePreviewState;
  onChange: (value: WorkspacePreviewState) => void;
}) {
  return (
    <label className="preview-state-control">
      <span>Internal state preview</span>
      <select
        aria-label="Preview state"
        value={value}
        onChange={(event) => onChange(event.target.value as WorkspacePreviewState)}
      >
        {workspaceStateOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function ContextBar({ text }: { text: string }) {
  return (
    <div className="context-bar" role="status" aria-live="polite" aria-label="Knowledge context">
      {text}
    </div>
  );
}

function WorkflowGuidance({ onDismiss }: { onDismiss: () => void }) {
  return (
    <section className="workflow-guidance" role="status" aria-label="First-time workflow guidance">
      <div>
        <strong>Select a property on the map or table to review verified institutional knowledge.</strong>
        <span>Map to property to Knowledge Summary to Passport to supporting evidence to review history.</span>
      </div>
      <button type="button" aria-label="Dismiss workflow guidance" onClick={onDismiss}>
        Dismiss
      </button>
    </section>
  );
}

function WorkspaceBanner({ title, message }: { title: string; message: string }) {
  return (
    <div className="workspace-banner" role="status">
      <strong>{title}</strong>
      <span>{message}</span>
    </div>
  );
}

function WorkspaceStateMessage({ notice }: { notice: WorkspaceNotice }) {
  return (
    <div className="workspace-state-message" role={notice.role}>
      <h2>{notice.title}</h2>
      <p>{notice.message}</p>
      {notice.detail && <p>{notice.detail}</p>}
    </div>
  );
}

function FilterRail({
  disabled,
  filters,
  onChange,
  onReset
}: {
  disabled: boolean;
  filters: WorkspaceFilters;
  onChange: <K extends keyof WorkspaceFilters>(key: K, value: WorkspaceFilters[K]) => void;
  onReset: () => void;
}) {
  const availableFilters = mapWorkspaceData.available_filters;
  const hasActiveFilters = hasActiveWorkspaceFilters(filters);

  return (
    <aside className="filter-rail" aria-label="Filter rail">
      <div>
        <p className="panel-label">Filters</p>
        <h2>Workspace scope</h2>
      </div>

      <label className="filter-control">
        <span>Search</span>
        <input
          type="search"
          value={filters.search}
          disabled={disabled}
          aria-label="Search properties"
          placeholder="Name, address, type, status"
          onChange={(event) => onChange("search", event.target.value)}
        />
      </label>

      <FilterSelect
        label="Property type"
        value={filters.propertyType}
        values={availableFilters.property_type}
        disabled={disabled}
        onChange={(value) => onChange("propertyType", value)}
      />
      <FilterSelect
        label="Verification status"
        value={filters.verificationStatus}
        values={availableFilters.verification_status}
        disabled={disabled}
        onChange={(value) => onChange("verificationStatus", value)}
      />
      <FilterSelect
        label="Supporting evidence"
        value={filters.evidenceAvailable}
        values={["available", "unavailable"]}
        disabled={disabled}
        onChange={(value) => onChange("evidenceAvailable", value as WorkspaceFilters["evidenceAvailable"])}
      />
      <FilterSelect
        label="Review history"
        value={filters.auditActivity}
        values={["available", "unavailable"]}
        disabled={disabled}
        onChange={(value) => onChange("auditActivity", value as WorkspaceFilters["auditActivity"])}
      />
      <FilterSelect
        label="Record status"
        value={filters.recordStatus}
        values={availableFilters.status}
        disabled={disabled}
        onChange={(value) => onChange("recordStatus", value)}
      />

      <button type="button" className="filter-reset" disabled={disabled || !hasActiveFilters} onClick={onReset}>
        Reset filters
      </button>

      <p className="rail-note">Search and filters apply to this preview only. Layers remain separate map controls.</p>
    </aside>
  );
}

function FilterSelect({
  label,
  value,
  values,
  disabled,
  onChange
}: {
  label: string;
  value: string;
  values: Array<string | boolean>;
  disabled: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className={`filter-control ${disabled ? "disabled" : ""}`}>
      <span>{label}</span>
      <select
        value={value}
        disabled={disabled}
        aria-label={label}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">Any</option>
        {values.map((item) => (
          <option key={String(item)} value={String(item)}>
            {formatLabel(String(item))}
          </option>
        ))}
      </select>
    </label>
  );
}

function MapMarker({
  pin,
  pins,
  isSelected,
  layers,
  row,
  onSelect
}: {
  pin: MapPin;
  pins: MapPin[];
  isSelected: boolean;
  layers: LayerState;
  row: TableRow;
  onSelect: (id: string) => void;
}) {
  const position = coordinatePlanePosition(pin, pins);

  return (
    <button
      type="button"
      className={`map-marker ${isSelected ? "selected" : ""}`}
      style={position}
      aria-pressed={isSelected}
      aria-label={`Select ${pin.display_label}`}
      onClick={() => onSelect(pin.id)}
    >
      <span>{pin.display_label}</span>
      <LayerMarkerDetail row={row} layers={layers} />
    </button>
  );
}

function SynchronizedTable({
  layers,
  rows,
  selectedId,
  disabled,
  stateNotice,
  onReset,
  onSelect
}: {
  layers: LayerState;
  rows: TableRow[];
  selectedId: string;
  disabled: boolean;
  stateNotice: WorkspaceNotice;
  onReset?: () => void;
  onSelect: (id: string) => void;
}) {
  function handleRowKeyDown(event: KeyboardEvent<HTMLTableRowElement>, id: string) {
    if (disabled || (event.key !== "Enter" && event.key !== " ")) {
      return;
    }

    event.preventDefault();
    onSelect(id);
  }

  return (
    <section className="table-panel" aria-label="Synchronized assignments and intelligence table">
      <div className="table-header">
        <p className="panel-label">Assignments / intelligence</p>
        <span>{rows.length} rows</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Property</th>
            <th>Type</th>
            <th>Status</th>
            <th>Verification</th>
          </tr>
        </thead>
        <tbody>
          {rows.length > 0 ? (
            rows.map((row) => (
            <tr
              key={row.id}
              className={row.id === selectedId ? "selected-row" : ""}
              aria-selected={row.id === selectedId}
              tabIndex={disabled ? -1 : 0}
              onClick={() => {
                if (!disabled) {
                  onSelect(row.id);
                }
              }}
              onKeyDown={(event) => handleRowKeyDown(event, row.id)}
            >
              <td>
                <button type="button" disabled={disabled} onClick={() => onSelect(row.id)}>
                  {row.display_label}
                </button>
                <span>{row.address}</span>
                <LayerBadges row={row} layers={layers} />
              </td>
              <td>{formatLabel(row.record_type)}</td>
              <td>{formatLabel(row.status)}</td>
              <td>{formatLabel(row.verification_status)}</td>
            </tr>
            ))
          ) : (
            <tr>
              <td colSpan={4}>
                <div className="table-state">
                  <strong>{stateNotice.title}</strong>
                  <span>{stateNotice.message}</span>
                  {onReset && (
                    <button type="button" onClick={onReset}>
                      {stateNotice.badge === "Layer filtered"
                        ? "Reset layers"
                        : stateNotice.badge === "Filtered"
                          ? "Reset filters"
                          : "Reset preview state"}
                    </button>
                  )}
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}

function KnowledgeSummary({
  layers,
  actionRef,
  passport,
  selectedRow,
  hasPassport,
  disabled,
  notice,
  onOpenPassport
}: {
  layers: LayerState;
  actionRef: RefObject<HTMLButtonElement | null>;
  passport: PassportPreview | null;
  selectedRow: TableRow;
  hasPassport: boolean;
  disabled: boolean;
  notice: WorkspaceNotice;
  onOpenPassport: () => void;
}) {
  const verifiedFactCount = getVerifiedFactCount(passport);
  const evidenceCount = getEvidenceCount(selectedRow, passport);
  const auditActivityCount = getAuditActivityCount(selectedRow, passport);
  const trustSentence = getKnowledgeTrustSentence(selectedRow, passport);

  return (
    <aside className="selected-summary knowledge-summary" aria-label="Knowledge Summary">
      <p className="panel-label">Knowledge Summary</p>
      <h2>{disabled ? "Selection unavailable" : selectedRow.display_label}</h2>
      <p className="summary-address">
        {disabled ? notice.message : `${selectedRow.address}, ${selectedRow.city}, ${selectedRow.state}`}
      </p>
      {!disabled && <p className="trust-sentence">{trustSentence}</p>}
      <dl className="knowledge-metrics">
        <div>
          <dt>Property use</dt>
          <dd>{disabled ? notice.badge : formatLabel(selectedRow.property_type)}</dd>
        </div>
        <div>
          <dt>Trust status</dt>
          <dd>{disabled ? "Unavailable" : formatLabel(selectedRow.verification_status)}</dd>
        </div>
        <div>
          <dt>Verified facts</dt>
          <dd>{disabled ? "Unavailable" : verifiedFactCount}</dd>
        </div>
        <div>
          <dt>Supporting evidence</dt>
          <dd>{disabled ? "Unavailable" : evidenceCount}</dd>
        </div>
        <div>
          <dt>Review history</dt>
          <dd>{disabled ? "Unavailable" : auditActivityCount > 0 ? "Review history available" : "Not in preview"}</dd>
        </div>
        <div>
          <dt>Last review</dt>
          <dd>{disabled ? "Unavailable" : getLastReviewLabel(passport)}</dd>
        </div>
      </dl>
      {!disabled && <LayerBadges row={selectedRow} layers={layers} />}
      <p className="confidence-copy">{disabled ? notice.detail : selectedRow.confidence_summary}</p>
      {!disabled && (
        <p className="summary-next-step">Open the Passport to review verified facts, supporting evidence, and review history.</p>
      )}
      <button
        ref={actionRef}
        type="button"
        className="passport-action"
        disabled={!hasPassport}
        aria-describedby={!hasPassport ? "passport-unavailable-reason" : undefined}
        onClick={onOpenPassport}
      >
        Open Passport
      </button>
      {!hasPassport && (
        <p id="passport-unavailable-reason" className="summary-note">
          No Passport is available for this selected property in the preview records.
        </p>
      )}
      <p className="summary-note">This preview uses approved synthetic records only. It does not select comps or make conclusions.</p>
    </aside>
  );
}

function LayerPanel({
  disabled,
  layers,
  onChange
}: {
  disabled: boolean;
  layers: LayerState;
  onChange: (layer: LayerKey, value: boolean) => void;
}) {
  const activeLayers: Array<{ key: LayerKey; label: string; note: string }> = [
    { key: "subjects", label: "Subjects", note: "Show preview properties on the map and table." },
    { key: "verifiedKnowledge", label: "Verified Knowledge", note: "Show verification details when available." },
    { key: "reports", label: "Reports", note: "Show report and Passport indicators." },
    { key: "evidenceAvailable", label: "Supporting Evidence", note: "Show supporting evidence indicators." },
    { key: "auditActivity", label: "Review History", note: "Show review history indicators when present." }
  ];

  return (
    <aside className="layer-panel" aria-label="Layer panel">
      <div>
        <p className="panel-label">Layers</p>
        <h2>Workspace layers</h2>
      </div>
      <div className="layer-toggle-list">
        {activeLayers.map((layer) => (
          <label key={layer.key} className={`layer-toggle ${disabled ? "disabled" : ""}`}>
            <input
              type="checkbox"
              checked={layers[layer.key]}
              disabled={disabled}
              aria-describedby={`${layer.key}-layer-note`}
              onChange={(event) => onChange(layer.key, event.target.checked)}
            />
            <span>
              <strong>{layer.label}</strong>
              <em id={`${layer.key}-layer-note`}>{layer.note}</em>
            </span>
          </label>
        ))}
      </div>
      <div className="future-layer-list" aria-label="Future deferred layers">
        <p className="panel-label">Deferred</p>
        {futureLayers.map((layer) => (
          <label key={layer} className="future-layer">
            <input type="checkbox" disabled />
            <span>{layer}</span>
          </label>
        ))}
      </div>
    </aside>
  );
}

function LayerMarkerDetail({ row, layers }: { row: TableRow; layers: LayerState }) {
  const details = getLayerBadges(row, layers);

  if (details.length === 0) {
    return null;
  }

  return <small>{details[0]}</small>;
}

function LayerBadges({ row, layers }: { row: TableRow; layers: LayerState }) {
  const badges = getLayerBadges(row, layers);

  if (badges.length === 0) {
    return <span className="layer-badge muted">Layer details hidden</span>;
  }

  return (
    <div className="layer-badges" aria-label={`${row.display_label} layer badges`}>
      {badges.map((badge) => (
        <span key={badge} className="layer-badge">
          {badge}
        </span>
      ))}
    </div>
  );
}

function getLayerBadges(row: TableRow, layers: LayerState) {
  const badges: string[] = [];

  if (layers.verifiedKnowledge && row.verification_status === "verified") {
    badges.push("Verified knowledge");
  }

  if (layers.reports && row.passport_id) {
    badges.push("Report context");
  }

  if (layers.evidenceAvailable && row.evidence_link_count > 0) {
    badges.push("Supporting evidence available");
  }

  if (layers.auditActivity && rowHasAuditActivity(row)) {
    badges.push("Review history available");
  }

  return badges;
}

function PassportDrawer({
  closeButtonRef,
  correctionAudit,
  passport,
  selectedRow,
  onClose,
  onOpenEvidence
}: {
  closeButtonRef: RefObject<HTMLButtonElement | null>;
  correctionAudit: CorrectionAuditPreview | null;
  passport: PassportPreview | null;
  selectedRow: TableRow;
  onClose: () => void;
  onOpenEvidence: (evidence: EvidenceLink) => void;
}) {
  return (
    <aside
      className="passport-drawer"
      role="dialog"
      aria-modal="false"
      aria-labelledby="passport-drawer-title"
      aria-describedby="passport-drawer-description"
    >
      <div className="drawer-header">
        <div>
          <p className="eyebrow">Passport</p>
          <h2 id="passport-drawer-title">{selectedRow.display_label}</h2>
          <p id="passport-drawer-description">
            {selectedRow.address}, {selectedRow.city}, {selectedRow.state}
          </p>
        </div>
        <button
          ref={closeButtonRef}
          type="button"
          className="drawer-close"
          aria-label="Close Passport"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      {passport ? (
        <div className="drawer-content">
          <section className="drawer-section" aria-label="Passport identity">
            <h3>Identity</h3>
            <DefinitionRows
              rows={[
                { label: "Property", value: selectedRow.display_label },
                { label: "Address", value: `${selectedRow.address}, ${selectedRow.city}, ${selectedRow.state}` },
                { label: "Property use", value: formatLabel(selectedRow.property_type) },
                { label: "Record type", value: formatLabel(selectedRow.record_type) },
                { label: "Passport", value: passport.identity.passportId },
                { label: "Assignment", value: passport.identity.assignmentId },
                { label: "Tenant", value: passport.identity.tenantId }
              ]}
            />
          </section>

          <section className="drawer-section" aria-label="Verified Knowledge">
            <h3>Verified Knowledge</h3>
            <p className="guidance-hint">This section summarizes what Falcon Intelligence knows about the selected property.</p>
            <p className="fact-label">{passport.factLabel}</p>
            <p className="fact-value">{passport.factValue}</p>
            <div className="status-row">
              <span>{formatLabel(passport.factType)}</span>
              <span>{formatLabel(passport.review.verificationStatus)}</span>
              <span>{formatLabel(passport.searchableStatus)}</span>
            </div>
            <p className="confidence-copy">{passport.confidenceSummary}</p>
            <DefinitionRows
              rows={Object.entries(passport.confidenceDimensions).map(([label, value]) => ({
                label: formatLabel(label),
                value: formatLabel(value)
              }))}
              emptyText="Detailed confidence notes are not available for this preview record."
            />
          </section>

          <CorrectionHistoryPanel correctionAudit={correctionAudit} />

          <section className="drawer-section" aria-label="Supporting Evidence">
            <h3>Supporting Evidence</h3>
            <p className="guidance-hint">Supporting evidence explains why this knowledge can be reviewed and trusted.</p>
            {passport.evidenceLinks.length > 0 ? (
              <ul className="evidence-list">
                {passport.evidenceLinks.map((evidence) => (
                  <li key={evidence.evidence_id}>
                    <strong>{evidence.display_label}</strong>
                    <span>
                      {formatLabel(evidence.source_document_type)} · {formatLabel(evidence.access_level)} ·{" "}
                      {formatLabel(evidence.status)}
                    </span>
                    <button type="button" onClick={() => onOpenEvidence(evidence)}>
                      View supporting evidence
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="summary-note">No supporting evidence is available for this preview record.</p>
            )}
            <p className="summary-note">Supporting evidence is metadata-only in this preview. Source documents are not shown.</p>
          </section>

          <section className="drawer-section" aria-label="Verification and review">
            <h3>Verification / Review</h3>
            <DefinitionRows
              rows={[
                { label: "Verification status", value: formatLabel(passport.review.verificationStatus) },
                { label: "Verified by", value: passport.review.verifiedBy },
                { label: "Verified at", value: passport.review.verifiedAt },
                { label: "Reviewed by", value: passport.review.reviewedBy },
                { label: "Reviewed at", value: passport.review.reviewedAt },
                { label: "Review events", value: String(passport.auditEventIds.length) }
              ]}
            />
          </section>

          <section className="drawer-section" aria-label="Related Work">
            <h3>Related Work</h3>
            <DefinitionRows rows={passport.relatedContext} />
          </section>

          {passport.warnings.map((warning) => (
            <p key={warning} className="drawer-warning">
              {warning}
            </p>
          ))}
        </div>
      ) : (
        <div className="drawer-content">
          <section className="drawer-section">
            <h3>Passport unavailable</h3>
            <p className="confidence-copy">
              This selected property does not have a Passport in the current preview records.
            </p>
          </section>
        </div>
      )}
    </aside>
  );
}

function CorrectionHistoryPanel({ correctionAudit }: { correctionAudit: CorrectionAuditPreview | null }) {
  if (!correctionAudit) {
    return (
      <section className="drawer-section" aria-label="Field History">
        <h3>Field History</h3>
        <p className="summary-note">No Correction history is attached to this preview field.</p>
      </section>
    );
  }

  return (
    <section className="drawer-section correction-history" aria-label="Field History">
      <div className="section-heading-row">
        <h3>Field History</h3>
        <span>{correctionAudit.reviewStatus}</span>
      </div>
      <p className="guidance-hint">
        Correction history preserves the Prior Value, Current Value, Supporting Evidence, and Confidence change.
      </p>
      <p className="fact-label">Correction</p>
      <p className="fact-value">
        {correctionAudit.fieldLabel} was reviewed by {correctionAudit.actor}. Current Value is{" "}
        {correctionAudit.correctedValue}.
      </p>
      <DefinitionRows
        rows={[
          { label: "Field", value: correctionAudit.fieldKey },
          { label: "Prior Value", value: correctionAudit.originalValue },
          { label: "Current Value", value: correctionAudit.correctedValue },
          { label: "Original actor", value: correctionAudit.originalActor },
          { label: "Correction actor", value: correctionAudit.actor },
          { label: "Timestamp", value: formatAuditTimestamp(correctionAudit.timestamp) },
          { label: "Reason", value: correctionAudit.reason },
          { label: "Supporting Evidence", value: correctionAudit.supportingEvidence },
          {
            label: "Confidence",
            value: `${correctionAudit.confidenceBefore}% to ${correctionAudit.confidenceAfter}%`
          },
          { label: "Status", value: correctionAudit.reviewStatus }
        ]}
      />
      <ol className="audit-list compact-audit-list" aria-label="Correction audit event history">
        {correctionAudit.events.map((event) => (
          <li key={`${event.actor}-${event.timestamp}-${event.event}`}>
            <div className="audit-event-line">
              <span>Actor</span>
              <strong>{event.actor}</strong>
            </div>
            <div className="audit-event-line">
              <span>Action</span>
              <strong>{event.event}</strong>
            </div>
            <div className="audit-result">
              <span>Timestamp</span>
              <strong>{formatAuditTimestamp(event.timestamp)}</strong>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

function EvidenceDrawer({
  closeButtonRef,
  evidence,
  onClose,
  onOpenAudit
}: {
  closeButtonRef: RefObject<HTMLButtonElement | null>;
  evidence: EvidencePreview;
  onClose: () => void;
  onOpenAudit: () => void;
}) {
  return (
    <aside
      className="evidence-drawer"
      role="dialog"
      aria-modal="false"
      aria-labelledby="evidence-drawer-title"
      aria-describedby="evidence-drawer-description"
    >
      <div className="drawer-header">
        <div>
          <p className="eyebrow">Supporting evidence</p>
          <h2 id="evidence-drawer-title">{evidence.title}</h2>
          <p id="evidence-drawer-description">{evidence.unavailableMessage}</p>
        </div>
        <button
          ref={closeButtonRef}
          type="button"
          className="drawer-close"
          aria-label="Close supporting evidence"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      <div className="drawer-content">
        <section className="drawer-section" aria-label="Evidence summary">
          <h3>Evidence summary</h3>
          <p className="fact-label">{evidence.title}</p>
          <p className="fact-value">This supporting record explains the selected knowledge item.</p>
          <DefinitionRows
            rows={[
              { label: "Source/report", value: evidence.sourceDocumentId },
              { label: "Type", value: evidence.sourceDocumentType },
              { label: "Open status", value: evidence.openStatus }
            ]}
          />
        </section>

        <section className="drawer-section" aria-label="Source information">
          <h3>Source information</h3>
          <DefinitionRows
            rows={[
              { label: "Supporting evidence", value: evidence.evidenceId },
              { label: "Passport", value: evidence.passportId },
              { label: "Source/report", value: evidence.sourceDocumentId },
              { label: "Open status", value: evidence.openStatus }
            ]}
          />
          <DefinitionRows rows={evidence.provenanceRows} />
        </section>

        <section className="drawer-section" aria-label="Trust Context">
          <h3>Trust Context</h3>
          <p className="confidence-copy">{evidence.confidenceContext}</p>
          <p className="summary-note">
            This drawer explains why the supporting record exists. It does not display source files, extracted text, OCR, or
            document previews.
          </p>
        </section>

        <section className="drawer-section" aria-label="Review history handoff">
          <h3>Review history</h3>
          <p className="guidance-hint">Review history shows who reviewed or verified this record.</p>
          <DefinitionRows
            rows={[
              { label: "Available", value: evidence.auditHandoff.isAvailable ? "Yes" : "No" },
              { label: "Event", value: evidence.auditHandoff.eventCode }
            ]}
          />
          <p className="summary-note">{evidence.auditHandoff.message}</p>
          <button
            type="button"
            className="drawer-action"
            disabled={!evidence.auditHandoff.isAvailable}
            onClick={onOpenAudit}
          >
            View review history
          </button>
        </section>

        <p className="drawer-warning">
          Supporting evidence is metadata-only in this preview. Opening source reports remains outside the approved workspace scope.
        </p>
      </div>
    </aside>
  );
}

function formatAuditTimestamp(timestamp: string) {
  const parsed = Date.parse(timestamp);
  if (Number.isNaN(parsed)) {
    return timestamp || "Not available";
  }

  return new Intl.DateTimeFormat("en-US", {
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    month: "long",
    timeZone: "UTC",
    timeZoneName: "short",
    year: "numeric"
  }).format(new Date(parsed));
}

function getAuditCurrentStatus(audit: AuditPreview) {
  const lastEvent = audit.events[audit.events.length - 1];

  return {
    additionalHistory: audit.events.length > 0 ? "Review events available" : "No additional review history in preview",
    lastActivity: lastEvent ? formatAuditTimestamp(lastEvent.timestamp) : "Not available in the preview records",
    verificationState: lastEvent?.verificationStatus ?? "Unavailable"
  };
}

function AuditDrawer({
  audit,
  closeButtonRef,
  onClose
}: {
  audit: AuditPreview;
  closeButtonRef: RefObject<HTMLButtonElement | null>;
  onClose: () => void;
}) {
  return (
    <aside
      className="audit-drawer"
      role="dialog"
      aria-modal="false"
      aria-labelledby="audit-drawer-title"
      aria-describedby="audit-drawer-description"
    >
      <div className="drawer-header">
        <div>
          <p className="eyebrow">Review history</p>
          <h2 id="audit-drawer-title">{audit.title}</h2>
          <p id="audit-drawer-description">{audit.message}</p>
        </div>
        <button
          ref={closeButtonRef}
          type="button"
          className="drawer-close"
          aria-label="Close review history"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      <div className="drawer-content">
        <section className="drawer-section" aria-label="Review summary">
          <h3>Review summary</h3>
          <p className="fact-value">This review history records how this knowledge was reviewed and verified.</p>
          <DefinitionRows
            rows={[
              { label: "Review events", value: String(audit.events.length) },
              { label: "Current verification status", value: getAuditCurrentStatus(audit).verificationState },
              { label: "History available", value: getAuditCurrentStatus(audit).additionalHistory }
            ]}
          />
        </section>

        <section className="drawer-section timeline-section" aria-label="Review events">
          <h3>Review events</h3>
          {audit.events.length > 0 ? (
            <ol className="audit-list">
              {audit.events.map((event) => (
                <li key={`${event.eventCode}-${event.matchId}-${event.summary}`}>
                  <div className="audit-event-line">
                    <span>Actor</span>
                    <strong>{event.actor}</strong>
                  </div>
                  <div className="audit-event-line">
                    <span>Action</span>
                    <strong>{event.summary}</strong>
                  </div>
                  <div className="audit-event-line">
                    <span>Timestamp</span>
                    <strong>{formatAuditTimestamp(event.timestamp)}</strong>
                  </div>
                  <div className="audit-result">
                    <span>Status</span>
                    <strong>{event.verificationStatus}</strong>
                  </div>
                </li>
              ))}
            </ol>
          ) : (
            <p className="confidence-copy">
              Review history is unavailable for this supporting evidence in the current preview records.
            </p>
          )}
        </section>

        <section className="drawer-section" aria-label="Current review status">
          <h3>Current review status</h3>
          <DefinitionRows
            rows={[
              { label: "Current verification state", value: getAuditCurrentStatus(audit).verificationState },
              { label: "Last activity", value: getAuditCurrentStatus(audit).lastActivity },
              { label: "Additional review history", value: getAuditCurrentStatus(audit).additionalHistory }
            ]}
          />
          <DefinitionRows rows={audit.contextRows} />
        </section>

        <p className="drawer-warning">
          Review history uses committed synthetic event snapshots only. It is not production review history.
        </p>
      </div>
    </aside>
  );
}

function DefinitionRows({
  rows,
  emptyText
}: {
  rows: Array<{ label: string; value: string }>;
  emptyText?: string;
}) {
  if (rows.length === 0) {
    return <p className="summary-note">{emptyText ?? "No preview detail is available."}</p>;
  }

  return (
    <dl className="definition-list">
      {rows.map((row) => (
        <div key={`${row.label}-${row.value}`}>
          <dt>{row.label}</dt>
          <dd>{row.value}</dd>
        </div>
      ))}
    </dl>
  );
}
