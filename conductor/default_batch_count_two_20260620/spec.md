# Specification: Restore Default Batch Count to 2

## Overview
This track restores the default batch count setting of the application to `2`. A recent change set the default to `1`. This fix will update both the initial HTML element state and the client-side JavaScript initialization state to ensure that the default batch count is consistently `2` across all scenarios, including page loads, fresh session initializations, and state resets.

## Functional Requirements
1. **HTML Default Input Value:**
   - Update `static/index.html`'s `#batch-count-slider` input range element to have a default `value="2"`.
2. **JavaScript State Initialization:**
   - Update `static/app.js`'s initialization logic (inside the `init()` function) to set `state.batchCount` to `2`.
   - Update the UI slider value to `2` and update the value label (`#batch-count-value`) to display `'2'` on load.
3. **Automated Unit Testing:**
   - Write a unit test asserting that the default batch count value is set to `2` on page load / initialization.

## Acceptance Criteria
- The slider is initialized at `2` on page reload/fresh sessions.
- The label text next to the slider displays "Batch Count: 2" by default.
- The internal state variable `state.batchCount` is set to `2` on load.
- Automated tests pass and confirm that the default batch count is `2`.
