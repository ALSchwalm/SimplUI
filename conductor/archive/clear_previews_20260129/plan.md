# Implementation Plan: Clear Previews on Stop/Skip

This plan addresses the issue where preview images persist in the gallery after a generation is stopped or skipped. We will follow a TDD approach to ensure the fix is robust and verified.

## Phase 1: Reproduce and Setup
- [~] Task: Analyze current gallery and preview state management in `src/ui.py`.
- [x] Task: Create a reproduction UI test in `tests/ui/test_preview_persistence.py` that simulates a generation, triggers a 'Stop' or 'Skip', and asserts that the preview is removed while completed images remain. [repro-verified]
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Reproduce and Setup' (Protocol in workflow.md)

## Phase 2: Implementation
- [x] Task: Modify `src/ui.py` (or relevant state handler) to clear the current preview from the gallery's state when a 'Stop' signal is processed.
- [x] Task: Ensure the 'Skip' handler also triggers the removal of the current preview before proceeding to the next item in the batch.
- [x] Task: Verify that the gallery correctly updates to show only completed images after the preview is cleared.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Verification and Quality
- [x] Task: Run all UI and unit tests to ensure no regressions in generation flow or gallery display.
- [x] Task: Verify code coverage for the changes in `src/ui.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Verification and Quality' (Protocol in workflow.md)
