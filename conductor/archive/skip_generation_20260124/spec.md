# Specification - Skip Current Generation Feature

## Overview
Enhance the generation workflow by allowing users to skip the current image in a batch and immediately move to the next. During the generation process, the primary "Generate" button will be replaced by a visually distinct "Skip" button.

## Functional Requirements

### UI Behavior
- **Button Transformation:** When generation starts, the "Generate" button (Primary variant) will be hidden and replaced by a "Skip" button (Warning variant, likely orange/yellow).
- **Conditional Replacement:** If the current generation is the *last* one in the batch, the "Skip" button should behave like a "Stop" action to avoid ambiguity.
- **Gallery Update:** Clicking "Skip" must immediately remove the active preview of the current generation from the results gallery. Images from previously completed iterations in the same batch must remain visible.

### Generation Logic
- **Skip Action:** Triggering "Skip" will send a cancellation request to ComfyUI for the *current* prompt only, then the loop in the application will immediately proceed to the next iteration in the batch.
- **Interruption Integration:** Leverage ComfyUI's `/interrupt` functionality, ensuring the loop in `process_generation` catches the skip signal and continues.

## Non-Functional Requirements
- **Responsiveness:** The UI must reflect the "Skip" action and move to the next batch status update within <500ms.

## Acceptance Criteria
- [ ] Clicking "Generate" replaces it with a distinct "Skip" button.
- [ ] Clicking "Skip" drops the current generation and starts the next one in the batch.
- [ ] Previews for the skipped image are removed from the gallery.
- [ ] Previously completed images in the same batch are preserved.
- [ ] Skipping the final image in a batch stops the generation process entirely.
- [ ] The "Skip" button reverts to "Generate" once the entire batch is finished or stopped.

## Out of Scope
- Re-ordering images in the batch.
- Retrying a specific skipped index within the same batch.
