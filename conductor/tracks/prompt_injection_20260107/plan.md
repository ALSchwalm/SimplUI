# Plan: Dynamic Prompt Injection

This plan follows Test-Driven Development (TDD). Each feature task requires writing failing tests before implementation.

## Phase 1: Core Logic for Node Discovery and Injection [checkpoint: 2fdea8c]

- [x] Task: ComfyClient - Implement node discovery by title dc6af58
    - [x] Sub-task: Write tests for `find_node_by_title` (case-insensitive)
    - [x] Sub-task: Implement `find_node_by_title` in `ComfyClient`
- [x] Task: ComfyClient - Implement prompt injection logic 1d5fb3c
    - [x] Sub-task: Write tests for `inject_prompt`
    - [x] Sub-task: Implement `inject_prompt` which updates the workflow dictionary
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) 2fdea8c

## Phase 2: UI Integration

- [ ] Task: Gradio UI - Add Prompt Textarea component
    - [ ] Sub-task: Write tests for UI component presence and layout
    - [ ] Sub-task: Update `create_ui` to include the `Textbox` (lines=3+)
- [ ] Task: Gradio UI - Integrate prompt into generation flow
    - [ ] Sub-task: Write integration tests for end-to-end prompt injection
    - [ ] Sub-task: Update `handle_generation` to pass prompt text to `ComfyClient`
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
