import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { LocalIntakeReviewWorkspace } from "./intake/LocalIntakeReviewWorkspace";
import "./styles.css";

createRoot(document.getElementById("root") as HTMLElement).render(
  <StrictMode>
    <LocalIntakeReviewWorkspace />
  </StrictMode>
);
