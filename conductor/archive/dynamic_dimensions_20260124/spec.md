# Specification - Dynamic Aspect Ratio and Resolution Control

## Overview
Transform how image dimensions are handled in the UI. Instead of raw width and height inputs, nodes with dimension parameters will feature user-friendly "Aspect Ratio" and "Target Pixel Count" dropdowns. The application will internally calculate and inject the correct pixel dimensions, optimized for generative models.

## Functional Requirements

### UI Components
- **Inputs:** Replace raw `width` and `height` inputs with two dropdown menus:
    - **Aspect Ratio:** Options include 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3, 7:9, 9:7, 1:2, and 2:1.
    - **Target Pixels (Millions):** Options include 0.25M, 0.5M, 1M, 1.5M, and 2M.
- **Node Detection:** Automatically identify nodes containing both `width` and `height` inputs to apply this transformation.

### Calculation Logic
- **Internal Mapping:** The "1M" target specifically maps to $1024 \times 1024$ ($1,048,576$ pixels) to align with standard model training.
- **Formula:** 
    - Given $R$ (Aspect Ratio width/height) and $P$ (Total Pixels):
    - $Height = \sqrt{P/R}$
    - $Width = Height \times R$
- **Optimization:** Calculated dimensions must be rounded to the nearest multiple of **64** to ensure compatibility with modern generative models (like SDXL).

## Non-Functional Requirements
- **Transparency:** The `overrides_store` will store the final calculated width/height values, ensuring they are correctly injected into the ComfyUI workflow.

## Acceptance Criteria
- [ ] Nodes with width/height inputs show Aspect Ratio and Pixel Count dropdowns instead.
- [ ] Selecting "1:1" and "1M" results in internal dimensions of $1024 \times 1024$.
- [ ] All calculated dimensions are multiples of 64.
- [ ] State persistence works for the new dropdown values.

## Out of Scope
- Custom manual width/height entry (user must use the dropdowns).
- Support for models requiring rounding to 8 or other specific increments (Fixed to 64 for now).
