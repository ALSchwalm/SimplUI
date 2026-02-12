# Specification: Fix Prompt Injection for z-image Workflow

## Overview
This track addresses a bug where the main prompt input is not correctly injected into the `z-image.json` workflow. While the generation proceeds, it uses the default text within the workflow node instead of the user-provided input. Initial investigation suggests the target node is titled "Prompt," but it may not be correctly identified or modified due to its specific node type or internal structure.

## Functional Requirements
- **Accurate Node Identification:** The application must correctly identify the "Prompt" node within the `z-image.json` workflow regardless of its specific node type (e.g., `CLIPTextEncode`, `CustomPromptNode`, etc.).
- **Successful Injection:** The text entered in the main UI prompt area must reliably overwrite the default text in the identified "Prompt" node before the workflow is sent to the ComfyUI server.
- **Workflow-Specific Fix:** Ensure the fix resolves the issue for `z-image.json` without regressing prompt injection for other workflows (e.g., `test.json`, `real.json`).

## Non-Functional Requirements
- **Maintainability:** The solution should improve the robustness of the prompt node detection logic to handle variations in node types that serve as prompts.

## Acceptance Criteria
- [ ] When `z-image.json` is selected and a custom prompt is entered, the generated image reflects the custom prompt rather than the workflow's default text.
- [ ] Automated tests confirm that the "Prompt" node in `z-image.json` is correctly found and updated by the `comfy_client` or relevant utility.
- [ ] Existing workflows (`test.json`, `real.json`) continue to handle prompt injection correctly.

## Out of Scope
- Redesigning the entire workflow parsing logic.
- Adding support for multiple prompt nodes within a single workflow.
