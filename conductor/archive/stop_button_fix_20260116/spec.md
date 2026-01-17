# Specification - Fix: Stop Button Persistence

## Overview
Currently, the "Stop" button in the UI remains visible even after an image generation process has completed, been manually stopped, or encountered an error. This creates a confusing user experience where the interface appears to be in a "generating" state when it is actually idle.

## Functional Requirements
- **Post-Generation State:** Once a generation process finishes (successfully or otherwise), the "Stop" button must be hidden.
- **Button Toggle:** The "Generate" button must be shown and re-enabled as soon as the "Stop" button is hidden.
- **Progress Reset:** The progress bar must be reset to 0% or hidden when the generation ends.
- **Status Update:** The UI status indicator should transition to a "Ready" state upon completion, cancellation, or error.

## Technical Details
- **Trigger Points:** The UI update must be triggered by:
    1. Successful completion of the ComfyUI workflow.
    2. User clicking the "Stop" button (manual cancellation).
    3. An error occurring during the generation or communication process.
- **Component Targeting:** Target the Gradio `Button` and `Progress` components in `src/ui.py`.

## Acceptance Criteria
- [ ] After a successful generation, the "Stop" button is hidden and the "Generate" button is visible.
- [ ] After clicking "Stop", the "Stop" button is hidden and the "Generate" button is visible.
- [ ] If an error occurs during generation, the "Stop" button is hidden and the "Generate" button is visible.
- [ ] The progress bar and status text reset correctly in all "end-of-generation" scenarios.

## Out of Scope
- Refactoring the entire generation logic.
- Adding new features to the progress bar.
