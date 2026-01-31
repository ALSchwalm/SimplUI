# Specification: Prompt Shortcut (Ctrl/Cmd + Enter)

## Overview
This feature adds a keyboard shortcut (`Ctrl+Enter` or `Cmd+Enter`) to the main prompt input field to improve the user workflow. This shortcut will provide a quick way to start or stop image generation without needing to manually click the UI buttons.

## Functional Requirements

1.  **Shortcut Support:**
    -   Support `Ctrl+Enter` on Windows/Linux.
    -   Support `Cmd+Enter` on macOS.

2.  **Context-Aware Activation:**
    -   The shortcut must only be active when the user is focused on the main prompt textarea (`prompt-input`).

3.  **Toggle Behavior:**
    -   **Generate:** If the application is in an idle state (no active generation), the shortcut triggers the generation process.
    -   **Stop:** If the application is currently generating images, the shortcut triggers the stop/interrupt process.

4.  **Integration:**
    -   The shortcut logic should map directly to the existing `generate_btn` and `stop_btn` event handlers in `src/ui.py`.

## Technical Implementation (Proposed)
-   Gradio `Textbox` component supports `.submit()`, but we need custom logic to handle the "Stop" toggle.
-   We will likely use a custom JavaScript event listener attached to the prompt box to detect the keys and trigger the appropriate hidden or visible button clicks, or call the Gradio functions directly if supported.

## Acceptance Criteria
-   Pressing `Ctrl+Enter` while the prompt is focused starts generation.
-   Pressing `Ctrl+Enter` again while generation is active stops it.
-   The same behavior applies to `Cmd+Enter` on Mac.
-   The shortcut does not trigger if the prompt box is not focused.

## Out of Scope
-   Global keyboard shortcuts (anywhere on the page).
-   Shortcuts for other actions (like "Skip" or "Advanced Controls").
