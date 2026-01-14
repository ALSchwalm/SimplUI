# Plan: Fix Seed Update on Randomization

This plan follows Test-Driven Development (TDD).

## Phase 1: Verify and Fix State Trigger

- [x] Task: UI Logic - Verify state-to-UI update loop 20289ce
    - [x] Sub-task: Write UI automation test (Playwright) that checks if the seed value in the input box changes after clicking Generate.
- [x] Task: UI Logic - Fix re-render trigger or value binding 8f8def6
    - [x] Sub-task: Ensure `gr.render` correctly picks up the updated seed from `overrides_store` when `on_generate` yields it.
    - [x] Sub-task: Add explicit trigger if needed: `triggers=[workflow_dropdown.change, overrides_store.change]`.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) 20289ce

## Phase 2: Refinement and Stability [checkpoint: 8f8def6]

- [x] Task: UX - Prevent focus loss during re-render 8f8def6
    - [x] Sub-task: Verify that re-rendering doesn't cause frustrating focus loss for the user (since it happens on click of Generate, it might be acceptable).
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) 8f8def6
