# Spec: Smarter Advanced Controls

## Overview
This track enhances the Advanced Controls UI by replacing generic textboxes with context-aware dropdown menus. It leverages ComfyUI's metadata to provide users with valid choices for parameters like checkpoints, samplers, and schedulers.

## User Stories
- **Advanced User:** I want to see a list of available checkpoints and samplers so I don't have to remember their exact filenames or names.

## Functional Requirements
- **Metadata Retrieval:** Implement fetching of node definitions from ComfyUI via the `/object_info` endpoint.
- **Dynamic Widget Selection:** When rendering the Advanced Controls sidebar:
    - Cross-reference each node's `class_type` with the retrieved object info.
    - If an input field has a defined set of possible values (a list), render a `gr.Dropdown` instead of a `gr.Textbox`.
- **Fallback Behavior:** If `/object_info` cannot be retrieved or a node type is missing from the metadata, show an error message in the UI for that node or input.

## Technical Requirements
- Update `ComfyClient` to include a `get_object_info()` method.
- Update `src/ui.py`:
    - Cache the object info on app startup or upon the first workflow load.
    - Update `extract_workflow_inputs` to optionally accept the object info.
    - Update the dynamic render loop to handle list types by creating `gr.Dropdown`.

## Acceptance Criteria
- Parameters like `sampler_name`, `scheduler`, and `ckpt_name` appear as dropdowns in the Advanced Controls.
- The dropdown options match the actual files/settings available on the ComfyUI server.
- Non-list inputs (like `steps`, `cfg`) remain as `gr.Number` or `gr.Textbox`.
- UI automation tests verify that dropdowns are correctly rendered for specific node types.
