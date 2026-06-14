# Implementation Plan - Exclude Previews from Session History

## Phase 1: Bug Investigation & Fix [checkpoint: ce46664]

- [x] Task: Fix History Previews Bug (26ad61a)
    - [x] Write failing Playwright integration tests in a new test file `tests/test_history_previews.py` that verifies that intermediate preview images and skipped generations are never added to the History tab.
    - [x] Implement the code changes in `static/app.js` to remove the fallback history addition logic from the `executing` (node === null) block.
    - [x] Ensure that `handleCompletedImage` remains the single source of truth for session history additions.
    - [x] Run the automated test suite to ensure all tests pass (TDD Green phase).
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)
