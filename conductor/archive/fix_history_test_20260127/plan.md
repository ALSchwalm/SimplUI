# Implementation Plan - Fix Flaky History Integration Test

The `test_history_integration` fails because it likely proceeds to check the gallery count for the second run while the "Generation complete" message from the first run is still visible, resulting in an incorrect image count (2 instead of 4).

## Phase 1: Reproduction & Robust Waiting [checkpoint: aef8059]
- [x] Task: Modify `tests/ui/test_history_integration.py` to add debug logging of the status text and gallery image counts between steps.
- [x] Task: Implement a "wait for state change" pattern in the test. Specifically, after clicking Generate for the second run, the test should first wait for the status to change from "Generation complete" to something like "Initializing" or "Processing" before waiting for "Generation complete" again.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Reproduction & Robust Waiting' (Protocol in workflow.md)

## Phase 2: Final Verification
- [x] Task: Verify that the test passes consistently across multiple local runs.
- [x] Task: Run the full test suite to ensure no regressions in other UI tests.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Final Verification' (Protocol in workflow.md)
