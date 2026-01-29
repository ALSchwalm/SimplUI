# Implementation Plan - Fix Concurrency Errors & State Reversion

Interacting with node-specific controls during an active generation causes `KeyError` exceptions and UI state reversions. We need to stabilize the Gradio event handling and ensure that state updates during generation are preserved for the next run without interfering with the current one.

## Phase 1: Diagnostics and Reproduction [checkpoint: 845bbc9]
- [x] Task: Create a reproduction script/test that simulates changing a control (e.g., a slider or toggle) while a long-running generation is active.
- [x] Task: Verify the `KeyError` occurs during dynamic visibility toggles (like "Show Exact Dimensions") while generation events are being sent.
- [x] Task: Confirm the "reversion" behavior where a slider moves back to its previous position after a preview update.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Diagnostics and Reproduction' (Protocol in workflow.md)

## Phase 2: Stabilize UI State & Prevent Reversions
- [ ] Task: Investigate the `ui.py` event triggers. Ensure that preview updates only update the `Image` component and do not trigger a full UI refresh or dependency re-evaluation that might overwrite other component states.
- [ ] Task: Update the generation loop to minimize the scope of returned updates. Instead of returning a list of all components, ensure only the gallery/preview and status markers are updated.
- [ ] Task: Implement a strategy (e.g., checking generation status in callbacks) to ensure that event listeners for advanced controls do not conflict with the generation queue.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Stabilize UI State & Prevent Reversions' (Protocol in workflow.md)

## Phase 3: Robust Error Handling & Final Verification
- [ ] Task: Add defensive error handling in the dynamic control generation logic to catch and log (but not crash on) Gradio internal `KeyErrors` during concurrent access.
- [ ] Task: Verify that all changes made during generation persist and are correctly used in the *next* generation call.
- [ ] Task: Run full suite of UI tests to ensure no regressions in basic generation or advanced control functionality.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Robust Error Handling & Final Verification' (Protocol in workflow.md)
