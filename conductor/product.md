# Initial Concept

This will be a gradio project that acts as a wrapper/proxy for comfyui workflows. It will allow a user that knows nothing about comfy to select a workflow and generate an image. It will also allow more advanced users to access controls to manpulate the nodes in the workflow.

# Product Guide

## Core Features

### Workflow Selection
- **Configurable Dropdown:** Users will select workflows via a simple dropdown menu.
- **Dynamic Loading:** The available workflows in the list will be configurable by an administrator. Ideally, the system will attempt to programmatically fetch available workflows from the ComfyUI instance if an API is available.

### User Inputs
- **Dynamic Prompt Injection:** Users can enter custom text descriptions via a multi-line textarea.
- **Node-Based Injection:** The application automatically searches for a node titled "Prompt" in the workflow and injects the user's text into it before generation.
- **Live Previews:** Users see real-time, lower-resolution preview images during the generation process, providing immediate visual feedback.
- **Smart Prompt Handling:** The main Prompt box auto-fills with the workflow's default text, and the duplicate input is hidden from the Advanced Controls list to reduce clutter.
- **Batch Results (Gallery):** For batch generations, the application displays results in a responsive gallery limited to 50% of the viewport height, allowing users to view all generated images in real-time as they are completed without excessive scrolling.

### Advanced User Controls
- **Advanced Mode:** The interface will feature an "Advanced" button.
- **Sidebar Controls:** Clicking the "Advanced Controls" checkbox will reveal a sidebar on the right containing detailed controls for manipulating the specific nodes within the selected workflow.
- **Resilient State:** Advanced settings are persisted client-side in the browser, ensuring they survive server restarts without interruption.
- **Smart Widgets:** The UI automatically detects enumeration inputs (like checkpoints or samplers) and replaces textboxes with dropdown menus populated from the server.
- **Seed Control:** The UI automatically detects "seed" inputs, defaulting them to random if 0, and provides a checkbox to easily toggle between fixed and random seeds.

### Connectivity
- **Remote Connection:** The application will connect to a remote ComfyUI server.
- **Configuration:** The URL for the target ComfyUI instance will be configurable.

## Product Goals
- **Ease of Use:** The primary interface will be streamlined and intuitive, ensuring that non-technical users can generate images without understanding the underlying complexity of ComfyUI.
- **Flexibility:** Advanced users will be supported with granular control over node parameters, bridging the gap between simplicity and power.
