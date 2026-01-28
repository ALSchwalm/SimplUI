# Implementation Plan - Project Renaming (Simpl2 -> SimplUI)

This plan outlines the steps to comprehensively rename the project from "Simpl2" to "SimplUI" across the codebase, UI, and documentation.

## Phase 1: Preparation and Search
- [x] Task: Create comprehensive list of "Simpl2" occurrences
    - [ ] Run `grep -r "Simpl2" .` and `grep -r "simpl2" .` to identify all targets.
    - [ ] Create a target list file to track replacement progress.

## Phase 2: Codebase Updates
- [x] Task: Rename Python Code References
    - [ ] Update `main.py` (CLI description, argument parsing help text).
    - [ ] Update `src/ui.py` (Gradio Blocks title, window title).
    - [ ] Update `config.json` or config loading logic if it defaults to "simpl2" paths/names.
    - [ ] Update `src/config_manager.py` if applicable.
    - [ ] Scan and update other files in `src/` for variable names or comments.

## Phase 3: Test Suite Updates
- [x] Task: Update Test Files
    - [ ] Update `tests/test_ui.py` (check for updated titles/labels).
    - [ ] Update `tests/test_cli_args.py` (if exists, check for CLI help text).
    - [ ] Update any other tests that assert specific strings related to the project name.
    - [ ] Run tests to ensure no regressions.

## Phase 4: Documentation Updates
- [x] Task: Update Project Documentation
    - [ ] Update `README.md` (if it exists).
    - [ ] Update `conductor/product.md` and `conductor/product-guidelines.md` to reflect the new name.
    - [ ] Update `pyproject.toml` (if name metadata exists there).
    - [ ] Update `conductor/tracks/` files if necessary (historical tracks might be left as is, but current context should change).

## Phase 5: Verification
- [x] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
