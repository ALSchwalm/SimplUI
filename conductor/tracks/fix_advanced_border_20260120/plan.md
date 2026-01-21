# Plan: Fix Advanced Controls Border

Fix the layout issue where an unwanted border appears around the "Advanced Controls" toggle.

## Phase 1: Reproduction and Verification
- [x] Task: Create a reproduction test case (or identify existing one) to verify the current layout state.
- [x] Task: Conductor - User Manual Verification 'Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation
- [x] Task: Remove the `gr.Row` wrapper around `advanced_toggle` in `src/ui.py`.
- [x] Task: Investigate and fix persistent border issue (removing `gr.Row` was insufficient).
    - [x] Sub-task: Pass the missing `css` argument to `gr.Blocks`.
    - [x] Sub-task: Add `elem_id="advanced-checkbox"` to the toggle and target it with custom CSS to force removal of borders/padding.
- [ ] Task: Verify the visual fix and ensure no regressions in layout or functionality.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 3: Final Validation
- [ ] Task: Run all UI tests to ensure the selector for "Advanced Controls" is still valid and functioning.
