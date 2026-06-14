# Specification: Relocate Batch Count in Advanced Controls

## Overview
This track relocates the Batch Count settings control to the top of the Advanced Controls sidebar, positioning it directly below the "Select Workflow" dropdown and above the dynamically loaded controls. Additionally, a visual divider/border will be introduced to separate the default controls (workflow selection, batch count) from the dynamic, workflow-specific controls to improve visual organization.

## Functional Requirements
1. **Relocate Batch Count Control:**
   - Move the Batch Count slider and its associated label/value display from the bottom of the "Settings" tab in the Advanced Controls sidebar to the top, directly below the "Select Workflow" dropdown.
   - It must reside above the `dynamic-controls-container` element in the HTML.
2. **Visual Divider/Separation:**
   - Add a styling divider (subtle border, spacing, or horizontal rule) between the default controls (Workflow Select and Batch Count) and the dynamic workflow controls container.
   - The separation must be visually consistent with the existing theme and stylesheet guidelines.
3. **Behavior and Control Preservation:**
   - The Batch Count slider must retain all existing functionality (updating the text label, storing and retrieving batch size, sending iterations sequentially to the backend).
   - Dynamic controls must continue to render correctly below the Batch Count control and the new divider.

## Acceptance Criteria
- The Batch Count slider and label are rendered directly below the "Select Workflow" dropdown and above the dynamically loaded controls.
- A subtle divider/border separates the static controls from the dynamic controls.
- Changing the Batch Count slider updates its displayed value.
- Generating a batch of images continues to function correctly.
- Dynamic controls load and render below the divider without layout regression.
