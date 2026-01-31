# Implementation Plan: Prompt Shortcut (Ctrl/Cmd + Enter)

This plan implements the `Ctrl+Enter` / `Cmd+Enter` shortcut for generating and stopping workflows directly from the prompt box.

## Phase 1: Implementation
- [x] Task: Create a reproduction/test case (manual or automated if possible) to verify keypress handling.
    *   *Note: Testing specific keypresses in Gradio via unit tests is difficult. We will rely on Playwright for verification.*
- [x] Task: Modify `src/ui.py` to inject custom JavaScript for handling `Ctrl+Enter` / `Cmd+Enter` on the prompt Textbox.
    -   Sub-task: Write JavaScript logic to detect the key combination.
    -   Sub-task: Check the application state (Generating vs Idle) to determine action.
    -   Sub-task: Trigger the corresponding button click (`#gen-btn` or `#stop-btn`) programmatically.
- [x] Task: Ensure the shortcut works only when the prompt box is focused.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Implementation' (Protocol in workflow.md)

## Phase 2: Verification
- [x] Task: Create a Playwright UI test (`tests/ui/test_shortcuts.py`) to simulate `Ctrl+Enter` and verify it triggers generation.
- [x] Task: Extend the test to verify it stops generation when pressed again.
- [x] Task: Run all UI tests to ensure no regressions.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Verification' (Protocol in workflow.md)
