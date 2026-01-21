# Plan: Move Workflow Selection to Advanced Controls

Move the "Select Workflow" dropdown from the main interface into the "Advanced Controls" sidebar to simplify the UI for basic users.

## Phase 1: Test Updates (TDD) [checkpoint: 75306df]
- [x] Task: Update existing UI tests to expect the workflow dropdown in the sidebar. 75306df
    - [x] Sub-task: Modify `tests/ui/test_basic_layout.py` to check that the dropdown is initially hidden. 75306df
    - [x] Sub-task: Update `tests/ui/test_layout_redesign.py` to verify the dropdown appears in the sidebar when advanced controls are toggled. 75306df
- [x] Task: Conductor - User Manual Verification 'Test Updates' (Protocol in workflow.md) 75306df

## Phase 2: UI Implementation [checkpoint: 75306df]
- [x] Task: Relocate the `workflow_dropdown` component in `src/ui.py`. 75306df
    - [x] Sub-task: Remove the dropdown from the `main_col` layout block. 75306df
    - [x] Sub-task: Place the dropdown at the top of the `sidebar_col` (above the Node Controls tabs). 75306df
    - [x] Sub-task: Ensure all event bindings (`workflow_dropdown.change`, `@gr.render`) are updated to reference the new location. 75306df
- [x] Task: Conductor - User Manual Verification 'UI Implementation' (Protocol in workflow.md) 75306df

## Phase 3: Final Validation [checkpoint: 75306df]
- [x] Task: Verify end-to-step functionality. 75306df
    - [x] Sub-task: Confirm that the default workflow (first in list) is used correctly when advanced controls are off. 75306df
    - [x] Sub-task: Confirm that switching workflows in the sidebar updates the prompt and node controls as expected. 75306df
    - [x] Sub-task: Run all playwright UI tests. 75306df
- [x] Task: Conductor - User Manual Verification 'Final Validation' (Protocol in workflow.md) 75306df
