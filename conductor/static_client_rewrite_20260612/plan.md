# Implementation Plan: Static Client & FastAPI Rewrite

## Phase 1: Backend Setup [checkpoint: 9e6f9cb]
- [x] Task: Setup FastAPI app and config API endpoints (85be4ac)
    - [x] Write unit tests for FastAPI config and workflow APIs
    - [x] Implement FastAPI app inside `main.py`
    - [x] Expose GET `/api/config` returning the resolved ComfyUI URL and available workflows
    - [x] Verify all tests pass
    - [x] Commit code changes with proper message
- [x] Task: Serve static assets (85be4ac)
    - [x] Write unit tests verifying static file serving routing
    - [x] Configure FastAPI to mount a static directory `/static` and serve `index.html` at root `/`
    - [x] Verify all tests pass
    - [x] Commit code changes with proper message
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend Setup' (Protocol in workflow.md)

## Phase 2: Frontend Foundation & Core UI [checkpoint: 2d49f58]
- [x] Task: Create static files and layout (38df157)
    - [x] Create `static/index.html` structure with clean, semantic HTML
    - [x] Create `static/styles.css` with dark mode, premium typography, glassmorphism, responsive batch gallery
    - [x] Verify layout visually
    - [x] Commit code changes with proper message
- [x] Task: Load Config and Workflows (cc4d697)
    - [x] Implement client-side `static/app.js` to fetch `/api/config` and populate workflow dropdown
    - [x] Establish initial UI structure and connection status indicator
    - [x] Commit code changes with proper message
- [x] Task: Conductor - User Manual Verification 'Phase 2: Frontend Foundation & Core UI' (Protocol in workflow.md)

## Phase 3: Client-Side ComfyUI Integration [checkpoint: a51e167]
- [x] Task: Node discovery and UI control generation (daa6b96)
    - [x] Implement client-side logic to load workflow JSON and discover nodes (Prompt, Width/Height, Seed, etc.)
    - [x] Dynamically render widgets in Advanced Sidebar
    - [x] Add Aspect Ratio simplified widget & toggle
    - [x] Add Seed control randomize toggle
    - [x] Commit code changes with proper message
- [x] Task: Generation connection & WebSocket handling (daa6b96)
    - [x] Implement direct connection to ComfyUI websocket and HTTP `/prompt`
    - [x] Implement submission, execution tracking, and real-time live preview rendering in JS
    - [x] Implement batch generation loop (1-20), seed generation per iteration, and "Skip" button
    - [x] Implement local storage state saving
    - [x] Commit code changes with proper message
- [x] Task: Conductor - User Manual Verification 'Phase 3: Client-Side ComfyUI Integration' (Protocol in workflow.md)

## Phase 4: Cleanup & Quality Verification [checkpoint: b9f56df]
- [x] Task: Remove old Gradio code (551525f)
    - [x] Delete or clean up unused python files (e.g. `src/ui.py`)
    - [x] Clean up requirements or config
    - [x] Verify test suite passes
    - [x] Commit code changes with proper message
- [x] Task: Conductor - User Manual Verification 'Phase 4: Cleanup & Quality Verification' (Protocol in workflow.md)
