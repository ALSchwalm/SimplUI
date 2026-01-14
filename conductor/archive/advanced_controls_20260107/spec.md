# Spec: Advanced Node Controls

## Overview
This track enables advanced users to manipulate the properties of ComfyUI nodes directly from the Gradio interface. This provides granular control over the generation process without needing to access the ComfyUI backend directly.

## User Stories
- **Advanced User:** I want to tweak specific parameters (like "steps", "cfg", or "seed") of any node in the workflow to fine-tune my results.

## Functional Requirements
- **Advanced Sidebar:** Add a collapsible sidebar or accordion section titled "Advanced Controls" to the UI.
- **Dynamic Form Generation:** When a workflow is loaded, parse it to identify all nodes and their inputs.
- **Input Widgets:** Automatically generate appropriate Gradio input components for each node property (e.g., `Number` for integers/floats, `Textbox` for strings).
- **State Management:** Store the modified values in the client-side state.
- **Workflow Update:** When "Generate" is clicked, inject the modified values into the workflow before submission.
- **Resilience:** The system should reconstruct the controls based on the selected workflow definition, ensuring that server restarts don't break the UI state as long as the workflow file is available locally.

## Technical Requirements
- Update `src/ui.py` to parse the loaded workflow JSON.
- Create a helper function to generate Gradio components dynamically based on the input types found in the workflow.
- Update `handle_generation` to merge the user's advanced settings into the workflow JSON.
- Use Gradio `State` to track overrides.

## Acceptance Criteria
- Clicking "Advanced Controls" reveals a list of nodes.
- Each node shows its editable parameters.
- Changing a parameter (e.g., KSampler steps) updates the value used in the next generation.
- The default values in the UI match the defaults in the loaded workflow file.
