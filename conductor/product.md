# Initial Concept

This will be a gradio project that acts as a wrapper/proxy for comfyui workflows. It will allow a user that knows nothing about comfy to immediately generate an image using a default workflow. It will also allow more advanced users to switch workflows and access granular controls within the "Advanced Controls" sidebar.

# Product Guide

## Core Features

### Workflow Selection
- **Hidden by Default:** To simplify the experience for basic users, the workflow selection is hidden from the main interface. The application defaults to the first available workflow.
- **Advanced Access:** Users can access the "Select Workflow" dropdown within the "Advanced Controls" sidebar to switch between different workflows.
- **Dynamic Loading:** The available workflows in the list are configurable and update the UI controls dynamically based on the selected workflow's nodes.

### User Inputs
- **Dynamic Prompt Injection:** Users can enter custom text descriptions via a multi-line textarea.
- **Node-Based Injection:** The application automatically searches for a node titled "Prompt" in the workflow and injects the user's text into it before generation.
- **Live Previews:** Users see real-time, lower-resolution preview images during the generation process, providing immediate visual feedback.
- **Smart Prompt Handling:** The main Prompt box auto-fills with the workflow's default text, and the duplicate input is hidden from the Advanced Controls list to reduce clutter.
- **Batch Results (Gallery):** For batch generations, the application displays results in a responsive gallery limited to 50% of the viewport height, allowing users to view all generated images in real-time as they are completed without excessive scrolling.
- **Skip Functionality:** During generation, the 'Generate' button is replaced by a 'Skip' button. Clicking 'Skip' immediately cancels the current iteration and moves to the next item in the batch, removing any partial preview from the gallery while preserving completed images.

### Advanced User Controls
- **Advanced Mode:** The interface will feature an "Advanced" button.
- **Sidebar Controls:** Clicking the "Advanced Controls" checkbox will reveal a sidebar on the right containing detailed controls for manipulating the specific nodes within the selected workflow.
- **History Tab:** A dedicated "History" tab within the advanced sidebar collects and displays all final images generated during the current session, excluding intermediate previews.
- **Resilient State:** Advanced settings are persisted client-side in the browser, ensuring they survive server restarts without interruption.
- **Smart Widgets:** The UI automatically detects enumeration inputs (like checkpoints or samplers) and replaces textboxes with dropdown menus populated from the server.
- **Seed Control:** The UI automatically detects "seed" inputs, defaulting them to random if 0. A "Randomize" checkbox toggles between fixed and random seeds. When randomized, the numeric input is hidden to reduce clutter; disabling randomization reveals the specific base seed used.
- **Batch Count:** Users can set the number of iterations (1-20) to run sequentially. Each iteration uses a unique, deterministic seed derived from the base seed, ensuring variety while maintaining reproducibility.

### Connectivity
- **Remote Connection:** The application will connect to a remote ComfyUI server.
- **Configuration:** The URL for the target ComfyUI instance will be configurable.

## Product Goals
- **Ease of Use:** The primary interface will be streamlined and intuitive, ensuring that non-technical users can generate images without understanding the underlying complexity of ComfyUI.
- **Flexibility:** Advanced users will be supported with granular control over node parameters, bridging the gap between simplicity and power.
