# Plan - Reorganize Aspect Ratio Presets

## Phase 1: Reorder Aspect Ratio Presets

- [ ] Task: Write Tests (Red Phase)
    - [ ] Create or update test cases in `tests/test_dimension_utils.py` asserting that `ASPECT_RATIOS` is sorted from tallest to widest.
    - [ ] Run pytest to verify the new test fails.
- [ ] Task: Implement to Pass Tests (Green Phase)
    - [ ] Reorder the `ASPECT_RATIOS` array in `src/dimension_utils.py`.
    - [ ] Reorder the `ASPECT_RATIOS` array in `static/app.js`.
    - [ ] Run pytest to verify all unit tests pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Reorder Aspect Ratio Presets' (Protocol in workflow.md)
