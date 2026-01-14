# Spec: Seed Randomization

## Overview
This track introduces automatic seed randomization for ComfyUI nodes. It allows users to toggle whether a specific seed should stay fixed or be randomized on every generation, enabling visual variety for the same prompt.

## User Stories
- **Novice User:** I want my images to be different every time I click "Generate" even if I don't change the prompt.
- **Advanced User:** I want to randomize the seed for one sampler but keep it fixed for another (e.g., in an img2img or controlnet workflow).

## Functional Requirements
- **Seed Detection:** Automatically identify input fields named "seed" (case-insensitive) in the workflow.
- **Randomization Toggle:** For each detected seed field, add a "Randomize Seed" checkbox in the Advanced Controls.
- **Default State:**
    - If the initial seed value in the workflow is `0`, the "Randomize Seed" checkbox should be **checked** by default.
    - Otherwise, it should be **unchecked**.
- **Dynamic Value Generation:** If "Randomize Seed" is checked for a field:
    - Before each generation, generate a large random integer.
    - Inject this random value into the workflow overrides.
- **Value Feedback:** After a successful generation, update the seed number input in the UI with the random value that was actually used. This allows users to uncheck "Randomize" and reuse that specific seed.

## Technical Requirements
- Update `extract_workflow_inputs` in `src/ui.py` to tag seed inputs.
- Update `render_dynamic_interface`:
    - Add a `gr.Checkbox` next to each tagged seed input.
    - Sync the checkbox state to the `overrides_store`.
- Update `on_generate`:
    - Check the state for randomization flags.
    - Generate and inject random seeds into the `overrides` dictionary before calling `handle_generation`.
    - Yield updates to set the new seed values in the UI components.

## Acceptance Criteria
- A "Randomize Seed" checkbox appears next to seed inputs.
- It defaults to TRUE if the seed is 0, FALSE otherwise.
- When checked, clicking "Generate" multiple times produces different images.
- When checked, the seed input box updates with the used value after generation.
- When unchecked, the value remains fixed.
