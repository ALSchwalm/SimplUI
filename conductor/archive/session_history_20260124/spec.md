# Specification - Session History Feature

## Overview
Introduce a "History" tab within the advanced controls sidebar to collect and display all final images generated during the current session. This feature provides users with a convenient way to review their past work without losing track of previous results as new generations are triggered.

## Functional Requirements

### UI Components
- **Tab Placement:** Add a new tab titled "History" alongside the existing "Node Controls" tab in the right sidebar.
- **Display Type:** Use a `gr.Gallery` component within the History tab to display images.
- **Ordering:** Images should be displayed in "Oldest First" order, meaning new images are appended to the end of the collection.

### History Logic
- **Content:** The history gallery must contain only final generated images. Intermediate preview images must be excluded.
- **Aggregation:** Every final image produced by a workflow execution (including individual items in a batch) must be automatically added to the History gallery upon completion.
- **Lifecycle:** The history is session-based. It persists as long as the application is running and the browser tab is open, but it is reset if the page is refreshed or the server restarts.
- **Interactivity:** For this initial version, the history is "View Only". No controls for deleting or re-ordering images are required.

## Non-Functional Requirements
- **Performance:** Appending images to the history should not noticeably degrade the performance of the generation loop or the UI responsiveness.

## Acceptance Criteria
- [ ] A "History" tab is visible next to "Node Controls".
- [ ] Successfully generated images appear in the History gallery.
- [ ] Previews do not appear in the History gallery.
- [ ] History persists across multiple "Generate" clicks in the same session.
- [ ] History resets upon page refresh.

## Out of Scope
- Permanent storage (database or local file system persistence).
- "Clear History" or "Delete Item" functionality.
- Filtering or searching history.
