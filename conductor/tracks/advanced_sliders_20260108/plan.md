# Plan: Advanced Slider Controls

This plan follows Test-Driven Development (TDD).

## Phase 1: Configuration and Logic

- [~] Task: Config - Implement slider range management
    - [ ] Sub-task: Write tests for `ConfigManager` merging hardcoded slider defaults with `config.json`
    - [ ] Sub-task: Implement built-in defaults and loading logic in `ConfigManager`
- [x] Task: UI Logic - Tag slider inputs 72bdade
    - [x] Sub-task: Write tests for `extract_workflow_inputs` identifying sliders from metadata and config
    - [x] Sub-task: Update `extract_workflow_inputs` to handle range extraction and tagging
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: UI Implementation and Verification

- [ ] Task: Gradio UI - Render Sliders
    - [ ] Sub-task: Write UI automation test verifying a slider is rendered for "steps"
    - [ ] Sub-task: Update `render_dynamic_interface` to create `gr.Slider`
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
