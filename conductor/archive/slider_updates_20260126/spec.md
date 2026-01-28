# Specification: Release-Only Slider Updates

## Overview
Currently, dragging numeric sliders in the Advanced Controls panel sends a continuous stream of updates to the backend. This results in UI stuttering and "jumping" as the backend struggles to keep up with the volume of requests. This track will modify the slider behavior to only trigger updates when the user releases the mouse button.

## Functional Requirements
- Modify all numeric sliders in the "Advanced Controls" node panel.
- Disable continuous updates (live triggering) while the slider is being dragged.
- Ensure the final value is sent to the backend only once, upon mouse release.
- Maintain immediate visual feedback (the slider handle moving) without triggering the backend call.

## Non-Functional Requirements
- Performance: Significantly reduce the number of API calls during slider interaction.
- Responsiveness: Eliminate UI stuttering caused by excessive backend communication.

## Acceptance Criteria
- [ ] Dragging a slider does not trigger a backend request until the mouse is released.
- [ ] The UI remains smooth and responsive during the drag operation.
- [ ] Upon release, the backend receives the correct final value.
- [ ] All numeric sliders (CFG, Steps, Seeds, etc.) exhibit this new behavior.

## Out of Scope
- Debouncing or throttling (Release-only was explicitly chosen).
- Modifying other input types (textboxes, dropdowns).
