# Initial Concept

This will be a gradio project that acts as a wrapper/proxy for comfyui workflows. It will allow a user that knows nothing about comfy to select a workflow and generate an image. It will also allow more advanced users to access controls to manpulate the nodes in the workflow.

# Product Guide

## Core Features

### Workflow Selection
- **Configurable Dropdown:** Users will select workflows via a simple dropdown menu.
- **Dynamic Loading:** The available workflows in the list will be configurable by an administrator. Ideally, the system will attempt to programmatically fetch available workflows from the ComfyUI instance if an API is available.

### Advanced User Controls
- **Advanced Mode:** The interface will feature an "Advanced" button.
- **Sidebar Controls:** Clicking the "Advanced" button will reveal a sidebar containing detailed controls for manipulating the specific nodes within the selected workflow.

### Connectivity
- **Remote Connection:** The application will connect to a remote ComfyUI server.
- **Configuration:** The URL for the target ComfyUI instance will be configurable.

## Product Goals
- **Ease of Use:** The primary interface will be streamlined and intuitive, ensuring that non-technical users can generate images without understanding the underlying complexity of ComfyUI.
- **Flexibility:** Advanced users will be supported with granular control over node parameters, bridging the gap between simplicity and power.
