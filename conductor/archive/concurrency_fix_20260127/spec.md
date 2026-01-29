# Specification: Fix Concurrency Errors & State Reversion in Advanced Controls

## Overview
Currently, interacting with "Advanced Controls" (specifically dynamic widgets like "Show Exact Dimensions" or node-specific sliders) during an active generation causes backend errors (`KeyError: 1396`) and frontend state issues (user inputs reverting/undoing when a preview updates).

The goal is to ensure robust concurrency: users should be able to adjust settings freely during generation. These adjustments should persist without errors and apply **only** to the next requested generation, not the currently running one or its pending batch items.

## Functional Requirements
1.  **Error-Free Interaction:** Toggling "Show Exact Dimensions" or adjusting node control sliders during an active generation must not trigger `KeyError` or other exceptions in the server logs.
2.  **State Persistence:** Adjusting a control (e.g., moving a slider) during generation must not be "undone" or reverted when the UI updates with a new generation preview image.
3.  **Scope of Impact:** Changes made to settings during an active generation must:
    *   **Ignore:** Have NO effect on the currently running generation or any remaining images in the current batch.
    *   **Apply:** Be preserved and applied to the *next* manual "Generate" request.
4.  **System Stability:** The application must remain responsive and stable (no crashes) during these concurrent interactions.

## Technical Context (Inferred)
*   **Root Cause:** The `KeyError` suggests a race condition in Gradio's queue or component registry, likely triggered when dynamic visibility changes (adding/removing components from the render tree) occur while the generation thread is yielding events.
*   **State Reversion:** The "undo" behavior suggests that the preview update event might be pushing a full state synchronization that overwrites the user's unsent local changes, or that the component is being re-rendered, losing its client-side state.

## Out of Scope
*   Applying changes immediately to the *current* generation (e.g., changing the prompt mid-stream).
