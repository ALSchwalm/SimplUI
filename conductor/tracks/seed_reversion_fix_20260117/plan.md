# Implementation Plan - Fix: Seed Reversion on Randomize Toggle

## Phase 1: Reproduction and Automated Testing
- [x] Task: Create a reproduction test case 286baf9
    - [x] Create `tests/ui/test_seed_behavior.py`.
    - [x] Implement a Playwright test that:
        1. Opens the UI.
        2. Enables "Randomize" for a seed.
        3. Clicks "Generate" and captures the generated seed from the status text.
        4. Disables "Randomize".
        5. Asserts that the seed textbox value matches the captured seed (proving the bug if it fails).

## Phase 2: Implementation
- [x] Task: Update Seed State Management 286baf9
    - [x] Modify `src/ui.py` to ensure that when `on_generate` randomizes a seed, it updates the `overrides_store` in a way that the UI component reflects the new value.
    - [x] Investigate the `@gr.render` block for seed inputs to ensure the `Textbox` value is correctly bound to the latest value in `overrides_store` during re-renders.
    - [x] Add a JS callback or update the existing one to ensure that unchecking "Randomize" doesn't trigger a value reset from an stale component state.
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 3: Verification
- [ ] Task: Run Verification Tests
    - [ ] Execute `pytest tests/ui/test_seed_behavior.py` and ensure it passes.
    - [ ] Run existing UI tests to check for regressions in advanced controls.
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
