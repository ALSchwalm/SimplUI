# Implementation Plan: Fix persistent 'Generating...' badge on completed images

## Phase 1: Verification and Bug Fix [checkpoint: 0b9d8ca]
- [x] Task: Write failing tests (Red Phase) (c2e4338)
    - [x] Analyze existing tests to verify if we have coverage for gallery slot markup/badges.
    - [x] Write a test in `tests/test_fastapi_backend.py` or a frontend test verifying that the DOM structure for completed images does not contain the `preview-badge` element.
    - [x] Run the tests and confirm they fail.
- [x] Task: Implement fix to remove badge (Green Phase) (c2e4338)
    - [x] Inspect `static/app.js` (specifically `handleCompletedImage` and `createGallerySlot`).
    - [x] Modify `handleCompletedImage` to remove the `.preview-badge` element from the slot when the final image is set.
    - [x] Run the test suite and confirm that all tests now pass.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Verification and Bug Fix' (Protocol in workflow.md)
