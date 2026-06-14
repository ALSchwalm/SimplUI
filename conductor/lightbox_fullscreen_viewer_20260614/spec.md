# Specification: Lightbox Full Screen Image Viewer

## Overview
This track implements a full screen lightbox viewer for generated images and historical images. Clicking on any image in the batch results gallery or the history sidebar tab will open a high-resolution, full screen view. Users can navigate through the respective set of images (gallery or history) using keyboard shortcuts or by clicking the left/right halves of the image.

## Functional Requirements
1. **Triggering Full Screen:**
   - Clicking any image in the Batch Results gallery or the History tab sidebar must open the full screen lightbox overlay.
2. **Visual Presentation (Lightbox):**
   - The lightbox must feature a semi-translucent dark backdrop (`rgba(0, 0, 0, 0.85)`) with a blur effect (`backdrop-filter: blur(8px)`).
   - The active image must be scaled to fit the viewport using `object-fit: contain` to preserve its aspect ratio without cropping.
   - A visible floating close button (e.g. cross icon) must be positioned in the top-right corner.
3. **Navigation Controls:**
   - **Keyboard navigation:** Pressing the `ArrowLeft` key navigates to the previous image, `ArrowRight` navigates to the next image, and `Escape` closes the lightbox.
   - **Click navigation:** Clicking the left 50% area of the visible image must navigate to the previous image, and clicking the right 50% must navigate to the next image.
   - **Backdrop exit:** Clicking the translucent background outside the image boundaries must close the lightbox.
4. **Mobile Back Button Integration:**
   - On mobile devices, triggering the system or browser back navigation (back button or swipe gesture) while the lightbox is active must close the lightbox rather than navigating to the previous website/page in browser history.
   - This must be implemented using browser history state management (`history.pushState` and the `popstate` event listener) when opening and closing the lightbox.
5. **Context-Aware Scopes:**
   - If the viewer is opened from a Batch Results gallery item, navigation must cycle through all currently visible batch result images.
   - If the viewer is opened from a History tab item, navigation must cycle through all historical images currently loaded in the history sidebar tab.
6. **Looping Behavior:**
   - Navigation must loop around seamlessly (navigating past the last image returns to the first, and navigating before the first returns to the last).
7. **Transitions:**
   - Swapping between images in the lightbox must be instantaneous (no transition animations).

## Acceptance Criteria
- Clicking any gallery or history image opens the lightbox.
- Pressing Escape, clicking the close button/backdrop, or triggering browser back on mobile exits the lightbox.
- Keyboard Left/Right arrow keys navigate through the images of the active context (gallery or history) and loop at boundaries.
- Clicking the left half of the image goes back; clicking the right half goes forward.
- Images scale cleanly within the lightbox and retain correct aspect ratios.
