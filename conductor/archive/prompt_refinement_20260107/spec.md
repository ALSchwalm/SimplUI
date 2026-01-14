# Spec: Prompt UI Refinement

## Overview
This track refines the interaction between the main Prompt textarea and the "Prompt" node in the workflow. It ensures the UI is consistent, pre-filled with sensible defaults, and free of confusing duplication.

## User Stories
- **Novice User:** When I select a workflow, I want to see its default prompt so I know what kind of input it expects.
- **Advanced User:** I want a clean sidebar that doesn't show me the same prompt setting twice.

## Functional Requirements
- **Auto-prefill:** When a workflow is selected (or the page loads), the "Prompt" textarea must be automatically populated with the value from the workflow's "Prompt" node.
- **De-duplication:** In the "Advanced Controls" sidebar, the specific input field used for the main Prompt (e.g., node titled "Prompt", field "text") must be hidden to avoid confusion.
- **Dynamic Awareness:** If the "Prompt" node uses a different input name (like "string"), that specific input should be the one pre-filled and hidden.

## Technical Requirements
- Update `render_dynamic_interface` in `src/ui.py` to:
    - Identify the "Prompt" node and its primary text input.
    - Set the `value` of the `prompt_input` textarea to that found value.
    - Filter the `extracted` inputs list to exclude the primary prompt input before rendering the advanced accordion.

## Acceptance Criteria
- Selecting "Test Workflow" fills the Prompt box with its default text (e.g., "A photo of...").
- Opening "Advanced Controls" for that workflow does NOT show the prompt text input field.
- Other inputs for the same node (if any) still appear.
- Clicking Generate still correctly injects the (possibly modified) prompt.
