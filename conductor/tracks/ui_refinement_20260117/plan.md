# Implementation Plan - UI Refinement: Header Removal and Width Constraint

## Phase 1: Layout Verification Tests
- [x] Task: Create layout verification test ba95cc5
    - [x] Create `tests/ui/test_layout_constraints.py`.
    - [x] Implement a test that verifies the header text "Simpl2 ComfyUI Wrapper" is NOT visible in the page body.
    - [x] Implement a test that verifies the application container has a `max-width` of `1280px` (by checking computed styles of the root container).

## Phase 2: Implementation
- [x] Task: Remove Header and Constrain Width ba95cc5
    - [x] Modify `src/ui.py`: Remove `gr.Markdown("# Simpl2 ComfyUI Wrapper")`.
    - [x] Modify `src/ui.py`: Update the CSS string to include:
        ```css
        .gradio-container {
            max-width: 1280px !important;
            margin: 0 auto !important;
        }
        ```
- [ ] Task: Conductor - User Manual Verification 'Implementation' (Protocol in workflow.md)

## Phase 3: Verification
- [x] Task: Run Verification Tests ba95cc5
    - [x] Execute `pytest tests/ui/test_layout_constraints.py`.
    - [x] Execute `pytest tests/ui/test_basic_layout.py` (and update it if it explicitly checked for the header).
- [ ] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
