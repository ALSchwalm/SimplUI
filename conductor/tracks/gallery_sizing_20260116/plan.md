# Implementation Plan - Fix: Image Gallery Sizing

## Phase 1: UI Layout Testing
- [x] Task: Create layout verification tests f395f36
    - [x] Create `tests/ui/test_gallery_layout.py`
    - [x] Implement a test that asserts the gallery container height does not exceed 70% of the viewport height.
    - [x] Implement a test that verifies the gallery's `object-fit` property is set to `contain`.

## Phase 2: Implementation
- [x] Task: Apply Height Constraints f395f36
    - [x] Modify `src/ui.py` to update the `gr.Gallery` component with `height="50vh"`.
    - [x] Add custom CSS to the `gr.Blocks` constructor to ensure the gallery and its child images respect the height limit without overflow issues.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 3: Verification
- [ ] Task: Run Regression and Layout Tests
    - [ ] Execute `pytest tests/ui/test_gallery_layout.py`.
    - [ ] Execute existing UI tests (`tests/ui/test_basic_layout.py`) to ensure no layout regressions.
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
