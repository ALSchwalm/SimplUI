# Implementation Plan: Compact Connection Status Indicator with Custom Tooltip

## Phase 1: Implement Compact Indicator and CSS Tooltip [checkpoint: 4c55f3e]
- [x] Task: Write failing tests (Red Phase) [4bc2eb8]
    - [x] Add unit tests in `tests/test_layout.py` to assert that `.status-text` is hidden in CSS, `app.js` sets the `data-tooltip` attribute on the connection indicator, and the custom CSS tooltip (`::after`) rules are present in `styles.css`.
    - [x] Run the tests and confirm they fail.
- [x] Task: Implement JS dynamic tooltip update (Green Phase) [54c208c]
    - [x] Modify `static/app.js` to update the `data-tooltip` attribute of `elements.connectionStatus` with the status text whenever the connection state changes.
- [x] Task: Implement CSS layout and tooltip styling (Green Phase) [7748741]
    - [x] Modify `static/styles.css` to hide `.status-text` (e.g., `display: none;` or screen-reader only styling) and update the padding/shape of `.connection-status` to make it a compact dot.
    - [x] Modify `static/styles.css` to add the custom CSS tooltip styling (fade-in, backdrop filter, position) on hover.
    - [x] Run the tests and confirm that all tests pass.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Implement Compact Indicator and CSS Tooltip' (Protocol in workflow.md) [4c55f3e]
