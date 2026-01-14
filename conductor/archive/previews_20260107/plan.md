# Plan: Real-time Generation Previews

This plan follows Test-Driven Development (TDD). Each feature task requires writing failing tests before implementation.

## Phase 1: ComfyClient Binary Message Handling [checkpoint: 20a264d]

- [x] Task: ComfyClient - Implement binary message detection and decoding 0618bca
    - [x] Sub-task: Write tests for binary message handling in `generate_image` (Mocked WS)
    - [x] Sub-task: Update `generate_image` to detect binary messages and yield `{"type": "preview", "data": bytes}`
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) 20a264d

## Phase 2: UI Integration for Live Previews [checkpoint: 0a9ce80]

- [x] Task: Gradio UI - Update generation loop to handle preview events d391a19
    - [x] Sub-task: Write integration tests verifying previews are yielded to the UI
    - [x] Sub-task: Update `handle_generation` in `src/ui.py` to process `preview` events
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) 0a9ce80
