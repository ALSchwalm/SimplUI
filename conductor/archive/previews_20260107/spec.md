# Spec: Real-time Generation Previews

## Overview
This track enhances the user experience by displaying live preview images during the generation process. This provides immediate visual feedback, similar to the experience in the ComfyUI native interface.

## User Stories
- **Novice User:** I want to see the image taking shape as it generates so I don't have to wait until the very end to see if it's what I wanted.

## Functional Requirements
- **WebSocket Listener Update:** Update `ComfyClient.generate_image` to handle binary preview frames sent by ComfyUI over the WebSocket.
- **Binary Image Decoding:** Detect binary WebSocket messages and decode them as image data (previews).
- **Gradio UI Update:** Ensure the `on_generate` callback yields the preview images immediately to update the `gr.Image` component in real-time.
- **Seamless Transition:** The final high-quality image should naturally replace the last preview image once generation is complete.

## Technical Requirements
- Update `ComfyClient.generate_image` to process binary messages (which ComfyUI uses for previews).
- Identify the binary message format (usually starts with a 4-byte or 8-byte header indicating the image type).
- Update the Gradio generator loop to yield these intermediate preview images.

## Acceptance Criteria
- While an image is generating, the UI updates with lower-resolution preview images.
- The status text continues to show progress alongside the previews.
- The final image is displayed correctly at the end.
- No regression in connectivity or final image retrieval.
