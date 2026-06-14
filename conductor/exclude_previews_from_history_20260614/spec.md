# Specification: Exclude Previews from Session History

## Overview
There is a bug in the application where temporary live preview images (e.g., `blob:` URLs representing intermediate steps of generation) and images from aborted/skipped/failed runs are added to the session History tab. The expected behavior is that the History tab must ONLY contain successfully completed final images from generations.

## Functional Requirements
1. **Successful Final Images Only**: The History tab must only collect and display images that have successfully completed generation.
2. **Exclude Previews**: Intermediate live preview images (the stream of step-by-step images generated during KSampler/sampling stages) must never be added to the History tab.
3. **Exclude Skipped/Aborted/Failed runs**: If a generation is skipped, cancelled, or fails to complete successfully, no partial preview or placeholder image from that run should be added to the History tab.
4. **Identify and Fix History Addition Trigger**: 
   - Remove the fallback logic in `static/app.js` under the `executing` with `node === null` event handler that attempts to grab and add whatever image is currently inside the gallery slot.
   - Restructure history additions to occur exclusively when a final image output event is received (`eventType === 2` binary final image or `type === 'executed'` JSON message outputting final images).

## Non-Functional Requirements
- **Performance**: History rendering and storage updates should remain responsive and fast.
- **State Integrity**: Session history must continue to be updated dynamically in the lightbox context list when a new successful image is generated.

## Acceptance Criteria
- Running a generation to completion adds only the final image to the History tab.
- Intermediate live previews generated during the run do not appear in the History tab.
- Skipping or interrupting a generation does not add any item to the History tab.
- Re-running multiple generations only accumulates final successful images in the History tab.
- All existing and new automated integration tests pass.

## Out of Scope
- Backend persistence of image history across refreshes (already handled/reset per current fresh session specifications).
