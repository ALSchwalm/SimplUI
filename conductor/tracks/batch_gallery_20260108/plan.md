# Plan: Batch Image Support (Gallery)

This plan follows Test-Driven Development (TDD).

## Phase 1: Logic Refinement

- [x] Task: UI Logic - Update handle_generation for multiple images 8450cbf
    - [x] Sub-task: Write tests for `handle_generation` yielding lists of images
    - [x] Sub-task: Refactor `handle_generation` to maintain an image list and yield it
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: UI Implementation

- [x] Task: Gradio UI - Replace Image with Gallery 566134c
    - [x] Sub-task: Update `create_ui` to use `gr.Gallery`
    - [x] Sub-task: Update `on_generate` output mapping
- [x] Task: Testing - UI Automation 566134c
    - [x] Sub-task: Write Playwright test verifying that multiple items appear in the gallery for a mock batch
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) 566134c
