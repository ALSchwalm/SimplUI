# Spec: Advanced Slider Controls

## Overview
This track introduces the ability to render numeric inputs as sliders with customized ranges. It addresses the issue where ComfyUI's default ranges are sometimes too broad or inappropriate for a user-friendly UI.

## Functional Requirements
- **Slider Rendering:** Support `gr.Slider` for numeric inputs.
- **Hardcoded Defaults:** Include a built-in mapping of common node parameters (e.g., `steps`, `cfg`) to sensible slider ranges (min, max, step).
- **Configurable Overrides:** Allow administrators to define or override slider ranges in `config.json`.
- **Automatic Range Adoption:** If no override exists but `object_info` provides a min/max, use `gr.Slider` with those values.
- **Input Type Inference:** A numeric input becomes a slider if a range (min/max) can be determined from either the config or the server metadata.

## Technical Requirements
- Update `config.json` schema to support a `slider_overrides` field.
- Update `ConfigManager` to load and merge hardcoded defaults with `config.json` overrides.
- Update `extract_workflow_inputs` in `src/ui.py` to:
    - Tag numeric inputs as `slider` if range data is found.
    - Store `min`, `max`, and `step` values.
- Update the dynamic render loop to handle `type="slider"` by creating `gr.Slider`.

## Acceptance Criteria
- "steps" and "cfg" appear as sliders by default.
- Custom ranges defined in `config.json` are respected.
- Sliders correctly update the `overrides_store`.
- Sliders survive server restarts (resilience check).
