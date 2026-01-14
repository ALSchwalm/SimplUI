# Spec: UI Automation with Playwright

## Overview
This track introduces Playwright into the testing stack. This allows the AI agent to verify UI-level requirements (like button visibility, form behavior, and dynamic rendering) autonomously, reducing the need for manual user verification.

## Functional Requirements
- **Playwright Setup:** Install and configure Playwright for Python.
- **Pytest Integration:** Use `pytest-playwright` to allow UI tests to run as standard pytest cases.
- **Mocking Strategy:** Implement a way to run the Gradio app in a test context where ComfyUI API calls are mocked or redirected to a local mock server.
- **Headless Execution:** Default tests to run in headless mode for efficient automation.

## Technical Requirements
- Update `requirements.txt` with `pytest-playwright`.
- Create a `tests/ui/` directory for Playwright scripts.
- Implement a `conftest.py` fixture to launch/shutdown the Gradio app automatically for UI tests.
- Add an initial test case verifying:
    - Main components (Dropdown, Prompt, Generate) are visible.
    - Advanced controls can be toggled.

## Acceptance Criteria
- `pytest tests/ui/` runs and passes in a headless browser.
- The AI agent can successfully run these tests to verify UI changes without manual screenshots/confirmation.
- The mock server correctly simulates successful ComfyUI responses for UI verification.
