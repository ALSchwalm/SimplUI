# Specification: Clear Previews on Stop/Skip

## Overview
Currently, when a generation is interrupted via the "Stop" or "Skip" buttons, the last received preview image remains visible in the gallery. This creates confusion, as the incomplete preview persists alongside (or instead of) final results. This track aims to fix this behavior by ensuring that any transient preview image is immediately removed from the UI when a Stop or Skip action is triggered.

## Functional Requirements

1.  **Stop Action Behavior:**
    -   When the user clicks the "Stop" button, the current preview image must be immediately removed from the gallery.
    -   The gallery must display **only** the images that successfully completed generation within the current batch.
    -   If no images completed generation in the current batch, the gallery must be cleared (empty).

2.  **Skip Action Behavior:**
    -   When the user clicks the "Skip" button, the current preview image must be immediately removed from the gallery.
    -   Similar to "Stop", the gallery must retain only successfully completed images from the current batch.
    -   The UI should prepare to display the next image in the batch (if applicable), but the "skipped" image's preview must not persist.

3.  **State Consistency:**
    -   The internal state representing the gallery images must be updated to reflect the removal of the preview, ensuring that subsequent UI updates do not accidentally restore it.

## Non-Functional Requirements
-   **Responsiveness:** The removal of the preview should happen immediately upon user interaction (optimistic update) or as soon as the cancellation event is processed, to prevent UI flicker or lag.

## Out of Scope
-   Changes to the "History" tab (previews are already excluded there).
-   Modifications to the actual ComfyUI cancellation logic (backend), only the frontend representation of the gallery is in scope.
