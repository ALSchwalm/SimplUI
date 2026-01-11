# Plan: Batch Image Support (Gallery)

This plan follows Test-Driven Development (TDD).

## Phase 1: Logic Refinement

- [x] Task: UI Logic - Update handle_generation for multiple images 8450cbf
    - [x] Sub-task: Write tests for `handle_generation` yielding lists of images
    - [x] Sub-task: Refactor `handle_generation` to maintain an image list and yield it
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: UI Implementation

- [ ] Task: Gradio UI - Replace Image with Gallery
    - [ ] Sub-task: Update `create_ui` to use `gr.Gallery`
    - [ ] Sub-task: Update `on_generate` output mapping
- [ ] Task: Testing - UI Automation
    - [ ] Sub-task: Write Playwright test verifying that multiple items appear in the gallery for a mock batch
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
