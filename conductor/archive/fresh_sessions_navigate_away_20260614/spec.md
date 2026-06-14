# Specification: Fresh Sessions & Navigate Away Warning

## Overview
This track changes the behavior of SimplUI on page refresh. Currently, some user settings/workflow overrides are preserved across page reloads using browser local storage. This track ensures that refreshing the page starts a completely fresh session with no memory of the previous one. Additionally, it implements a native browser confirmation dialog warning users when they attempt to navigate away, refresh, or close the page.

## Functional Requirements
1. **Fresh Session on Page Load:**
   - On page load/initialization, the client application must completely clear all client-controlled persisted state in the browser (`localStorage`).
   - This resets all workflow overrides (such as sliders, text inputs, aspect ratios, etc.) and ensures that the session begins with the default workflow settings retrieved from the server.
   - The session history of generated images (`state.history`) must start empty.

2. **Navigate-Away Confirmation Dialog:**
   - The application must register a native browser listener for the `beforeunload` event.
   - The confirmation warning must be triggered always, whenever the user attempts to:
     - Refresh the page (e.g., F5, Ctrl+R, browser refresh button).
     - Close the tab or browser window.
     - Navigate away to a different website/URL.
   - The warning dialog must ask the user to confirm if they want to leave the site and warn them that their changes and session data will be lost.

## Acceptance Criteria
- Loading or refreshing the page clears all saved workflow overrides in `localStorage`.
- Attempting to reload, close, or navigate away from the page prompts the standard native browser unload confirmation dialog.
- The default workflow inputs are restored to their server-defined defaults upon page reload.
