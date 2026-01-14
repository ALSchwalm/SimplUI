# Plan: Seed Randomization

This plan follows Test-Driven Development (TDD).

## Phase 1: Logic and State Management

- [x] Task: UI Logic - Implement seed detection and tagging 2d2cf76
    - [x] Sub-task: Write tests for `extract_workflow_inputs` identifying "seed" inputs and default random state
    - [x] Sub-task: Update `extract_workflow_inputs` to tag seed inputs and set `random_default`
- [x] Task: UI Logic - Implement random seed generation c871979
    - [x] Sub-task: Update `on_generate` to detect randomization flags and generate new seeds
    - [x] Sub-task: Write tests verifying `overrides` dictionary is updated with random seeds
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: UI Implementation and Feedback

- [x] Task: Gradio UI - Render Randomize checkboxes 6743f32
    - [x] Sub-task: Write UI automation test verifying checkbox presence and default state
    - [x] Sub-task: Update `render_dynamic_interface` to show `gr.Checkbox` for seeds
- [x] Task: Gradio UI - Implement seed value feedback 6743f32
    - [x] Sub-task: Update `on_generate` to yield component updates for the seed inputs
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
