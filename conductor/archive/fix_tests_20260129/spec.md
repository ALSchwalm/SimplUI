# Specification: Fix Failing Tests

## Overview
The goal of this track is to restore the health of the test suite by addressing current failures. The user has indicated that the application functionality appears correct, suggesting the issues lie within the tests themselves (e.g., outdated selectors, timing issues, or incorrect assertions). We will identify all failing tests and fix them one by one without modifying the production code unless absolutely necessary.

## Functional Requirements

1.  **Identify Failures:**
    -   Execute the full test suite (`pytest`) to capture the current state.
    -   List all failing tests.

2.  **Fix Strategy:**
    -   Address each failing test individually.
    -   **Constraint:** Do not modify `src/` (production code) unless a genuine bug is discovered. Prioritize updating `tests/`.
    -   Common fixes may include:
        -   Updating UI selectors (IDs, classes, labels).
        -   Adjusting timeouts or `expect` conditions for asynchronous events.
        -   Correcting mock behaviors or test data setup.

3.  **Verification:**
    -   Ensure each fixed test passes in isolation.
    -   Ensure the full suite passes at the end of the track.

## Non-Functional Requirements
-   Maintain or improve the stability of the test suite.
-   Avoid introducing new flaky tests.

## Out of Scope
-   Refactoring production code.
-   Adding new feature tests (unless required to replace a broken/invalid test).
