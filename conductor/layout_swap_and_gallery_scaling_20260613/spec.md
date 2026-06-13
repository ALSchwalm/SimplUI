# Specification: Layout Swap and Gallery Scaling Updates

## Overview
This track modifies the main page layout by swapping the positions of the Gallery Card and the Prompt Card, placing the Gallery Results above the Prompt Box. It also updates the gallery image scaling constraints to use a 70vh maximum height and an 80vw maximum width for images, removing the forced 1:1 square aspect ratio for slot items.

## Functional Requirements
1. **Layout Swap:**
   - The Gallery Results card (`gallery-card`) must be rendered above the Prompt Card (`prompt-card`) inside the main generation space column.
2. **Gallery Sizing & Scaling:**
   - The `.gallery-card` height and max-height must be set to `70vh` (updated from `50vh`).
   - The `.gallery-item` aspect-ratio must be changed from `1 / 1` to `auto` so that items stretch to fill the height of the gallery grid.
   - The images inside the slots (`.gallery-item img`) must have `max-width: 80vw` and `object-fit: contain` to preserve their correct aspect ratio without stretching or cropping.
3. **Responsive Adaptations:**
   - Keep the mobile responsiveness where the layout switches to a single column, and the gallery grid columns drop to `1fr`.

## Acceptance Criteria
- Layout: Gallery Card is on top, Prompt Card is at the bottom.
- Sizing: The gallery card height is constrained to `70vh` of the viewport.
- Scaling: Images scale dynamically to fit their correct aspect ratio within the 70vh constraint, without being forced into square boxes.
