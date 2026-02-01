# Specification: Remove Seed from Status Section

## Overview
Currently, the image generation status message includes the specific seed used (e.g., "Processing... Seed: 12345 (Batch 1/1)"). This track aims to remove this seed information from the status text to reduce UI clutter and simplify the status display. 

## Functional Requirements
- **Remove Seed Text:** The string ` Seed: [number]` must be removed from all status updates displayed in the UI.
- **Affected States:** This applies to the status message during generation (progress updates) and the final status message upon completion or interruption.
- **Preserve Other Info:** Other status information, such as the current batch progress (e.g., "(Batch 1/5)"), must remain untouched.

## Non-Functional Requirements
- **Test Integrity:** The removal must be verified by automated tests to prevent regressions.

## Acceptance Criteria
- [ ] Status text during generation does not contain the word "Seed".
- [ ] Status text after generation completes does not contain the word "Seed".
- [ ] Unit tests verify that the status formatting logic excludes seed information.
- [ ] Playwright integration tests verify that the `#status-text` element (or equivalent) never displays "Seed" during a mock generation run.

## Out of Scope
- Moving the seed information to another part of the UI (e.g., metadata or tooltips).
- Changing the seed randomization or generation logic itself.
