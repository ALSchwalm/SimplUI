# Track Specification: Project Renaming (Simpl2 -> SimplUI)

## 1. Overview
The project is currently named "Simpl2" (or "simpl2" in some contexts). The goal is to rename the project to "SimplUI" to better reflect its purpose as a simplified user interface for ComfyUI. This renaming will be comprehensive, affecting user-facing elements, internal code references, and documentation, while preserving the root directory name.

## 2. Functional Requirements
- **User Interface:**
  - The browser tab/window title must display "SimplUI" instead of "Simpl2 ComfyUI Wrapper".
  - Any internal UI headers or labels referencing "Simpl2" must be updated to "SimplUI".
- **CLI:**
  - The help text for the command-line interface (e.g., `python main.py --help`) must reference "SimplUI".
- **Codebase:**
  - All internal references to "Simpl2" in comments, log messages, and variable names (if any specific "simpl2" variables exist) must be updated to "SimplUI" or "simpl_ui" as appropriate for the casing.
  - Test descriptions and assertions that check for the project name must be updated.

## 3. Non-Functional Requirements
- **Directory Structure:** The root directory name `/home/adam/repos/simpl2` MUST NOT be changed.
- **Consistency:** The renaming must be consistent across all file types (Python, Markdown, JSON, etc.).
- **Stability:** The renaming must not break existing functionality, particularly regarding configuration loading or external connections.

## 4. In Scope
- `main.py` (CLI description)
- `src/ui.py` (Gradio Blocks title)
- `README.md` (if exists) and other documentation in `conductor/`
- Test files in `tests/`
- Code comments and docstrings across `src/`

## 5. Out of Scope
- Renaming the root project folder.
- Renaming external repositories or dependencies.
