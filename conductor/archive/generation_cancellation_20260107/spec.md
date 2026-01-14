# Spec: Generation Cancellation

## Overview
This track implements a mechanism to stop or interrupt an ongoing image generation process. This improves user control and resource management.

## User Stories
- **Novice User:** I clicked "Generate" by mistake or changed my mind, so I want to stop it immediately.
- **Advanced User:** I want to quickly restart a generation with new parameters without waiting for the previous one to finish.

## Functional Requirements
- **Stop Button:** A "Stop" button should be visible in the UI when a generation is active.
- **Auto-Stop on Re-Generate:** Clicking "Generate" while a generation is currently running should automatically interrupt the active generation before starting the new one.
- **Backend Interruption:** The stop action must send an interrupt command to the ComfyUI backend to halt processing and clear the queue for that prompt.

## Technical Requirements
- **ComfyClient Update:** Add an `interrupt()` method that calls the ComfyUI `/interrupt` endpoint.
- **Queue Management:** Add a method to clear the queue (delete queued items) if possible, or rely on interrupt.
- **UI State Management:** Track the "running" state in `src/ui.py`.
- **Button Logic:**
    - Add a "Stop" button component.
    - Update "Generate" logic to check for active runs and call interrupt if needed.
    - Bind "Stop" button to the interrupt function.

## Acceptance Criteria
- Clicking "Stop" halts the current generation and updates the status to "Interrupted".
- Clicking "Generate" while busy stops the current run and starts the new one immediately.
- The ComfyUI server stops processing the interrupted job.
