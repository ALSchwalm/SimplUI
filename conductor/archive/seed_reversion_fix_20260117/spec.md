# Specification - Fix: Seed Reversion on Randomize Toggle

## Overview
A bug exists in the seed control logic where disabling the "randomize" toggle causes the seed value to revert to a previous state rather than persisting the current value. This prevents users from easily "locking in" a randomly generated seed for subsequent manual adjustments.

## Functional Requirements
- **State Persistence:** When the "Randomize" checkbox is unchecked, the value currently in the seed textbox must remain unchanged.
- **Post-Generation Consistency:** If a random seed was generated and used during the most recent generation process, that specific seed value should be the one visible and preserved when randomization is turned off.
- **Client-Side Sync:** Ensure the `overrides_store` (client-side state) correctly reflects the transition from random to fixed state without triggering unintended value resets.

## Technical Details
- **Component Targeting:** Target the seed `Textbox` and `Checkbox` components in the dynamic interface renderer within `src/ui.py`.
- **Interaction Logic:** Review the JS-based update mechanism `(val, store) => { store['{key}'] = val; return store; }` and the `on_generate` function's seed injection logic to ensure they don't overwrite each other incorrectly during the toggle event.

## Acceptance Criteria
- [ ] 1. Check "Randomize" for a seed.
- [ ] 2. Click "Generate". Observe a new random seed in the status/output.
- [ ] 3. Uncheck "Randomize".
- [ ] 4. The seed textbox should now contain the exact value used in the previous generation.
- [ ] 5. Clicking "Generate" again (with "Randomize" now unchecked) should use that same seed value.

## Out of Scope
- Refactoring the entire `overrides_store` mechanism.
- Changing the 64-bit integer handling for seeds.
