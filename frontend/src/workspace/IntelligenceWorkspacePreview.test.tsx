import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { IntelligenceWorkspacePreview } from "./IntelligenceWorkspacePreview";

describe("IntelligenceWorkspacePreview", () => {
  async function setPreviewState(user: ReturnType<typeof userEvent.setup>, label: string) {
    await user.selectOptions(screen.getByLabelText("Preview state"), label);
  }

  it("renders the workspace, markers, and synchronized table rows", () => {
    render(<IntelligenceWorkspacePreview />);

    expect(screen.getByRole("heading", { name: "Map Workspace" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Current subject/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Verified industrial sale comp/i })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    expect(screen.getByRole("row", { name: /Verified industrial sale comp/i })).toHaveAttribute(
      "aria-selected",
      "true"
    );
  });

  it("renders default workspace context", () => {
    render(<IntelligenceWorkspacePreview />);

    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Falcon Intelligence Preview • 8 visible properties • Verified property knowledge preview"
    );
    expect(screen.getByRole("status", { name: "Knowledge context" })).toBeInTheDocument();
    expect(screen.getByRole("complementary", { name: "Knowledge Summary" })).toBeInTheDocument();
    expect(screen.getByText("Knowledge Summary")).toBeInTheDocument();
  });

  it("renders first-time workflow guidance before a property is explicitly selected", () => {
    render(<IntelligenceWorkspacePreview />);

    const guidance = screen.getByRole("status", { name: "First-time workflow guidance" });
    expect(within(guidance).getByText("Select a property on the map or table to review verified institutional knowledge."))
      .toBeInTheDocument();
    expect(within(guidance).getByText("Map to property to Knowledge Summary to Passport to supporting evidence to review history."))
      .toBeInTheDocument();
  });

  it("dismisses first-time workflow guidance for the current preview session", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: "Dismiss workflow guidance" }));

    expect(screen.queryByRole("status", { name: "First-time workflow guidance" })).not.toBeInTheDocument();
  });

  it("renders the preview layer panel with active and deferred layers", () => {
    render(<IntelligenceWorkspacePreview />);

    const layerPanel = screen.getByRole("complementary", { name: "Layer panel" });
    expect(within(layerPanel).getByRole("checkbox", { name: /Subjects/i })).toBeChecked();
    expect(within(layerPanel).getByRole("checkbox", { name: /Verified Knowledge/i })).toBeChecked();
    expect(within(layerPanel).getByRole("checkbox", { name: /Reports/i })).toBeChecked();
    expect(within(layerPanel).getByRole("checkbox", { name: /Supporting Evidence/i })).toBeChecked();
    expect(within(layerPanel).getByRole("checkbox", { name: /Review History/i })).toBeChecked();
    expect(within(layerPanel).getByRole("checkbox", { name: /AI Suggestions/i })).toBeDisabled();
    expect(screen.getByRole("row", { name: /Unverified retail lead/i })).toBeInTheDocument();
    expect(screen.getByRole("row", { name: /Historical office sale comp/i })).toBeInTheDocument();
  });

  it("toggles Subjects to hide and restore visible markers and table rows", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("checkbox", { name: /Subjects/i }));

    expect(screen.queryByRole("button", { name: /Select Current subject/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("row", { name: /Verified industrial sale comp/i })).not.toBeInTheDocument();
    expect(screen.getAllByText("No properties match the active layers.").length).toBeGreaterThan(1);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "No properties match the active layers. • 0 visible properties • Adjust layers to restore map context"
    );

    await user.click(screen.getByRole("button", { name: "Reset layers" }));

    expect(screen.getByRole("button", { name: /Select Current subject/i })).toBeInTheDocument();
    expect(screen.getByRole("row", { name: /Verified industrial sale comp/i })).toBeInTheDocument();
  });

  it("toggles a derived layer to update visible badges without filtering records", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    expect(screen.getAllByText("Verified knowledge").length).toBeGreaterThan(0);

    await user.click(screen.getByRole("checkbox", { name: /Verified Knowledge/i }));

    expect(screen.queryByText("Verified knowledge")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Current subject/i })).toBeInTheDocument();
    expect(screen.getByRole("row", { name: /Verified industrial sale comp/i })).toBeInTheDocument();
  });

  it("searches local synthetic records to find the airport warehouse", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.type(screen.getByRole("searchbox", { name: "Search properties" }), "airport");

    expect(screen.getByRole("row", { name: /Airport warehouse/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Airport warehouse/i })).toBeInTheDocument();
    expect(screen.queryByRole("row", { name: /Verified industrial sale comp/i })).not.toBeInTheDocument();
    expect(screen.getByRole("complementary", { name: "Knowledge Summary" })).toHaveTextContent(
      "The selected property is hidden by the current local search or filters."
    );
  });

  it("filters visible markers and rows with local workspace filters", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.selectOptions(screen.getByLabelText("Property type"), "retail");
    await user.selectOptions(screen.getByLabelText("Verification status"), "unverified");
    await user.selectOptions(screen.getByLabelText("Supporting evidence"), "unavailable");
    await user.selectOptions(screen.getByLabelText("Record status"), "active");

    expect(screen.getByRole("row", { name: /Unverified retail lead/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Unverified retail lead/i })).toBeInTheDocument();
    expect(screen.queryByRole("row", { name: /Airport warehouse/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Select Airport warehouse/i })).not.toBeInTheDocument();
  });

  it("resets local filters to restore visible records", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.type(screen.getByRole("searchbox", { name: "Search properties" }), "airport");
    expect(screen.queryByRole("row", { name: /Current subject/i })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Reset filters" }));

    expect(screen.getByRole("row", { name: /Current subject/i })).toBeInTheDocument();
    expect(screen.getByRole("row", { name: /Unverified retail lead/i })).toBeInTheDocument();
    expect(screen.getByRole("row", { name: /Historical office sale comp/i })).toBeInTheDocument();
  });

  it("shows a calm unavailable summary when filters hide the selected property", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Airport warehouse/i }));
    await user.selectOptions(screen.getByLabelText("Property type"), "office");

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Selection unavailable" })).toBeInTheDocument();
    expect(within(summary).getByText("The selected property is hidden by the current local search or filters."))
      .toBeInTheDocument();
    expect(within(summary).getByRole("button", { name: "Open Passport" })).toBeDisabled();
  });

  it("shows a calm unavailable summary when the selected property is hidden by layers", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("checkbox", { name: /Subjects/i }));

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Selection unavailable" })).toBeInTheDocument();
    expect(within(summary).getByText("The selected property is hidden by the current layers."))
      .toBeInTheDocument();
    expect(within(summary).getByRole("button", { name: "Open Passport" })).toBeDisabled();
    expect(screen.queryByRole("dialog", { name: "Current subject" })).not.toBeInTheDocument();
  });

  it("selects a table row when its marker is clicked and updates the Knowledge Summary", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Completed logistics assignment/i }));

    expect(screen.getByRole("button", { name: /Select Completed logistics assignment/i })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    expect(screen.getByRole("row", { name: /Completed logistics assignment/i })).toHaveAttribute(
      "aria-selected",
      "true"
    );

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Completed logistics assignment" })).toBeInTheDocument();
    expect(within(summary).getByText(/1200 Example Logistics Loop/i)).toBeInTheDocument();
    expect(within(summary).getByText("This property contains verified institutional knowledge with supporting evidence available."))
      .toBeInTheDocument();
    expect(screen.queryByRole("status", { name: "First-time workflow guidance" })).not.toBeInTheDocument();
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Completed logistics assignment • Knowledge Summary • Verified property • 1 evidence item"
    );
  });

  it("selects a marker from keyboard focus", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    const marker = screen.getByRole("button", { name: /Select Completed logistics assignment/i });
    marker.focus();
    await user.keyboard("{Enter}");

    expect(marker).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Completed logistics assignment/i })).toHaveAttribute(
      "aria-selected",
      "true"
    );
  });

  it("selects a marker when its table row is clicked and updates the Knowledge Summary", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: "Verified industrial lease comp" }));

    expect(screen.getByRole("button", { name: /Select Verified industrial lease comp/i })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    expect(screen.getByRole("row", { name: /Verified industrial lease comp/i })).toHaveAttribute(
      "aria-selected",
      "true"
    );

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Verified industrial lease comp" })).toBeInTheDocument();
    expect(within(summary).getByText(/1400 Example Loading Court/i)).toBeInTheDocument();
    expect(screen.queryByRole("status", { name: "First-time workflow guidance" })).not.toBeInTheDocument();
  });

  it("shows verified facts, evidence, audit, and next-step indicators in the Knowledge Summary", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByText("Trust status")).toBeInTheDocument();
    expect(within(summary).getByText("Verified facts")).toBeInTheDocument();
    expect(within(summary).getByText("Supporting evidence")).toBeInTheDocument();
    expect(within(summary).getByText("Review history")).toBeInTheDocument();
    expect(within(summary).getAllByText("Review history available")[0]).toBeInTheDocument();
    expect(within(summary).getByText("Last review")).toBeInTheDocument();
    expect(within(summary).getByText("Open the Passport to review verified facts, supporting evidence, and review history."))
      .toBeInTheDocument();
  });

  it("supports the airport warehouse demo scenario through Knowledge Summary, Passport, Evidence, and Audit", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Airport warehouse/i }));

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Airport warehouse" })).toBeInTheDocument();
    expect(within(summary).getByText(/1750 Example Airport Cargo Road/i)).toBeInTheDocument();
    expect(within(summary).getByText(/building area record/i)).toBeInTheDocument();
    expect(within(summary).getAllByText("Review history available")[0]).toBeInTheDocument();
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Airport warehouse • Knowledge Summary • Verified property • 1 evidence item"
    );

    await user.click(screen.getByRole("button", { name: "Open Passport" }));

    const passport = screen.getByRole("dialog", { name: "Airport warehouse" });
    expect(within(passport).getByRole("heading", { name: "Verified Knowledge" })).toBeInTheDocument();
    expect(within(passport).getByText(/Industrial assignment metadata for 50,000 sf synthetic property/i))
      .toBeInTheDocument();

    await user.click(within(passport).getByRole("button", { name: "View supporting evidence" }));

    const evidence = screen.getByRole("dialog", { name: "Synthetic industrial assignment source metadata" });
    expect(within(evidence).getByRole("heading", { name: "Evidence summary" })).toBeInTheDocument();
    expect(within(evidence).getByText("This supporting record explains the selected knowledge item.")).toBeInTheDocument();

    await user.click(within(evidence).getByRole("button", { name: "View review history" }));

    const audit = screen.getByRole("dialog", { name: /Review history for Synthetic industrial assignment/i });
    expect(within(audit).getByRole("heading", { name: "Review events" })).toBeInTheDocument();
    expect(within(audit).getByText(/Supporting evidence opened/i)).toBeInTheDocument();
  });

  it("selects a table row from keyboard focus", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    const row = screen.getByRole("row", { name: /Completed logistics assignment/i });
    row.focus();
    await user.keyboard(" ");

    expect(screen.getByRole("button", { name: /Select Completed logistics assignment/i })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    expect(row).toHaveAttribute("aria-selected", "true");
  });

  it("opens a passport drawer from the selected property without losing map and table context", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));

    const drawer = screen.getByRole("dialog", { name: "Current subject" });
    expect(within(drawer).getByRole("heading", { name: "Current subject" })).toBeInTheDocument();
    expect(within(drawer).getByRole("button", { name: "Close Passport" })).toHaveFocus();
    expect(within(drawer).getByText("synthetic-passport-assignment-industrial-alpha")).toBeInTheDocument();
    expect(within(drawer).getByText(/Synthetic industrial assignment summary/i)).toBeInTheDocument();
    expect(within(drawer).getByText(/Synthetic industrial assignment source metadata/i)).toBeInTheDocument();
    expect(within(drawer).getByText("Supporting evidence explains why this knowledge can be reviewed and trusted.")).toBeInTheDocument();

    expect(screen.getByRole("button", { name: /Select Current subject/i })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Current subject/i })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Current subject • Passport open • Synthetic industrial assignment summary"
    );
  });

  it("renders Passport information architecture sections with property context", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));

    const drawer = screen.getByRole("dialog", { name: "Current subject" });
    expect(within(drawer).getByRole("heading", { name: "Identity" })).toBeInTheDocument();
    expect(within(drawer).getByRole("heading", { name: "Verified Knowledge" })).toBeInTheDocument();
    expect(within(drawer).getByRole("heading", { name: "Supporting Evidence" })).toBeInTheDocument();
    expect(within(drawer).getByRole("heading", { name: "Verification / Review" })).toBeInTheDocument();
    expect(within(drawer).getByRole("heading", { name: "Related Work" })).toBeInTheDocument();
    const identity = within(drawer).getByLabelText("Passport identity");
    expect(within(identity).getByText("Property use")).toBeInTheDocument();
    expect(within(identity).getByText("Industrial")).toBeInTheDocument();
    expect(within(drawer).getByText("Verification status")).toBeInTheDocument();
    expect(within(drawer).getByText("Review events")).toBeInTheDocument();
    expect(within(drawer).getByText("This section summarizes what Falcon Intelligence knows about the selected property."))
      .toBeInTheDocument();
  });

  it("closes the passport drawer while preserving the selected property", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Completed logistics assignment/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "Close Passport" }));

    expect(screen.queryByRole("dialog", { name: "Completed logistics assignment" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Completed logistics assignment/i })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    expect(screen.getByRole("row", { name: /Completed logistics assignment/i })).toHaveAttribute(
      "aria-selected",
      "true"
    );

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Completed logistics assignment" })).toBeInTheDocument();
  });

  it("opens evidence from the passport drawer and preserves workspace context", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));

    const passport = screen.getByRole("dialog", { name: "Current subject" });
    const evidence = screen.getByRole("dialog", { name: "Synthetic industrial assignment source metadata" });
    expect(within(passport).getByRole("heading", { name: "Current subject" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: /Synthetic industrial assignment source metadata/i }))
      .toBeInTheDocument();
    expect(within(evidence).getByRole("button", { name: "Close supporting evidence" })).toHaveFocus();
    expect(within(evidence).getByRole("heading", { name: "Evidence summary" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: "Source information" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: "Trust Context" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: "Review history" })).toBeInTheDocument();
    expect(within(evidence).getByText("This supporting record explains the selected knowledge item.")).toBeInTheDocument();
    const sourceMetadata = within(evidence).getByLabelText("Source information");
    expect(within(sourceMetadata).getByText("synthetic-source-report-industrial-alpha")).toBeInTheDocument();
    expect(within(evidence).getByText(/This supporting evidence cannot open a source document/i)).toBeInTheDocument();
    expect(within(evidence).getByText(/Review history is available/i)).toBeInTheDocument();
    expect(within(evidence).getByText("Review history shows who reviewed or verified this record.")).toBeInTheDocument();
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Synthetic industrial assignment source metadata • Supporting evidence • Source: synthetic-source-report-industrial-alpha"
    );

    expect(screen.getByRole("button", { name: /Select Current subject/i })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Current subject/i })).toHaveAttribute("aria-selected", "true");

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Current subject" })).toBeInTheDocument();
  });

  it("closes evidence back to passport without losing selected property context", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));
    await user.click(screen.getByRole("button", { name: "Close supporting evidence" }));

    expect(screen.queryByRole("dialog", { name: "Synthetic industrial assignment source metadata" }))
      .not.toBeInTheDocument();
    expect(screen.getByRole("dialog", { name: "Current subject" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Current subject/i })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Current subject/i })).toHaveAttribute("aria-selected", "true");
  });

  it("opens audit from evidence and preserves every parent context", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));
    await user.click(screen.getByRole("button", { name: "View review history" }));

    const passport = screen.getByRole("dialog", { name: "Current subject" });
    const evidence = screen.getByRole("dialog", { name: "Synthetic industrial assignment source metadata" });
    const audit = screen.getByRole("dialog", { name: /Review history for Synthetic industrial assignment/i });

    expect(within(passport).getByRole("heading", { name: "Current subject" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: /Synthetic industrial assignment source metadata/i }))
      .toBeInTheDocument();
    expect(within(audit).getByRole("heading", { name: /Review history for Synthetic industrial assignment/i }))
      .toBeInTheDocument();
    expect(within(audit).getByRole("button", { name: "Close review history" })).toHaveFocus();
    expect(within(audit).getByRole("heading", { name: "Review summary" })).toBeInTheDocument();
    expect(within(audit).getByRole("heading", { name: "Review events" })).toBeInTheDocument();
    expect(within(audit).getByRole("heading", { name: "Current review status" })).toBeInTheDocument();
    expect(within(audit).getByText("This review history records how this knowledge was reviewed and verified."))
      .toBeInTheDocument();
    expect(within(audit).getAllByText("Review events").length).toBeGreaterThan(0);
    expect(within(audit).getByText("Current verification status")).toBeInTheDocument();
    expect(within(audit).getByText(/Supporting evidence opened/i)).toBeInTheDocument();
    expect(within(audit).getByText(/Passport opened/i)).toBeInTheDocument();
    expect(within(audit).getAllByText("Actor").length).toBeGreaterThan(0);
    expect(within(audit).getAllByText("Action").length).toBeGreaterThan(0);
    expect(within(audit).getAllByText("Timestamp").length).toBeGreaterThan(0);
    expect(within(audit).getAllByText("Status").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Review history for Synthetic industrial assignment source metadata • Review history • Accountability trail"
    );

    expect(screen.getByRole("button", { name: /Select Current subject/i })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Current subject/i })).toHaveAttribute("aria-selected", "true");

    const summary = screen.getByRole("complementary", { name: "Knowledge Summary" });
    expect(within(summary).getByRole("heading", { name: "Current subject" })).toBeInTheDocument();
  });

  it("renders audit events in existing chronological model order with actor, action, timestamp, and result", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));
    await user.click(screen.getByRole("button", { name: "View review history" }));

    const audit = screen.getByRole("dialog", { name: /Review history for Synthetic industrial assignment/i });
    const timeline = within(audit).getByLabelText("Review events");
    const events = within(timeline).getAllByRole("listitem");

    expect(events).toHaveLength(2);
    expect(events[0]).toHaveTextContent("user-synthetic-001");
    expect(events[0]).toHaveTextContent("Supporting evidence opened");
    expect(events[0]).toHaveTextContent("synthetic-dynamic-timestamp");
    expect(events[0]).toHaveTextContent("Placeholder");
    expect(events[1]).toHaveTextContent("Passport opened");
    expect(events[1]).toHaveTextContent("Searchable");
  });

  it("closes audit back to evidence without losing passport or selected property context", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));
    await user.click(screen.getByRole("button", { name: "View review history" }));
    await user.click(screen.getByRole("button", { name: "Close review history" }));

    expect(screen.queryByRole("dialog", { name: /Review history for Synthetic industrial assignment/i }))
      .not.toBeInTheDocument();
    expect(screen.getByRole("dialog", { name: "Synthetic industrial assignment source metadata" })).toBeInTheDocument();
    expect(screen.getByRole("dialog", { name: "Current subject" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Current subject/i })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Current subject/i })).toHaveAttribute("aria-selected", "true");
  });

  it("closing passport clears nested evidence and audit drawers safely", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));
    await user.click(screen.getByRole("button", { name: "View review history" }));
    await user.click(screen.getByRole("button", { name: "Close Passport" }));

    expect(screen.queryByRole("dialog", { name: /Review history for Synthetic industrial assignment/i }))
      .not.toBeInTheDocument();
    expect(screen.queryByRole("dialog", { name: "Synthetic industrial assignment source metadata" }))
      .not.toBeInTheDocument();
    expect(screen.queryByRole("dialog", { name: "Current subject" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Current subject/i })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Current subject/i })).toHaveAttribute("aria-selected", "true");
  });

  it("closes nested drawers with Escape from audit to evidence to passport", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));
    await user.click(screen.getByRole("button", { name: "View review history" }));

    await user.keyboard("{Escape}");

    expect(screen.queryByRole("dialog", { name: /Review history for Synthetic industrial assignment/i }))
      .not.toBeInTheDocument();
    expect(screen.getByRole("dialog", { name: "Synthetic industrial assignment source metadata" })).toBeInTheDocument();
    expect(screen.getByRole("dialog", { name: "Current subject" })).toBeInTheDocument();

    await user.keyboard("{Escape}");

    expect(screen.queryByRole("dialog", { name: "Synthetic industrial assignment source metadata" }))
      .not.toBeInTheDocument();
    expect(screen.getByRole("dialog", { name: "Current subject" })).toBeInTheDocument();

    await user.keyboard("{Escape}");

    expect(screen.queryByRole("dialog", { name: "Current subject" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Select Current subject/i })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("row", { name: /Current subject/i })).toHaveAttribute("aria-selected", "true");
  });

  it("renders the loading state without fake results", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "Loading");

    expect(screen.getAllByText("Loading workspace intelligence.").length).toBeGreaterThan(1);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Loading workspace intelligence. • Verified records, filters, and map locations are being prepared."
    );
    expect(screen.queryByRole("status", { name: "First-time workflow guidance" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Select Current subject/i })).not.toBeInTheDocument();
    expect(
      screen.getAllByText("No verified records, confidence values, or result totals are shown until data resolves.")
        .length
    ).toBeGreaterThan(1);
  });

  it("renders the empty state", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "Empty");

    expect(screen.getAllByText("No verified intelligence is available yet.").length).toBeGreaterThan(1);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "No verified intelligence is available yet. • No eligible preview assignments or verified facts are available to this workspace yet."
    );
    expect(screen.getAllByText(/Facts become searchable only after verification/i).length).toBeGreaterThan(1);
  });

  it("renders permission denied and disables workspace interaction", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "Permission denied");

    expect(screen.getAllByText("Falcon Intelligence is not available for your role.").length).toBeGreaterThan(1);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Falcon Intelligence is not available for your role. • Access to internal intelligence is controlled by firm policy."
    );
    expect(screen.queryByRole("button", { name: /Select Current subject/i })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open Passport" })).toBeDisabled();
  });

  it("renders stale warning while content remains visible", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "Stale data");

    expect(screen.getAllByText("Some intelligence may be stale.").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Falcon Intelligence Preview • Stale-data caution • Review provenance before relying on records"
    );
    expect(screen.getByRole("button", { name: /Select Current subject/i })).toBeInTheDocument();
    expect(screen.getByRole("row", { name: /Verified industrial sale comp/i })).toBeInTheDocument();
  });

  it("renders no-results state with reset behavior", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "No results");

    expect(screen.getAllByText("No properties match the current view.").length).toBeGreaterThan(1);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "No properties match the current view. • The current search and filters do not match any preview properties."
    );
    expect(screen.queryByRole("button", { name: /Select Current subject/i })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Reset preview state" }));

    expect(screen.getByRole("button", { name: /Select Current subject/i })).toBeInTheDocument();
  });

  it("renders evidence unavailable from the evidence drawer", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "Supporting evidence unavailable");
    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));

    const evidence = screen.getByRole("dialog", { name: "Synthetic industrial assignment source metadata" });
    expect(within(evidence).getByRole("heading", { name: "Evidence summary" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: "Source information" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: "Trust Context" })).toBeInTheDocument();
    expect(within(evidence).getByRole("heading", { name: "Review history" })).toBeInTheDocument();
    expect(within(evidence).getByText("This supporting evidence cannot be opened from the current workspace."))
      .toBeInTheDocument();
    expect(within(evidence).getByRole("button", { name: "View review history" })).toBeDisabled();
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Synthetic industrial assignment source metadata • Supporting evidence • Source: Unavailable from current workspace"
    );
  });

  it("renders audit unavailable from the audit drawer", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "Review history unavailable");
    await user.click(screen.getByRole("button", { name: /Select Current subject/i }));
    await user.click(screen.getByRole("button", { name: "Open Passport" }));
    await user.click(screen.getByRole("button", { name: "View supporting evidence" }));
    await user.click(screen.getByRole("button", { name: "View review history" }));

    const audit = screen.getByRole("dialog", { name: /Review history for Synthetic industrial assignment source metadata/i });
    expect(within(audit).getByText("Review history is not available in the current preview."))
      .toBeInTheDocument();
    expect(within(audit).getByRole("heading", { name: "Review summary" })).toBeInTheDocument();
    expect(within(audit).getByRole("heading", { name: "Review events" })).toBeInTheDocument();
    expect(within(audit).getByRole("heading", { name: "Current review status" })).toBeInTheDocument();
    expect(within(audit).getByText("Review history is unavailable for this supporting evidence in the current preview records."))
      .toBeInTheDocument();
    expect(within(audit).getAllByText("No additional review history in preview").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Review history for Synthetic industrial assignment source metadata • Review history • Accountability trail"
    );
  });

  it("renders the generic error state with reset behavior", async () => {
    const user = userEvent.setup();
    render(<IntelligenceWorkspacePreview />);

    await setPreviewState(user, "Error");

    expect(screen.getAllByText("Workspace intelligence is unavailable.").length).toBeGreaterThan(1);
    expect(screen.getByLabelText("Knowledge context")).toHaveTextContent(
      "Workspace intelligence is unavailable. • Falcon Intelligence could not load the preview records."
    );
    expect(screen.queryByText(/stack trace/i)).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Reset preview state" }));

    expect(screen.getByRole("button", { name: /Select Current subject/i })).toBeInTheDocument();
  });
});
