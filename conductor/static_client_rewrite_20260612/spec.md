# Specification: Static Client & FastAPI Rewrite

## Overview
Rewrite SimplUI from a Python-based Gradio proxy/wrapper to a FastAPI-based server serving a premium, single-page Vanilla HTML/CSS/JS client application. The client will connect directly to the ComfyUI HTTP/WebSocket APIs, handling all workflow logic, prompt injection, and preview parsing in browser JavaScript. The simplui backend will only serve static files, parse CLI options, and expose endpoints to retrieve available workflows and the resolved ComfyUI connection address.

## Functional Requirements

### 1. FastAPI Backend Server
- **Server Core:** Replaced Gradio launcher with FastAPI serving static directory assets (`index.html`, `app.js`, `styles.css`).
- **CLI & Config Parsing:** Retain the parsing of `--comfy-addr`, `--listen-addr`, and `--config` (mapping to `config.json`).
- **Config API Endpoint:** Expose a GET `/api/config` endpoint returning:
  - `comfy_url`: The resolved URL of the ComfyUI server.
  - `workflows`: A list of available workflows with metadata (name, and either path or pre-loaded workflow content).
- **Workflow Content Serving:** Expose a way to retrieve the workflow JSON files (either via GET `/api/workflows/{name}` or pre-embedded in the `/api/config` response).

### 2. Client-Side Web Application (Vanilla HTML/CSS/JS)
- **UI & Layout:** A premium, modern dashboard UI matching the SimplUI Product Definition:
  - Responsive layout (mobile-friendly, single column on small screens, two columns for batch gallery on larger screens).
  - Main area: Textarea prompt input (with auto-focus and `Ctrl+Enter` trigger), "Generate" / "Skip" button, and a batch gallery (limited to 50% viewport height).
  - Advanced Sidebar (collapsible, toggled via "Advanced Controls" checkbox):
    - Workflow selector dropdown.
    - Dynamically generated settings based on the selected workflow's nodes.
    - Aspect Ratio & Pixel Count simplifier for width/height controls.
    - Seed control (numeric input with "Randomize" checkbox).
    - Batch count slider (1-20 sequential iterations).
    - History tab containing generated images in the current session.
- **Direct ComfyUI Integration:**
  - Establish a direct HTTP connection to the ComfyUI server to fetch node configurations (`/object_info`) and submit prompts (`/prompt`).
  - Establish a direct WebSocket connection (`/ws`) to the ComfyUI server to stream generation progress and real-time live preview images.
  - Parse preview images (extracting binary frames from websocket messages) and render them in the gallery.
  - Handle iteration skipping and completion events, saving final images in the session history.
- **Client State Resilience:** Save user advanced controls (selected workflow, seed randomization choice, aspect ratio toggles, etc.) in `localStorage`.

## Non-Functional Requirements
- **High Aesthetics:** Modern CSS featuring dark-themed background, sleek typography, gradients, glassmorphism sidebar, clear focus indicators, and smooth micro-animations.
- **Low Latency:** Zero server-side proxying overhead for prompt generation or image streaming.
- **Coverage & Testability:** Update the unit test suite to test the FastAPI backend API and adapt integration tests for static assets.

## Acceptance Criteria
1. Running `python main.py` parses CLI arguments correctly and launches a FastAPI app on the listen address.
2. Loading the client page calls `/api/config` to resolve the configured ComfyUI address and active workflows.
3. The client establishes connection with ComfyUI and displays status (Connected/Disconnected).
4. Prompt execution, Aspect Ratio controls, Seed randomization, Batching (1-20), Skip function, and live preview image rendering work seamlessly on the client side.
5. All Gradio components are completely removed from the project.
6. The test suite passes.

## Out of Scope
- Server-side image storage (images are managed in-memory or via ComfyUI history/localStorage).
- Authentication and access control.
