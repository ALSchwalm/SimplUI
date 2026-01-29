# Specification: Fix Flaky History Integration Test

## Overview
The `test_history_integration` automated test is failing (reporting 2 images instead of 4) despite manual verification confirming that the history feature works correctly in the UI.

The suspected root cause is a race condition in the test logic. Specifically, the test waits for a "Generation complete" message to verify that a batch has finished. However, since the same status message is used for consecutive runs, the test might be prematurely matching the *previous* run's completion message, causing it to assert the gallery count before the second run's images have actually been added.

## Functional Requirements
1.  **Reliable Synchronization:** The test must unambiguously verify that the *second* generation run has completed before checking the total image count.
2.  **Accurate Assertions:** The test must correctly assert that 4 images are present in the history gallery after two runs of batch count 2.
3.  **No Code Changes:** Ideally, this fix should be confined to the test file (`tests/ui/test_history_integration.py`) and should not require changes to the application logic, as the feature itself is working.

## Proposed Solution
Modify the test to ensure it waits for a *new* completion event or a distinct state change between runs. Strategies include:
*   Waiting for the status to change to "Processing" *before* waiting for "Generation complete" again.
*   Checking for a specific increase in the image count (e.g., wait for count > 2) rather than just a status message.
*   Clearing or checking for the absence of the completion message before starting the second run.

## Acceptance Criteria
*   `pytest tests/ui/test_history_integration.py` passes consistently.
*   No regressions in other tests.
