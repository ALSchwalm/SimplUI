# Implementation Plan: Relocate Batch Count in Advanced Controls

## Phase 1: Relocate Batch Count and Add Visual Divider
- [x] Task: Write failing tests (Red Phase) [6a09112]
    - [x] Add unit tests in `tests/test_layout.py` to assert that in `static/index.html`, the batch count slider element is defined after the workflow select element and before the dynamic controls container.
    - [x] Add assertions that a divider or border style exists separating default controls from dynamic controls.
    - [x] Run the tests and confirm they fail.
- [x] Task: Implement HTML layout relocation (Green Phase) [c90ab68]
    - [x] Modify `static/index.html` to relocate the batch count settings group element directly below the workflow selection settings group element and above the dynamic controls container.
- [x] Task: Add CSS divider styling (Green Phase) [fddf34c]
    - [x] Modify `static/styles.css` to add styling to visually separate the default settings (Workflow Selection and Batch Count) from the dynamic controls.
    - [x] Run the tests and confirm that all tests now pass.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Relocate Batch Count and Add Visual Divider' (Protocol in workflow.md)
