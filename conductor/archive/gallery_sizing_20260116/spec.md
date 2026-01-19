# Specification - Fix: Image Gallery Sizing

## Overview
Currently, generated images and live previews are displayed at their full resolution, which often exceeds the available screen space, forcing users to scroll to see the whole image. This track will restrict the Gallery container to a responsive height and ensure all images scale to fit within that area using "contain" logic.

## Functional Requirements
- **Responsive Height Limit:** The Gallery component must be constrained to a maximum height of 70% of the viewport height (`50vh`) to ensure other UI elements remain visible.
- **Contain Scaling:** Both live preview images and final generated images must scale down to fit entirely within the gallery bounds while maintaining their original aspect ratio.
- **No Cropping:** The implementation must ensure no parts of the image are cropped or hidden.

## Technical Details
- **Component Targeting:** Modify the `gr.Gallery` component in `src/ui.py` (elem_id: `gallery`).
- **Styling:** Use Gradio's `height` parameter or custom CSS injected via `gr.Blocks(css=...)` to enforce the `50vh` constraint and ensure the internal image container respects the `contain` object-fit.

## Acceptance Criteria
- [ ] The image gallery container does not exceed 70% of the browser window height.
- [ ] Large images (e.g., 1024x1024 or portrait) are scaled down to fit fully inside the gallery.
- [ ] Aspect ratios of generated images are preserved (no stretching).
- [ ] Scrolling within the gallery container is eliminated for standard image sizes.

## Out of Scope
- Adding a "Download" button to individual images.
- Implementing a full-screen zoom or lightbox feature.
