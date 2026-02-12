# Plan: Fix Prompt Injection for z-image Workflow

This plan outlines the steps to fix a bug where prompt injection fails for the `z-image.json` workflow. We will investigate why the "Prompt" node isn't being detected or updated and ensure the logic is robust enough to handle the node type used in that specific workflow.

## Phase 1: Diagnosis and Reproduction [checkpoint: 97e1a43]

- [x] Task: Create a reproduction test case for `z-image` prompt injection [93760ce]
    - [ ] Create a new test `tests/test_z_image_injection.py`.
    - [ ] Load `workflows/z-image.json` and attempt to inject a prompt using `comfy_client.py` or the relevant utility.
    - [ ] Assert that the resulting prompt dictionary contains the injected text in the correct node.
- [x] Task: Analyze `workflows/z-image.json` structure [9a7d24c]
    - [ ] Inspect the JSON structure of the "Prompt" node in `z-image.json`.
    - [ ] Compare it with the structure expected by the injection logic in `src/comfy_client.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Diagnosis and Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation

- [ ] Task: Refactor prompt injection logic to handle `z-image` node type
    - [ ] Modify the injection logic (likely in `src/comfy_client.py` or a dedicated utility) to correctly identify and update the "Prompt" node in `z-image.json`.
    - [ ] Ensure the fix is generic enough to handle similar node structures in other workflows.
- [ ] Task: Verify fix with reproduction test
    - [ ] Run `tests/test_z_image_injection.py` and ensure it passes.
- [ ] Task: Run regression tests
    - [ ] Run existing tests (e.g., `tests/test_workflow_parsing.py`, `tests/test_comfy_client.py`) to ensure no regressions in other workflows.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Final Verification

- [ ] Task: Perform manual verification with `z-image` workflow
    - [ ] Run the application, select the `z-image` workflow, enter a unique prompt, and verify the output (or logs/network traffic) shows the injected prompt.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Verification' (Protocol in workflow.md)
