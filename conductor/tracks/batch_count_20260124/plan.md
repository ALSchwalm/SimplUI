# Plan - Batch Count Feature

## Phase 1: UI Implementation [checkpoint: dddb7a3]
- [x] Task: Add Batch Count slider to UI bf12271
    - [x] Update `src/ui.py` to include a `gradio.Slider` for batch count in the Advanced Sidebar.
    - [x] Position it below the workflow dropdown.
    - [x] Set range 1-20, step 1, default 2.
- [x] Task: Persist Batch Count state bf12271
    - [x] Ensure the batch count value is included in the client-side state persistence logic in `src/ui.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: UI Implementation' (Protocol in workflow.md)

## Phase 2: Core Logic & Seed Derivation
- [x] Task: Implement Deterministic Seed Generator 59a312d
    - [x] Create a utility function/method to generate a sequence of $N$ seeds from a `base_seed` using a deterministic PRNG (e.g., `random.Random(base_seed)`).
    - [x] Write unit tests to verify that the same `base_seed` always produces the same sequence.
- [x] Task: Update Generation Loop 47b7db7
    - [x] Modify the generation trigger in `src/ui.py` or `src/comfy_client.py` to wrap the workflow submission in a loop.
    - [x] Ensure the loop respects the Batch Count value.
    - [x] Inject the derived seed for each iteration.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Core Logic & Seed Derivation' (Protocol in workflow.md)

## Phase 3: Gallery & Integration
- [ ] Task: Aggregate Gallery Results
    - [ ] Ensure the UI gallery correctly appends images from subsequent iterations without clearing previous results within the same batch.
    - [ ] Verify that live previews still function correctly for each iteration in the batch.
- [ ] Task: Integration Testing
    - [ ] Write an integration test (using Playwright) to verify that setting Batch Count > 1 triggers multiple requests and populates the gallery.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Gallery & Integration' (Protocol in workflow.md)