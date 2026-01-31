# Specification: Fix Text Input Stuttering in Node Controls

## Overview
Users experience "stuttering" and text loss when typing in text boxes within the "Node Controls" sidebar. This is caused by the UI sending updates to the server on every keypress, which triggers re-renders or state updates that interrupt the user's typing. This track will modify the input behavior to only send updates on "submit" (Enter key) or "blur" (losing focus).

## Functional Requirements

1.  **Modified Input Trigger:**
    -   All text-based inputs (Textboxes, Numbers) within the "Node Controls" sidebar must be updated to trigger their state updates only on `submit` or `blur`.
    -   Remove `change` event listeners that trigger on every keypress for these specific components.

2.  **Scope:**
    -   Applies to all inputs generated dynamically within the `render_dynamic_interface` function in `src/ui.py`.
    -   Does **NOT** apply to the main Prompt input box.

3.  **Consistency & Race Conditions:**
    -   Ensure that if a user is typing and immediately clicks the "Generate" button, the blur event is processed correctly, and the new value is persisted before the generation starts.

## Technical Implementation (Proposed)
-   In `src/ui.py`, locate the component definitions within the dynamic render loop.
-   Change the event attachment from `.change()` to `.blur()` and/or ensure `blur` is handled. 
-   *Note: Gradio components like `gr.Textbox` and `gr.Number` support `blur` events or can be configured to only trigger on certain interactions.*

## Acceptance Criteria
-   Typing in any text box in the "Node Controls" sidebar does not cause stuttering or loss of focus.
-   Values are correctly saved when the user presses Enter.
-   Values are correctly saved when the user clicks away from the input.
-   The "Generate" button correctly uses the latest value from a currently focused input.

## Out of Scope
-   Changes to non-text inputs (Sliders, Checkboxes, Dropdowns) unless they exhibit similar stuttering issues.
-   Changes to the main Prompt box.
