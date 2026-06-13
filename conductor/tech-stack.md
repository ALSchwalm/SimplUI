# Technology Stack

## Backend
- **Language:** Python (3.11+)
- **Framework:** FastAPI (for serving static assets and config API)
- **Session State:** Client-side only (localStorage/browser state)
- **API Communication:** Synchronous HTTP in Python is no longer used for generation; the client browser directly requests ComfyUI.

## Frontend
- **Framework:** Vanilla HTML, JavaScript, and CSS (Zero build step, direct ComfyUI WebSocket/HTTP communication)
- **Styling:** Custom CSS featuring a premium dark theme, glassmorphism sidebar, and responsive gallery layout.

*Change Note (June 13, 2026):* Rewritten from Gradio to a static frontend architecture with a FastAPI backend to eliminate proxy overhead and allow direct client-to-ComfyUI websocket/HTTP integration.


## Infrastructure & Connectivity
- **Target System:** Remote ComfyUI instance (configurable URL).
- **Communication Protocol:** HTTP/JSON for REST API and WebSocket for real-time updates.

## Tooling
- **Formatting:** `black` (configured for 100-character line length)

## Testing
- **Unit & Integration:** `pytest`, `pytest-cov`, `pytest-asyncio`
- **UI Automation:** `playwright`, `pytest-playwright` (Headless Chromium)
- **Backend Mocking:** `unittest.mock` for ComfyUI API simulation
