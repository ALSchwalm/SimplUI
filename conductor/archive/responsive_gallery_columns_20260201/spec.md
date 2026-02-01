# Responsive Gallery Columns

## Overview
This feature adjusts the layout of the image gallery to be responsive. It ensures optimal viewing on different devices by switching between a single-column view on smaller screens and a two-column view on larger screens.

## Functional Requirements
- **Responsive Layout:** The gallery must dynamically adjust its column count based on the screen width.
- **Mobile View:** On small screens (mobile), the gallery displays 1 column.
- **Desktop View:** On larger screens (tablet/desktop), the gallery displays a maximum of 2 columns.
- **Implementation Strategy:** Utilize custom CSS media queries to adjust the `grid-template-columns` property of the gallery container for different screen widths.

## Non-Functional Requirements
- **Performance:** The layout change should happen effectively instantly on load or resize without visual stutter.
- **Maintainability:** Use standard Gradio API features without custom CSS hacks for the column count if possible.

## Acceptance Criteria
- [ ] Gallery shows 1 column when the viewport is narrow (simulating mobile).
- [ ] Gallery shows 2 columns when the viewport is wide (simulating desktop).
- [ ] No regression in gallery functionality (image selection, display).

## Out of Scope
- Custom CSS breakpoints beyond what Gradio natively supports for the `columns` list input.
- More than 2 columns on extra-wide screens.
