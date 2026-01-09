# Plan: Core Connectivity and Basic Gradio UI

This plan follows Test-Driven Development (TDD). Each feature task requires writing failing tests before implementation.

## Phase 1: Project Foundation and Basic Connectivity [checkpoint: 6955e26]

- [x] Task: Initialize Python project environment and testing framework 0f326fb
- [x] Task: ComfyUI Client - Implement health check and basic connectivity cec0d23
    - [x] Sub-task: Write tests for `check_connection`
    - [x] Sub-task: Implement `check_connection` using `requests`
- [x] Task: Configuration Manager - Load ComfyUI URL and workflow list from JSON/YAML 7bfea68
    - [x] Sub-task: Write tests for config loading
    - [x] Sub-task: Implement configuration management
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) 6955e26

## Phase 2: Workflow Execution and WebSocket Integration [checkpoint: e7dc6f9]

- [x] Task: ComfyUI Client - Implement prompt submission 3568978
    - [x] Sub-task: Write tests for `submit_workflow`
    - [x] Sub-task: Implement `submit_workflow` (POST /prompt)
- [x] Task: ComfyUI Client - Implement WebSocket listener for progress and output 3e660b9
    - [x] Sub-task: Write tests for WebSocket message handling (mocked)
    - [x] Sub-task: Implement WebSocket client for image streaming
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) e7dc6f9

## Phase 3: Basic Gradio Interface

- [x] Task: Gradio UI - Implement main layout and workflow selection 6c60d07
    - [x] Sub-task: Write tests for UI component initialization
    - [x] Sub-task: Implement Gradio `Dropdown` and "Generate" `Button`
- [x] Task: Gradio UI - Integrate image generation and display logic b4529e1
    - [x] Sub-task: Write integration tests for end-to-end generation flow
    - [x] Sub-task: Implement Gradio callback for image generation
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
