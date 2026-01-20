# Specification - UI Refinement: Header Removal and Width Constraint

## Overview
This track aims to streamline the user interface by removing the explicit page header and improving the layout on widescreen displays by introducing a maximum width constraint.

## Functional Requirements
- **Header Removal:** Remove the Markdown header "# Simpl2 ComfyUI Wrapper" from the top of the application.
- **Max-Width Constraint:** The application layout must be constrained to a maximum width of `1280px`.
- **Centering:** When the screen is wider than `1280px`, the application container should be centered horizontally.
- **Persistence:** The browser tab title (configured in `gr.Blocks(title=...)`) must be preserved.

## Technical Details
- **File Targeting:** Modify `src/ui.py`.
- **Styling:** Inject CSS via the `css` parameter in the `gr.Blocks` constructor or `demo.launch`. 
    - The target for width constraint is typically the `.gradio-container` or a top-level wrapper div.
    - CSS rule: `max-width: 1280px; margin: 0 auto;`

## Acceptance Criteria
- [ ] The text "Simpl2 ComfyUI Wrapper" is no longer visible at the top of the page.
- [ ] On displays wider than 1280px, the application content does not exceed that width.
- [ ] The application remains centered on widescreen displays.
- [ ] Browser tab title still reads "Simpl2 ComfyUI Wrapper".

## Out of Scope
- Adding new navigation elements.
- Changing the theme or color palette.
