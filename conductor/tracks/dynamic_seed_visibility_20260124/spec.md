# Specification - Dynamic Seed Visibility

## Overview
Refine the seed control interface within the "Advanced Controls" sidebar. To reduce clutter and improve clarity, the seed input box will be hidden whenever the "Randomize" option is enabled. When disabled, the seed box will reappear, populated with the base seed used for the most recent generation run.

## Functional Requirements

### UI Behavior
- **Conditional Visibility:** For every seed input, the numeric input box (Textbox) should be hidden if the corresponding "Randomize" checkbox is checked.
- **Initial State (Zero Logic):** If a workflow is loaded where a seed input value is `0`, the "Randomize" checkbox must be checked by default, and the numeric input box must be hidden.
- **Auto-Update Timing:** When "Generate" is clicked with "Randomize" enabled, the application will generate a new random base seed. This value must be pushed to the UI state **immediately at the start of the generation process**, ensuring the hidden input box is updated before the run begins.
- **Restoration:** When the user unchecks "Randomize", the seed input box becomes visible again, displaying the base seed that was just used (or generated).

### Implementation Details
- **Dynamic Rendering:** Leverage Gradio's `@gr.render` to dynamically adjust the `visible` property of seed input components based on the state of their respective "Randomize" checkboxes.
- **State Management:** Ensure the `overrides_store` correctly captures and propagates the generated base seed to the UI components during the generation lifecycle.

## Acceptance Criteria
- [ ] Seed inputs initialized to `0` in the workflow default to "Randomize" checked and input hidden.
- [ ] Checking "Randomize" immediately hides the associated seed numeric input.
- [ ] Unchecking "Randomize" immediately shows the associated seed numeric input.
- [ ] Clicking "Generate" while randomized updates the (hidden) seed value at the start of the run.
- [ ] After a randomized run, unchecking "Randomize" reveals the exact base seed used for that run.
- [ ] This behavior applies consistently to all seed inputs across all workflows.

## Out of Scope
- Animations for hide/show (prioritizing functional correctness first).
- Changes to how seeds are derived (handled in the Batch Count track).
