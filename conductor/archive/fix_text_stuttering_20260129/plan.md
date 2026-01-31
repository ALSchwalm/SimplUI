# Implementation Plan: Fix Text Input Stuttering in Node Controls

This plan addresses the stuttering issue in the "Node Controls" sidebar by changing text input update triggers from `change` to `submit` and `blur`.

## Phase 1: Implementation
- [x] Task: Locate dynamic text input components in `src/ui.py`.
    -   Identify `gr.Textbox` and `gr.Number` calls within `render_dynamic_interface`.
- [x] Task: Modify event listeners for `gr.Textbox` components.
    -   Change `.change()` to `.blur()`.
    -   Add `.submit()` listener to handle the Enter key.
- [x] Task: Modify event listeners for `gr.Number` components.
    -   Change `.change()` to `.blur()`.
    -   Add `.submit()` listener to handle the Enter key.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Implementation' (Protocol in workflow.md)

## Phase 2: Verification and Quality
- [x] Task: Create a Playwright UI test (`tests/ui/test_textbox_behavior.py`) to verify that typing doesn't trigger immediate updates but blur/enter does.
- [x] Task: Verify that clicking "Generate" while focused on a textbox correctly persists the value.
- [x] Task: Run all UI tests to ensure no regressions in advanced control state management.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Verification and Quality' (Protocol in workflow.md)
