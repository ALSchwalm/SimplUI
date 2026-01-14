# Spec: Fix Preview Panel Flickering

## Overview
This track addresses a visual bug where the preview panel flickers during image generation. The flickering occurs on every update, suggesting that the image component is briefly clearing or displaying a blank state before the new preview frame is rendered. The goal is to ensure smooth transitions between preview updates without any visible clearing.

## Functional Requirements
- **Smooth Preview Updates:** The preview image must update in real-time during generation without any visible flickering or flashing of white/blank space.
- **Consistent Display:** The previous preview image must remain visible until the new preview image is fully ready and rendered.

## Technical Requirements
- **Investigate `gr.Image` Behavior:** Analyze how the `gr.Image` component handles updates in the current Gradio version.
- **Optimize Update Logic:** Modify the client-side handling or the way data is yielded to the `gr.Image` component to prevent the `src` attribute from being cleared or reset between updates.
- **Verify WebSocket Data:** Ensure the WebSocket is sending valid image data for every frame and not sending empty/null payloads that might cause the clear.

## Acceptance Criteria
- Start a generation with a workflow that produces intermediate previews.
- Observe the preview panel during the generation process.
- **Success:** The preview image updates continuously and smoothly with no visible flicker or blank frames between updates.
