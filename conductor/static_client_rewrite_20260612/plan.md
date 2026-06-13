# Implementation Plan: Static Client & FastAPI Rewrite

## Phase 1: Backend Setup
- [ ] Task: Setup FastAPI app and config API endpoints
    - [ ] Write unit tests for FastAPI config and workflow APIs
    - [ ] Implement FastAPI app inside `main.py`
    - [ ] Expose GET `/api/config` returning the resolved ComfyUI URL and available workflows
    - [ ] Verify all tests pass
    - [ ] Commit code changes with proper message
- [ ] Task: Serve static assets
    - [ ] Write unit tests verifying static file serving routing
    - [ ] Configure FastAPI to mount a static directory `/static` and serve `index.html` at root `/`
    - [ ] Verify all tests pass
    - [ ] Commit code changes with proper message
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend Setup' (Protocol in workflow.md)

## Phase 2: Frontend Foundation & Core UI
- [ ] Task: Create static files and layout
    - [ ] Create `static/index.html` structure with clean, semantic HTML
    - [ ] Create `static/styles.css` with dark mode, premium typography, glassmorphism, responsive batch gallery
    - [ ] Verify layout visually
    - [ ] Commit code changes with proper message
- [ ] Task: Load Config and Workflows
    - [ ] Implement client-side `static/app.js` to fetch `/api/config` and populate workflow dropdown
    - [ ] Establish initial UI structure and connection status indicator
    - [ ] Commit code changes with proper message
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend Foundation & Core UI' (Protocol in workflow.md)

## Phase 3: Client-Side ComfyUI Integration
- [ ] Task: Node discovery and UI control generation
    - [ ] Implement client-side logic to load workflow JSON and discover nodes (Prompt, Width/Height, Seed, etc.)
    - [ ] Dynamically render widgets in Advanced Sidebar
    - [ ] Add Aspect Ratio simplified widget & toggle
    - [ ] Add Seed control randomize toggle
    - [ ] Commit code changes with proper message
- [ ] Task: Generation connection & WebSocket handling
    - [ ] Implement direct connection to ComfyUI websocket and HTTP `/prompt`
    - [ ] Implement submission, execution tracking, and real-time live preview rendering in JS
    - [ ] Implement batch generation loop (1-20), seed generation per iteration, and "Skip" button
    - [ ] Implement local storage state saving
    - [ ] Commit code changes with proper message
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Client-Side ComfyUI Integration' (Protocol in workflow.md)

## Phase 4: Cleanup & Quality Verification
- [ ] Task: Remove old Gradio code
    - [ ] Delete or clean up unused python files (e.g. `src/ui.py`)
    - [ ] Clean up requirements or config
    - [ ] Verify test suite passes
    - [ ] Commit code changes with proper message
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Cleanup & Quality Verification' (Protocol in workflow.md)
