# Specification: Fix persistent 'Generating...' badge on completed images

## Overview
There is a bug in the gallery slot update logic where the "Generating..." preview badge remains visible on top of the final image even after the generation finishes successfully. This specification outlines the fix to ensure the badge is completely removed from the slot when the final image is loaded.

## Functional Requirements
1. **Badge Removal on Completion:**
   - When the final image is successfully rendered in a gallery slot (via `handleCompletedImage`), the "Generating..." badge (`preview-badge`) must be completely removed/cleared from the slot's DOM structure.
2. **Batch Generation Handling:**
   - In a batch generation, each gallery slot must independently display the "Generating..." badge while its corresponding iteration is running.
   - Upon completion of each individual iteration, the badge must be removed from its respective slot, leaving only the completed image and the index badge.
3. **Skip Handling:**
   - When an iteration is skipped, the "Generating..." badge must be removed, and the slot should be updated to show the "Skipped" text placeholder.

## Non-Functional Requirements
- **DOM Consistency:** Ensure no leftover hidden or empty elements representing the badge remain in the gallery slot's DOM tree.

## Acceptance Criteria
- Single image generation: The "Generating..." badge is shown during generation, and is completely gone when the final image is displayed.
- Batch generation: Slots show "Generating..." badge while running, and the badge is removed as each image completes.
- Skipped generation: The badge is removed, and "Skipped" placeholder is displayed.

## Out of Scope
- General redesign of the gallery or the badge styles.
