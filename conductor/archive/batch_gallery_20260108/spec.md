# Spec: Batch Image Support (Gallery)

## Overview
This track fixes a bug where only the first image of a batch generation is displayed. It replaces the single image output with a `gr.Gallery` component to support multiple outputs and real-time updates.

## Functional Requirements
- **Gradio UI Update:** Replace `gr.Image` with `gr.Gallery` in the main output area.
- **Real-time Gallery Updates:** As `ComfyClient` yields new images from the WebSocket (`executed` events), append them to the gallery list.
- **Preview Handling:** Show the latest preview image. For batches, this should update the "current" view until a final image is ready.
- **State Management:** Maintain a list of generated images for the current session/request to populate the gallery.

## Technical Requirements
- Update `src/ui.py`:
    - Change `output_image = gr.Image(...)` to `output_gallery = gr.Gallery(...)`.
    - Update `handle_generation` to maintain a list of completed images.
    - Yield the updated list to the `gr.Gallery` component.

## Acceptance Criteria
- Set batch size > 1 in Advanced Controls.
- Click Generate.
- Images appear in the gallery as they finish.
- Previews are visible during the process.
- All images in the batch are accessible at the end.
