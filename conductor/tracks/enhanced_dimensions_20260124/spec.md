# Specification - Enhanced Dimension Control with View Toggle

## Overview
Improve the flexibility of dimension controls by introducing a toggle between the simplified "Aspect Ratio/Pixel Count" view and the raw "Width/Height" view. The system will intelligently select the appropriate view when loading a workflow based on whether the dimensions match a known preset.

## Functional Requirements

### UI Components
- **View Toggle:** A small button placed below the dimension controls (dropdowns or number inputs).
    - Label: "Show Exact Dimensions" (when in Aspect Ratio mode) / "Show Aspect Ratio" (when in Width/Height mode).
- **Dual Modes:**
    - **Mode A (Simplified):** Displays Aspect Ratio and Pixel Count dropdowns.
    - **Mode B (Exact):** Displays Width and Height numeric inputs.

### Logic & State Management
- **Intelligent Default:** When a workflow is loaded (or re-rendered):
    - Check if the current `width` and `height` exactly match one of the predefined Aspect Ratio / Pixel Count combinations (calculated with 64-pixel rounding).
    - If **Exact Match**: Default to **Mode A (Simplified)** with the correct presets selected.
    - If **No Match**: Default to **Mode B (Exact)** showing the raw numbers.
- **Manual Toggle Behavior:**
    - **Switching to Exact Mode:** Preserve the current underlying `width` and `height` values exactly.
    - **Switching to Simplified Mode:** Calculate the *nearest* Aspect Ratio and Pixel Count based on the current raw dimensions and update the values to match that preset (snapping).

## Non-Functional Requirements
- **State Persistence:** The toggle state (which mode is active) does not need to be persisted across sessions, as it is re-evaluated based on values.

## Acceptance Criteria
- [ ] A toggle button exists below dimension controls.
- [ ] Loading a workflow with 1024x1024 defaults to "Simplified" view (1:1, 1M).
- [ ] Loading a workflow with 1000x1000 defaults to "Exact" view (1000, 1000).
- [ ] Clicking "Show Exact Dimensions" reveals number inputs with current values.
- [ ] Clicking "Show Aspect Ratio" snaps irregular values to the nearest preset and shows dropdowns.
