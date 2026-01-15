# Plan: Fix Preview Panel Flickering

## Phase 1: Investigation & Reproduction
- [x] Task: Reproduce flickering behavior
    - [x] Sub-task: Create or identify a test workflow that generates frequent previews.
    - [x] Sub-task: Run the application and visually confirm the flickering on every update.
- [x] Task: Analyze current implementation
    - [x] Sub-task: Review `src/ui.py` to see how preview images are updated.
    - [x] Sub-task: Review `src/comfy_client.py` to see how preview data is received and processed.
    - [x] Sub-task: Inspect the browser console/network tab during generation to see if image resources are being re-requested or if there are errors.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Investigation & Reproduction' (Protocol in workflow.md)

## Phase 2: Implementation
- [x] Task: Implement Fix
    - [x] Sub-task: Attempt to modify the `gr.Image` update mechanism (e.g., buffering, checking for None values).
    - [x] Sub-task: If `gr.Image` is the root cause, explore alternative Gradio components or custom JS (if applicable/necessary) to handle seamless updates. *Self-correction: Stick to Python/Gradio logical fixes first.*
    - [x] Sub-task: Apply the fix to `src/ui.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Verification
- [x] Task: Verify Fix
    - [x] Sub-task: Run the test workflow again.
    - [x] Sub-task: Visually confirm that the flickering is gone.
    - [x] Sub-task: Ensure that the final image still renders correctly.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Verification' (Protocol in workflow.md)
