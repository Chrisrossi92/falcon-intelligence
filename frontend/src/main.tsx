import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { IntelligenceWorkspacePreview } from "./workspace/IntelligenceWorkspacePreview";
import "./styles.css";

createRoot(document.getElementById("root") as HTMLElement).render(
  <StrictMode>
    <IntelligenceWorkspacePreview />
  </StrictMode>
);
