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

## Phase 2: Dynamic UI Generation [checkpoint: 0ef3264]

- [x] Task: Gradio UI - Create Advanced Sidebar layout 7c46364
    - [x] Sub-task: Write tests for sidebar presence
    - [x] Sub-task: Implement `gr.Accordion` for "Advanced Controls"
- [x] Task: Gradio UI - Implement dynamic form generator b5213e6
    - [x] Sub-task: Write tests for dynamic component creation (mocked)
    - [x] Sub-task: Implement logic to render inputs based on the selected workflow
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) 0ef3264

## Phase 3: Resilience and Integration

- [x] Task: Resilience - Verify State Persistence c1b6605
    - [x] Sub-task: Write integration test simulating server restart/reload (UI state check)
    - [x] Sub-task: Refine state management to ensure robustness
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
