# Specification - Reorganize Aspect Ratio Presets

## Overview
This track reorganizes the predefined list of aspect ratio options in the user interface and backend helper logic. Currently, the aspect ratios are ordered as `["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "7:9", "9:7", "1:2", "2:1"]`. We will sort these options sequentially from tallest to widest to improve user experience, scannability, and intuitive navigation.

## Functional Requirements
1. **Sorted Presets List**:
   - Reorder the aspect ratio presets in both the frontend (`static/app.js`) and backend (`src/dimension_utils.py`) to:
     `["1:2", "9:16", "2:3", "3:4", "7:9", "1:1", "9:7", "4:3", "3:2", "16:9", "2:1"]`
2. **Behavioral Consistency**:
   - When loading workflows or mapping custom dimensions, the system must continue to search for the nearest preset.
   - If no custom dimensions can be matched to a preset, the default fallback selection remains `1:1`.
3. **Unit Tests**:
   - Update tests in `tests/test_dimension_utils.py` to ensure all functionality is preserved under the new sorted list.

## Non-Functional Requirements
- **Performance**: Dimension conversion calculations and preset matching must remain near-instantaneous.
- **Consistency**: Both Python and JavaScript preset tables must contain exactly matching options in the identical order.

## Acceptance Criteria
- [ ] The Aspect Ratio dropdown in the UI lists the options in the exact sorted order: `1:2`, `9:16`, `2:3`, `3:4`, `7:9`, `1:1`, `9:7`, `4:3`, `3:2`, `16:9`, `2:1`.
- [ ] Changing raw width/height input in custom dimensions snaps correctly to the nearest reordered preset when switching back to aspect ratio mode.
- [ ] The Python backend `ASPECT_RATIOS` list is identical and in the same order as the frontend JavaScript list.
- [ ] All Python unit tests run and pass.

## Out of Scope
- Adding new aspect ratio presets.
- Changing resolution/pixel count options.
