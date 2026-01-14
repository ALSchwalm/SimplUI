# Spec: Core Connectivity and Basic Gradio UI

## Overview
This track establishes the foundational connection between the Gradio frontend and a remote ComfyUI backend. It implements the "Novice" user story: selecting a pre-defined workflow and generating an image.

## User Stories
- **Novice User:** I want to select a workflow from a dropdown and click "Generate" to see an image.
- **Administrator:** I want to configure the ComfyUI URL and available workflows.

## Functional Requirements
- Establish a connection to a remote ComfyUI instance via HTTP and WebSockets.
- Retrieve and list available workflows (from a local configuration initially).
- Submit a prompt (workflow JSON) to ComfyUI.
- Listen for progress and the final image via WebSockets.
- Display the generated image in a Gradio UI.

## Technical Constraints
- Language: Python
- Libraries: `gradio`, `requests`, `websockets`
- Architecture: Client-Server (Gradio app acts as a proxy for ComfyUI)
