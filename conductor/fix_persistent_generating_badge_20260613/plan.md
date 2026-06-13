# Implementation Plan: Fix persistent 'Generating...' badge on completed images

## Phase 1: Verification and Bug Fix
- [ ] Task: Write failing tests (Red Phase)
    - [ ] Analyze existing tests to verify if we have coverage for gallery slot markup/badges.
    - [ ] Write a test in `tests/test_fastapi_backend.py` or a frontend test verifying that the DOM structure for completed images does not contain the `preview-badge` element.
    - [ ] Run the tests and confirm they fail.
- [ ] Task: Implement fix to remove badge (Green Phase)
    - [ ] Inspect `static/app.js` (specifically `handleCompletedImage` and `createGallerySlot`).
    - [ ] Modify `handleCompletedImage` to remove the `.preview-badge` element from the slot when the final image is set.
    - [ ] Run the test suite and confirm that all tests now pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Verification and Bug Fix' (Protocol in workflow.md)
