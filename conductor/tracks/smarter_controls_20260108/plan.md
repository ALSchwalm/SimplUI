# Plan: Smarter Advanced Controls

This plan follows Test-Driven Development (TDD).

## Phase 1: Metadata Retrieval

- [x] Task: ComfyClient - Implement object info fetching a09174e
    - [x] Sub-task: Write tests for `get_object_info` (Mocked API)
    - [x] Sub-task: Implement `get_object_info` in `ComfyClient` (GET /object_info)
- [x] Task: UI Logic - Integrate metadata into extraction 90b8514
    - [x] Sub-task: Write tests for `extract_workflow_inputs` with object info (identifying enums)
    - [x] Sub-task: Update `extract_workflow_inputs` to tag list-based inputs as "enum"
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Enhanced UI Rendering

- [ ] Task: Gradio UI - Implement Dropdown rendering
    - [ ] Sub-task: Write UI automation test (Playwright) verifying dropdown existence for sampler_name
    - [ ] Sub-task: Update `render_dynamic_interface` to render `gr.Dropdown` for "enum" types
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
