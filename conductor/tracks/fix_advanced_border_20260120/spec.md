# Spec: Fix Advanced Controls Border

## Overview
There is a layout regression where a border is visible around the "Advanced Controls" toggle area. Although the `gr.Checkbox` has `container=False` set, the parent `gr.Row()` container is likely contributing an unwanted border or padding that disrupts the intended clean UI look.

## Functional Requirements
- Remove the unwanted border surrounding the "Advanced Controls" checkbox.
- Ensure the checkbox remains correctly positioned below the Prompt/Generate area.
- Maintain the existing functionality where toggling the checkbox reveals/hides the advanced sidebar.

## Non-Functional Requirements
- The UI should remain responsive and consistent with the rest of the application's minimalist aesthetic.

## Acceptance Criteria
- [ ] No border is visible around the "Advanced Controls" label and checkbox.
- [ ] The toggle functionality for the Advanced Controls sidebar continues to work perfectly.
- [ ] UI tests for the "Advanced Controls" toggle still pass.

## Out of Scope
- Redesigning the Advanced Controls sidebar itself.
- Changing the behavior of the prompt or generation logic.
