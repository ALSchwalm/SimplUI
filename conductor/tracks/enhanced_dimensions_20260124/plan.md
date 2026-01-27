# Plan - Enhanced Dimension Control with View Toggle

## Phase 1: Logic Implementation [checkpoint: 70cf326]
- [x] Task: Implement reverse dimension lookup
    - [x] Update `src/dimension_utils.py` to include a function `find_matching_preset(width, height)` that returns `(aspect_ratio, pixel_count)` if an exact match exists, or `None`.
    - [x] Implement `find_nearest_preset(width, height)` to find the closest match for snapping behavior.
- [x] Task: Unit testing for logic
    - [x] Update `tests/test_dimension_utils.py` to test exact matching and nearest neighbor logic.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Logic Implementation' (Protocol in workflow.md)

## Phase 2: UI Updates & Toggle [checkpoint: 5bb00f8]
- [x] Task: Update dynamic renderer for dual modes
    - [x] Modify `render_dynamic_interface` in `src/ui.py`.
    - [x] Implement the logic to decide initial mode based on `find_matching_preset`.
    - [x] Render both sets of controls (Dropdowns AND Number inputs) but control their `visible` property based on a local state variable (e.g., `is_simplified_view`).
- [x] Task: Implement toggle button logic
    - [x] Add the "Show Exact Dimensions" / "Show Aspect Ratio" toggle button.
    - [x] Wire the click event to toggle the `visible` properties.
    - [x] Implement the "Snap to Nearest" logic when switching to Simplified mode using JS or Python callback.
- [~] Task: Conductor - User Manual Verification 'Phase 2: UI Updates & Toggle' (Protocol in workflow.md)

## Phase 3: Integration & Refinement
- [ ] Task: Update extraction logic
    - [ ] Ensure `extract_workflow_inputs` preserves the raw values correctly so the renderer can make the decision.
- [ ] Task: Integration Testing
    - [ ] Create `tests/ui/test_dimension_toggle.py` to verify:
        - [ ] Default view logic (1024x1024 -> Simplified, 1000x1000 -> Exact).
        - [ ] Toggle functionality.
        - [ ] Snapping behavior.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration & Refinement' (Protocol in workflow.md)
