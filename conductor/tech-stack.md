# Technology Stack

## Backend
- **Language:** Python
- **Session State:** `gr.State` used for managing temporary session data like image history.
- **API Communication:** `requests` (Synchronous HTTP for workflow submission and `/object_info` metadata retrieval)
- **Real-time Communication:** `websockets` (For streaming image generation progress and binary image data from ComfyUI)

## Frontend
- **Framework:** Gradio
- **Styling:** Standard Gradio themes with custom CSS for the integrated sidebar.

## Infrastructure & Connectivity
- **Target System:** Remote ComfyUI instance (configurable URL).
- **Communication Protocol:** HTTP/JSON for REST API and WebSocket for real-time updates.

## Testing
- **Unit & Integration:** `pytest`, `pytest-cov`, `pytest-asyncio`
- **UI Automation:** `playwright`, `pytest-playwright` (Headless Chromium)
- **Backend Mocking:** `unittest.mock` for ComfyUI API simulation
