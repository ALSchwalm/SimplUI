# Plan - Dynamic Seed Visibility

## Phase 1: Logic & State Preparation [checkpoint: 1cf98e1]
- [x] Task: Update extraction logic for initial randomization state
    - [x] Modify `extract_workflow_inputs` in `src/ui.py` to ensure that if a seed value is `0`, the `randomize` property in the metadata is explicitly set to `True`.
- [x] Task: Ensure base seed update timing
    - [x] Verify `process_generation` in `src/ui.py` correctly yields the updated `overrides` (containing new base seeds) *before* entering the batch loop.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Logic & State Preparation' (Protocol in workflow.md)

## Phase 2: UI Dynamic Visibility
- [ ] Task: Implement conditional visibility in renderer
    - [ ] Update the `render_dynamic_interface` function in `src/ui.py`.
    - [ ] For `seed` type inputs, set `visible=not random_val` for the numeric Textbox.
- [ ] Task: Add client-side toggle trigger
    - [ ] Ensure the `random_box.change` event handler correctly triggers a re-render of the dynamic interface by updating the `overrides_store`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: UI Dynamic Visibility' (Protocol in workflow.md)

## Phase 3: Verification & Integration
- [ ] Task: Unit testing visibility logic
    - [ ] Add a test case to `tests/test_ui.py` (or a new test file) to verify that the extracted metadata correctly reflects `randomize=True` for seed `0`.
- [ ] Task: UI Automation tests
    - [ ] Update `tests/ui/test_seed_behavior.py` or create a new Playwright test.
    - [ ] Verify that clicking "Randomize" hides the textbox.
    - [ ] Verify that unchecking "Randomize" shows the textbox.
    - [ ] Verify that a seed of `0` in a new workflow initializes to hidden/randomized.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification & Integration' (Protocol in workflow.md)
