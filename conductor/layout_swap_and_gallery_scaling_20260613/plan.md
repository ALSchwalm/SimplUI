# Implementation Plan: Layout Swap and Gallery Scaling Updates

## Phase 1: Layout Swapping and CSS Sizing
- [ ] Task: Write failing tests (Red Phase)
    - [ ] Create a new unit test file `tests/test_layout.py` to parse `static/index.html` and verify that `gallery-card` is defined before `prompt-card`.
    - [ ] Add checks in `tests/test_layout.py` to assert that `static/styles.css` defines `.gallery-card` with a height of `70vh` (and does not define `.gallery-item` with `aspect-ratio: 1 / 1`).
    - [ ] Run the tests and confirm they fail.
- [ ] Task: Implement layout swap and CSS scaling updates (Green Phase)
    - [ ] Modify `static/index.html` to swap the positions of the Gallery Card and Prompt Card (Gallery on top).
    - [ ] Modify `static/styles.css` to update the `.gallery-card` height/max-height to `70vh` and remove/update `aspect-ratio: 1 / 1` from `.gallery-item` to let images scale naturally.
    - [ ] Add `max-width: 80vw` to `.gallery-item img` to ensure it is constrained properly.
    - [ ] Run the tests and confirm that all tests now pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Layout Swapping and CSS Sizing' (Protocol in workflow.md)
