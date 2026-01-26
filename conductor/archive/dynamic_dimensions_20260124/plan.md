# Plan - Dynamic Aspect Ratio and Resolution Control

## Phase 1: Dimension Calculation Logic [checkpoint: 142c5db]
- [x] Task: Implement dimension utility functions
    - [x] Create `src/dimension_utils.py`.
    - [x] Implement `calculate_dimensions(aspect_ratio_str, pixel_count_m)` which returns `(width, height)`.
    - [x] Implement rounding to the nearest multiple of 64.
    - [x] Ensure "1M" pixels corresponds exactly to $1024 \times 1024$.
- [x] Task: Unit testing for dimension logic
    - [x] Create `tests/test_dimension_utils.py`.
    - [x] Test various ratios (1:1, 16:9, 2:1) and pixel counts.
    - [x] Verify rounding to 64.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Dimension Calculation Logic' (Protocol in workflow.md)

## Phase 2: UI Input Extraction & Grouping
- [x] Task: Update extraction logic to group dimensions
    - [x] Modify `extract_workflow_inputs` in `src/ui.py`.
    - [x] Detect nodes that have both `width` and `height` inputs.
    - [x] Group these into a single input item of type `dimensions`.
- [x] Task: Update dynamic renderer
    - [x] Modify `render_dynamic_interface` in `src/ui.py`.
    - [x] Add rendering logic for the `dimensions` type using two `gr.Dropdown` components (Aspect Ratio and Pixel Count).
    - [x] Set default selection to 1:1 and 1M if not already in overrides.
- [x] Task: Conductor - User Manual Verification 'Phase 2: UI Input Extraction & Grouping' (Protocol in workflow.md)

## Phase 3: State Management & Integration [checkpoint: 5071b6d]
- [x] Task: Implement JS-side dimension calculation
    - [x] Update the `change` handlers for the new dropdowns in `src/ui.py`.
    - [x] Use Javascript to calculate the width and height and update the `overrides_store` for both the selection state (to persist dropdown choices) and the raw `width`/`height` keys (to inject into the workflow).
- [x] Task: Integration Testing
    - [x] Write a Playwright test to verify that selecting "16:9" and "1M" updates the internal state to the correct calculated dimensions (e.g., $1344 \times 768$).
- [x] Task: Conductor - User Manual Verification 'Phase 3: State Management & Integration' (Protocol in workflow.md)
