# Technology Stack

## Backend
- **Language:** Python
- **API Communication:** `requests` (Synchronous HTTP for workflow submission and metadata retrieval)
- **Real-time Communication:** `websockets` (For streaming image generation progress and binary image data from ComfyUI)

## Frontend
- **Framework:** Gradio
- **Styling:** Standard Gradio themes with custom CSS for the integrated sidebar.

## Infrastructure & Connectivity
- **Target System:** Remote ComfyUI instance (configurable URL).
- **Communication Protocol:** HTTP/JSON for REST API and WebSocket for real-time updates.
