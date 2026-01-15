# Spec: UI Layout Redesign

## Overview
This track involves a significant redesign of the application's layout to improve usability and ergonomics. The main goal is to transition from a side-by-side layout (Controls vs. Image) to a vertical stack for the primary generation flow, while moving advanced controls to a toggleable sidebar.

## Functional Requirements
- **Vertical Main Flow:**
    - The `gr.Gallery` (output area) will be positioned at the top of the main column.
    - The Prompt area will be positioned directly below the gallery.
- **Prompt Area Layout:**
    - The Prompt textbox will occupy the left portion of this area.
    - The **Generate** and **Stop** buttons will be positioned to the right of the Prompt textbox, stacked vertically.
- **Advanced Controls Sidebar:**
    - An "Advanced Controls" checkbox will be placed below the Prompt/Generate area.
    - Checking this box will reveal a panel on the right side of the screen.
    - This panel will contain all the dynamic node controls (previously in the Accordion).
    - The sidebar will "push" the main content, reducing its width when visible.

## Technical Requirements
- **Gradio Layout Refactoring:**
    - Nest the Gallery and Prompt area inside a primary `gr.Column`.
    - Use `gr.Row` for the Prompt area, containing a `gr.Column` for the textbox and a `gr.Column` (or `gr.Group`) for the vertical buttons.
    - The entire application will be wrapped in a `gr.Row` containing the `Main Column` and the `Sidebar Column`.
- **Visibility Logic:**
    - The Sidebar `gr.Column` will have `visible=False` by default.
    - The "Advanced Controls" checkbox will trigger a visibility update for the Sidebar column.

## Acceptance Criteria
- Upon loading, the Gallery is at the top, and the Prompt/Generate button is below it.
- The Generate button and Stop button are to the right of the Prompt textbox and vertically aligned.
- Clicking the "Advanced Controls" checkbox reveals the sidebar on the right.
- The main content area shrinks smoothly to accommodate the sidebar.
- All generation functionality (progress, gallery updates, previews) remains functional in the new layout.
