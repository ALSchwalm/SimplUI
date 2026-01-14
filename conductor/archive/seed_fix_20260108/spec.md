# Spec: Fix Seed Update on Randomization

## Overview
This track fixes a UX issue where the seed input field does not update to show the random seed generated when "Randomize" is checked. It ensures that the generated seed is both used for the generation and immediately displayed to the user.

## User Stories
- **User:** When I click "Generate" with "Randomize" checked, I want to see the new seed number immediately in the input box, so I know what seed is being used and can uncheck "Randomize" to keep it for the next run.

## Functional Requirements
- **Immediate Update:** When "Generate" is clicked and "Randomize" is active, a new random seed must be generated instantly.
- **UI Reflection:** This new seed must be pushed to the `gr.Number` component in the UI immediately, *before* or *as* the generation request is sent.
- **Data Consistency:** The exact same seed value shown in the UI must be sent to the ComfyUI backend.

## Technical Requirements
- Update `src/ui.py` to ensure the generated random seed is yielded back to the UI component.
- Since `gr.render` components are dynamic and hard to target, we leverage the `overrides_store` triggering a re-render or finding a way to update the specific input.
- **Refinement:** The current implementation updates `overrides_store`. We need to ensure this update triggers the `gr.Number` value update.
    - If `overrides_store` changes, `gr.render` should re-run.
    - We must ensure the re-run picks up the new value from the store.

## Acceptance Criteria
- Check "Randomize" for a seed.
- Click "Generate".
- The number in the seed box changes to a new random integer immediately.
- The generation proceeds using that new integer.
