# Plan: UI Layout Redesign

## Phase 1: Layout Skeleton & Component Migration
- [x] Task: UI Logic - Refactor `create_ui` layout structure 4d490f9
    - [x] Sub-task: Wrap the entire UI in a top-level `gr.Row`.
    - [x] Sub-task: Create a `main_col` (left) and `sidebar_col` (right).
    - [x] Sub-task: Move the `gr.Gallery` and `status_text` into the top of `main_col`.
    - [x] Sub-task: Move the Prompt/Buttons area below the gallery in `main_col`.
- [x] Task: Gradio UI - Implement vertical button stack 4d490f9
    - [x] Sub-task: Create a `gr.Row` for the prompt area.
    - [x] Sub-task: Place the Prompt `gr.Textbox` in one column and the `Generate`/`Stop` buttons in a narrow column to its right.
    - [x] Sub-task: Verify buttons are vertically aligned when `Stop` is visible.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Layout Skeleton & Component Migration' (Protocol in workflow.md)

## Phase 2: Sidebar Toggle & Dynamic Rendering
- [x] Task: Gradio UI - Implement Sidebar Visibility Toggle 197cc01
    - [x] Sub-task: Add the "Advanced Controls" `gr.Checkbox` below the prompt area.
    - [x] Sub-task: Bind the checkbox change event to update the `visible` state of `sidebar_col`.
- [x] Task: Gradio UI - Migrate Dynamic Controls to Sidebar 197cc01
    - [x] Sub-task: Move the `@gr.render` block (Advanced Controls) into the `sidebar_col`.
    - [x] Sub-task: Remove the old `gr.Accordion`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Sidebar Toggle & Dynamic Rendering' (Protocol in workflow.md)

## Phase 3: Verification & Polish [checkpoint: 93b754e]
- [x] Task: Testing - Update UI Tests
    - [x] Sub-task: Update `tests/test_ui.py` to reflect the new component nesting and hierarchy.
    - [x] Sub-task: Write/Update Playwright tests to verify the sidebar toggle works and "pushes" content.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Verification & Polish' (Protocol in workflow.md)
