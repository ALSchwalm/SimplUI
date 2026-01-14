# Spec: Dynamic Prompt Injection

## Overview
This track introduces the ability for users to provide custom text prompts that are dynamically injected into the selected ComfyUI workflow. This moves beyond static workflows to allow for user-driven generation.

## User Stories
- **Novice User:** I want to type a description of an image and have it generated using my selected workflow.

## Functional Requirements
- **Gradio UI Update:** Add a multi-line textarea for "Prompt" input below the workflow dropdown.
- **Node Discovery:** When a workflow is loaded, search for a node with the title "Prompt" (case-insensitive).
- **Prompt Injection:** If a "Prompt" node is found, update its text input field with the user's provided prompt before submission to ComfyUI.
- **Fallback Behavior:** If no "Prompt" node is found, the generation should proceed using the workflow's default settings, and the custom prompt will be ignored (optionally, the input field could be visually disabled or hidden).

## Technical Requirements
- Update `ComfyClient` to support modifying the workflow dictionary before submission.
- Update `handle_generation` in `src/ui.py` to accept the prompt text and perform the injection.

## Acceptance Criteria
- User can enter text into a new textarea.
- If the workflow has a node titled "Prompt", that text is used in the generation.
- If no such node exists, the workflow runs as-is without error.
- Tests verify the search and injection logic.
