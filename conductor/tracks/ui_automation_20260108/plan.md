# Plan: UI Automation with Playwright

This plan follows Test-Driven Development (TDD) where applicable, although UI tests are their own form of verification.

## Phase 1: Infrastructure Setup

- [x] Task: Environment - Install Playwright dependencies 3fb5b52
    - [x] Sub-task: Add `pytest-playwright` to `requirements.txt`
    - [x] Sub-task: Install playwright browsers (`playwright install chromium`)
- [x] Task: Environment - Create conftest.py for UI testing 3fb5b52
    - [x] Sub-task: Implement `gradio_server` fixture to launch app in a background thread/process
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Mocking and Initial Tests

- [ ] Task: Mocking - Implement ComfyUI Mock Backend
    - [ ] Sub-task: Create a simple FastAPI or Flask mock to simulate ComfyUI endpoints
- [ ] Task: Testing - Implement first UI test case
    - [ ] Sub-task: Write `tests/ui/test_basic_layout.py`
    - [ ] Sub-task: Verify components visibility and basic interaction
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
