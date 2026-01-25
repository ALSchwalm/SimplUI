# Plan - Dynamic Seed Visibility

## Phase 1: Logic & State Preparation [checkpoint: 1cf98e1]
- [x] Task: Update extraction logic for initial randomization state
    - [x] Modify `extract_workflow_inputs` in `src/ui.py` to ensure that if a seed value is `0`, the `randomize` property in the metadata is explicitly set to `True`.
- [x] Task: Ensure base seed update timing
    - [x] Verify `process_generation` in `src/ui.py` correctly yields the updated `overrides` (containing new base seeds) *before* entering the batch loop.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Logic & State Preparation' (Protocol in workflow.md)

## Phase 2: UI Dynamic Visibility [checkpoint: 1c0cd3d]
- [x] Task: Implement conditional visibility in renderer
    - [x] Update the `render_dynamic_interface` function in `src/ui.py`.
    - [x] For `seed` type inputs, set `visible=not random_val` for the numeric Textbox.
- [x] Task: Add client-side toggle trigger
    - [x] Ensure the `random_box.change` event handler correctly triggers a re-render of the dynamic interface by updating the `overrides_store`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: UI Dynamic Visibility' (Protocol in workflow.md)

## Phase 3: Verification & Integration [checkpoint: 1c0cd3d]
- [x] Task: Unit testing visibility logic
    - [x] Add a test case to `tests/test_ui.py` (or a new test file) to verify that the extracted metadata correctly reflects `randomize=True` for seed `0`.
- [x] Task: UI Automation tests
    - [x] Update `tests/ui/test_seed_behavior.py` or create a new Playwright test.
    - [x] Verify that clicking "Randomize" hides the textbox.
    - [x] Verify that unchecking "Randomize" shows the textbox.
    - [x] Verify that a seed of `0` in a new workflow initializes to hidden/randomized.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Verification & Integration' (Protocol in workflow.md)
