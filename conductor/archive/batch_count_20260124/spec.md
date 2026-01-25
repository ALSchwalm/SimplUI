# Specification - Batch Count Feature

## Overview
Introduce a "Batch Count" feature that allows users to trigger multiple sequential executions of a ComfyUI workflow with a single click. This feature bridges the gap between simple single-image generation and complex batch processing, ensuring that each iteration remains reproducible while producing unique results.

## Functional Requirements

### UI Controls
- **Location:** Position the Batch Count control within the "Advanced Controls" sidebar, specifically placed below the Workflow selection dropdown.
- **Input Type:** Provide a "Slider with Number Input" for granular and easy control.
- **Constraints:**
    - Minimum: 1
    - Maximum: 20 (to prevent server overload)
    - Step: 1
    - Default: 2

### Generation Logic
- **Sequential Execution:** The application will loop and trigger the ComfyUI workflow $N$ times (where $N$ is the Batch Count).
- **Deterministic Seed Derivation:** To ensure reproducibility, the seed for each iteration $i$ will be generated using a pseudo-random number generator (PRNG) initialized with the user-provided `base_seed`.
- **Gallery Integration:** The results gallery must aggregate and display all images generated across all $N$ iterations in real-time as they complete.

## Non-Functional Requirements
- **Resilience:** The Batch Count state should be persisted client-side along with other advanced settings.
- **Performance:** Iterations should be triggered sequentially to manage server load effectively.

## Acceptance Criteria
- [ ] User can adjust Batch Count (1-20) in the Advanced Sidebar.
- [ ] Clicking "Generate" triggers the workflow the specified number of times.
- [ ] Each iteration uses a unique but reproducible seed derived from the base seed.
- [ ] All images from all iterations appear in the output gallery.
- [ ] Using the same base seed and batch count results in the same sequence of images.

## Out of Scope
- Parallel execution of batch iterations (queued sequentially for now).
- Infinite batching/looping.