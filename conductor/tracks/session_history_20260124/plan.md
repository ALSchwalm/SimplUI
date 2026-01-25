# Plan - Session History Feature

## Phase 1: UI & State Setup [checkpoint: adde51e]
- [x] Task: Define history state and gallery
    - [x] Update `src/ui.py` to initialize a `gr.State` (for the image list) and a `gr.Gallery` (the History display) inside a new "History" tab in the sidebar.
    - [x] Ensure the History gallery is styled consistently with the main gallery (e.g., `object_fit="contain"`).
- [x] Task: Conductor - User Manual Verification 'Phase 1: UI & State Setup' (Protocol in workflow.md)

## Phase 2: Logic Implementation
- [ ] Task: Update generation loop for history tracking
    - [ ] Modify `process_generation` in `src/ui.py` to accept `history_state` as an argument.
    - [ ] Update the `process_generation` loop to append final images to the `history_state` only when an iteration completes successfully (avoiding previews).
    - [ ] Update all `yield` statements in `process_generation` to include the `history_state` and the `history_gallery` update.
- [ ] Task: Update event wiring
    - [ ] Update the `generate_btn.click` call in `create_ui` to include `history_state` in inputs/outputs and `history_gallery` in outputs.
    - [ ] Ensure `on_generate` correctly passes through the new state.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Logic Implementation' (Protocol in workflow.md)

## Phase 3: Verification & Refinement
- [ ] Task: Unit testing history aggregation
    - [ ] Create/update tests in `tests/test_batch_logic.py` or a new test file to verify that `process_generation` correctly accumulates only final images in the yielded history state.
- [ ] Task: Integration Testing
    - [ ] Write a Playwright test to verify that after multiple "Generate" runs, the History tab contains the expected number of images and no previews.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification & Refinement' (Protocol in workflow.md)
