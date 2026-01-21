# Spec: Move Workflow Selection to Advanced Controls

## Overview
To streamline the user experience for non-technical users, we will hide the "Select Workflow" dropdown from the primary interface and move it into the "Advanced Controls" sidebar. The application will default to the first workflow listed in the configuration. Only users who enable "Advanced Controls" will be able to switch workflows.

## Functional Requirements
- **Basic UI (Advanced Controls OFF):**
    - The "Select Workflow" dropdown is completely hidden.
    - The application automatically uses the first workflow defined in `config.json` (as per current behavior).
    - No workflow name or status is displayed to the user.
- **Advanced UI (Advanced Controls ON):**
    - The "Select Workflow" dropdown is visible at the very top of the "Advanced Controls" sidebar.
    - Changing the workflow in the sidebar correctly updates the available node controls and the prompt default value.
- **Persistence:**
    - The selected workflow state must be maintained correctly between toggling the advanced view.

## Non-Functional Requirements
- Maintain existing responsiveness and layout stability.
- Ensure the sidebar transition remains smooth.

## Acceptance Criteria
- [ ] When the app loads, the "Select Workflow" dropdown is not visible in the main column.
- [ ] Generation works using the default (first) workflow without any user selection.
- [ ] Toggling "Advanced Controls" reveals the "Select Workflow" dropdown at the top of the sidebar.
- [ ] Changing the workflow in the sidebar updates the prompt and the dynamic node controls.
- [ ] UI tests for workflow switching are updated to reflect the new location.

## Out of Scope
- Adding a dedicated "Settings" page or tab.
- Modifying the workflow loading logic or `config.json` structure.
