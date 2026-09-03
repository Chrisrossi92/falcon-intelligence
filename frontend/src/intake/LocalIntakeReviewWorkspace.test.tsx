import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { LocalIntakeReviewWorkspace } from "./LocalIntakeReviewWorkspace";


function candidateCard(label: string) {
  const heading = screen.getByRole("heading", { name: label });
  const card = heading.closest("article");
  if (!card) throw new Error(`Candidate card not found for ${label}`);
  return within(card);
}


describe("LocalIntakeReviewWorkspace", () => {
  it("renders the AIR-backed assignment overview and review progress", () => {
    render(<LocalIntakeReviewWorkspace />);

    expect(screen.getByRole("heading", { name: "Synthetic Northstar Distribution Center assignment" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Assignment overview" })).toBeInTheDocument();
    expect(screen.getByText("Example Regional Bank, N.A.", { selector: "dd" })).toBeInTheDocument();
    expect(screen.getByRole("progressbar", { name: "Candidate review progress" })).toHaveAttribute("max", "20");
    expect(screen.getByText("10 of 20 candidates reviewed")).toBeInTheDocument();
  });

  it("groups candidates by practical appraisal topic and shows provenance inline", () => {
    render(<LocalIntakeReviewWorkspace />);

    expect(screen.getByRole("heading", { name: "Client and intended users" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Important dates" })).toBeInTheDocument();
    const reportDate = candidateCard("Report date requirement");
    expect(reportDate.getByText("Synthetic Northstar Appraisal Report.pdf")).toBeInTheDocument();
    expect(reportDate.getByText(/Page 1/)).toBeInTheDocument();
    expect(reportDate.getByText(/deterministic label match/i)).toBeInTheDocument();
  });

  it("filters by review state and topic", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.selectOptions(screen.getByLabelText("Review state"), "deferred");
    expect(screen.getByRole("heading", { name: "Report date requirement" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Property address" })).not.toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText("Topic"), "important_dates");
    expect(screen.getByRole("heading", { name: "Important dates" })).toBeInTheDocument();
  });

  it("accepts a candidate using AIR state language and advances progress", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.click(candidateCard("Extraordinary assumptions present").getByRole("button", { name: "Accept" }));

    expect(candidateCard("Extraordinary assumptions present").getByText("Accepted")).toBeInTheDocument();
    expect(screen.getByText("11 of 20 candidates reviewed")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("AIR review semantics");
  });

  it("requires and records a reason when correcting a candidate", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.click(candidateCard("Report title").getByRole("button", { name: "Correct" }));
    expect(screen.getByRole("dialog", { name: "Correct candidate" })).toBeInTheDocument();
    await user.type(screen.getByLabelText("Corrected value"), "Northstar Distribution Center Appraisal");
    await user.type(screen.getByLabelText("Reason"), "Title reconciled to the synthetic engagement.");
    await user.click(screen.getByRole("button", { name: "Save decision" }));

    expect(candidateCard("Report title").getByText("Corrected")).toBeInTheDocument();
    expect(candidateCard("Report title").getByText("Northstar Distribution Center Appraisal")).toBeInTheDocument();
    expect(candidateCard("Report title").getByText(/Original observation:/)).toBeInTheDocument();
    expect(candidateCard("Report title").getByText(/Title reconciled/)).toBeInTheDocument();
  });

  it("rejects without deleting the candidate and retains the reason", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    const card = candidateCard("Sales comparison approach referenced");
    await user.click(card.getByRole("button", { name: "Reject" }));
    await user.type(screen.getByLabelText("Reason"), "Approach reference is not an assignment fact.");
    await user.click(screen.getByRole("button", { name: "Save decision" }));

    expect(candidateCard("Sales comparison approach referenced").getByText("Rejected")).toBeInTheDocument();
    expect(candidateCard("Sales comparison approach referenced").getByText(/not an assignment fact/)).toBeInTheDocument();
  });

  it("defers a candidate without accepting or rejecting it", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.click(candidateCard("Income approach referenced").getByRole("button", { name: "Defer" }));

    expect(candidateCard("Income approach referenced").getByText("Deferred")).toBeInTheDocument();
    expect(candidateCard("Income approach referenced").queryByText("Accepted")).not.toBeInTheDocument();
  });

  it("expands detailed evidence without losing the candidate row", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    const card = candidateCard("Report date requirement");
    await user.click(card.getByRole("button", { name: /Evidence/ }));

    expect(card.getByText("Evidence ID")).toBeInTheDocument();
    expect(card.getByText(/evidence-/)).toBeInTheDocument();
    expect(card.getByRole("button", { name: "Hide evidence detail" })).toHaveAttribute("aria-expanded", "true");
  });

  it("resolves a conflict with a selected value and required reason", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);
    const conflicts = screen.getByRole("heading", { name: "Conflicts" }).closest("section");
    if (!conflicts) throw new Error("Conflict panel missing");

    await user.click(within(conflicts).getAllByRole("button", { name: "Resolve conflict" })[0]);
    const dialog = screen.getByRole("dialog", { name: "Resolve conflict" });
    await user.type(within(dialog).getByLabelText("Resolution reason"), "Engagement purpose remains controlling for this preview.");
    await user.click(within(dialog).getByRole("button", { name: "Resolve conflict" }));

    expect(screen.getByRole("status")).toHaveTextContent("explicit competing rejections");
    expect(within(conflicts).getAllByText("Resolved").length).toBeGreaterThan(1);
  });

  it("adds a manual fact with dot-notation identity and provenance", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.click(screen.getByRole("button", { name: "Add fact" }));
    await user.type(screen.getByLabelText("AIR field key"), "subject.condition");
    await user.type(screen.getByLabelText("Field label"), "Condition");
    await user.type(screen.getByLabelText("Value"), "Average");
    await user.type(screen.getByLabelText("Reason and provenance"), "Observed by the synthetic appraiser.");
    await user.click(within(screen.getByRole("dialog", { name: "Add appraiser-entered fact" })).getByRole("button", { name: "Add fact" }));

    expect(screen.getByRole("heading", { name: "Appraiser-entered facts" })).toBeInTheDocument();
    expect(screen.getByText("subject.condition · Observed by the synthetic appraiser.")).toBeInTheDocument();
  });

  it("shows missing critical fields and practical readiness blockers", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.click(screen.getByRole("button", { name: "Missing critical" }));

    expect(screen.getByRole("heading", { name: "Missing critical information" })).toBeInTheDocument();
    expect(screen.getByText("assignment.appraisal_purpose")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Readiness" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Current blockers" })).toBeInTheDocument();
  });

  it("renders the AIR-generated brief and deterministic export controls", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.click(screen.getByRole("button", { name: "Generate / review brief" }));

    expect(screen.getByRole("heading", { name: "Assignment / Property Brief" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Assignment synopsis" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Subject synopsis" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Issues requiring attention" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Evidence summary" })).toBeInTheDocument();
    expect(screen.getByText(/does not constitute professional comparable selection/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "AIR JSON" })).toHaveAttribute("download", "assignment-intelligence-record-v1.json");
    expect(screen.getByRole("link", { name: "Brief JSON" })).toHaveAttribute("download", "assignment-property-brief-v1.json");
    expect(screen.getByRole("link", { name: "Markdown" })).toHaveAttribute("download", "assignment-property-brief-v1.md");
  });

  it("offers next-unreviewed keyboard focus and an AIR refresh control", async () => {
    const user = userEvent.setup();
    render(<LocalIntakeReviewWorkspace />);

    await user.click(screen.getByRole("button", { name: "Next unreviewed" }));
    expect(document.activeElement).toHaveAttribute("id", expect.stringContaining("candidate-"));
    await user.click(screen.getByRole("button", { name: "Assemble / refresh AIR" }));
    expect(screen.getByRole("status")).toHaveTextContent("Canonical AIR refresh requested");
  });
});
