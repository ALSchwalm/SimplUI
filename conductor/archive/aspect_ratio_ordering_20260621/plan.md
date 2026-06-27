# Plan - Reorganize Aspect Ratio Presets

## Phase 1: Reorder Aspect Ratio Presets [checkpoint: 7b8bcdb]

- [x] Task: Write Tests (Red Phase) (80d245c)
    - [x] Create or update test cases in `tests/test_dimension_utils.py` asserting that `ASPECT_RATIOS` is sorted from tallest to widest.
    - [x] Run pytest to verify the new test fails.
- [x] Task: Implement to Pass Tests (Green Phase) (a98edee)
    - [x] Reorder the `ASPECT_RATIOS` array in `src/dimension_utils.py`.
    - [x] Reorder the `ASPECT_RATIOS` array in `static/app.js`.
    - [x] Run pytest to verify all unit tests pass.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Reorder Aspect Ratio Presets' (Protocol in workflow.md)
