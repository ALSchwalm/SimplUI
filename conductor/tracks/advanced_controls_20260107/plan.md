# Plan: Advanced Node Controls

This plan follows Test-Driven Development (TDD). Each feature task requires writing failing tests before implementation.

## Phase 1: Workflow Parsing and Property Extraction [checkpoint: db4cef5]

- [x] Task: UI Logic - Implement workflow parser for input extraction ef3ef97
    - [x] Sub-task: Write tests for `extract_workflow_inputs`
    - [x] Sub-task: Implement `extract_workflow_inputs` in `src/ui.py`
- [x] Task: UI Logic - Implement state merging logic ef3ef97
    - [x] Sub-task: Write tests for merging user overrides into the workflow
    - [x] Sub-task: Implement merge logic in `handle_generation`
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) db4cef5

## Phase 2: Dynamic UI Generation

- [ ] Task: Gradio UI - Create Advanced Sidebar layout
    - [ ] Sub-task: Write tests for sidebar presence
    - [ ] Sub-task: Implement `gr.Accordion` for "Advanced Controls"
- [ ] Task: Gradio UI - Implement dynamic form generator
    - [ ] Sub-task: Write tests for dynamic component creation (mocked)
    - [ ] Sub-task: Implement logic to render inputs based on the selected workflow
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Resilience and Integration

- [ ] Task: Resilience - Verify State Persistence
    - [ ] Sub-task: Write integration test simulating server restart/reload (UI state check)
    - [ ] Sub-task: Refine state management to ensure robustness
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
