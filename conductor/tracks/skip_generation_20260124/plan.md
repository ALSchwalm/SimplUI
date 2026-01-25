# Plan - Skip Current Generation Feature

## Phase 1: UI Implementation [checkpoint: 7b08c16]
- [x] Task: Add Skip button to UI
    - [x] Update `src/ui.py` to include a "Skip" button (`gr.Button`) in the same column as "Generate".
    - [x] Set "Skip" button to `visible=False` and variant `warning`.
- [x] Task: Implement button visibility state machine
    - [x] Modify `on_generate` and `process_generation` to handle the visibility toggle between "Generate" and "Skip".
    - [x] Ensure "Generate" is hidden and "Skip" is shown when the run starts.
    - [x] Ensure "Skip" reverts to "Generate" on the last batch item or completion.
- [x] Task: Conductor - User Manual Verification 'Phase 1: UI Implementation' (Protocol in workflow.md)

## Phase 2: Skip Logic & Interruption [checkpoint: 8b9cc5e]
- [x] Task: Implement Skip signaling
    - [x] Add a mechanism to signal a skip from the UI to the generation loop (e.g., a shared flag or cancellation event).
- [x] Task: Update generation loop to handle skip
    - [x] Modify the loop in `process_generation` to catch interruptions or check the skip signal.
    - [x] Ensure that if "Skip" is clicked, the current iteration's `handle_generation` is cancelled but the loop proceeds to the next iteration.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Skip Logic & Interruption' (Protocol in workflow.md)

## Phase 3: Gallery State & Integration [checkpoint: bd41377]
- [x] Task: Clean gallery on skip
    - [x] Update the `process_generation` yield logic to explicitly remove the active preview from the gallery when a skip is triggered.
- [x] Task: Integration Testing
    - [x] Write a Playwright test to verify button swapping and skip-to-next behavior.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Gallery State & Integration' (Protocol in workflow.md)
