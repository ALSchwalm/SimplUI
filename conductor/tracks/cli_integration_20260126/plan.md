# Implementation Plan: CLI Argument Integration

## Phase 1: Research & Setup [checkpoint: cc46544]
- [x] Task: Analyze `main.py` and `src/config_manager.py` to understand how configuration is currently loaded and passed to `create_ui` and `ComfyClient`. 4992938
- [x] Task: Create a reproduction/verification script `tests/test_cli_args.py` that mocks `sys.argv` and verifies configuration precedence. 1cece9b
- [x] Task: Conductor - User Manual Verification 'Phase 1: Research & Setup' (Protocol in workflow.md)

## Phase 2: Implementation [checkpoint: f8da307]
- [x] Task: Implement `argparse` logic in `main.py` to handle `--comfy-addr`, `--listen-addr`, and `--config`. 129b87a
- [x] Task: Update the configuration loading sequence in `main.py` to implement the required precedence (CLI > Config > Defaults). 129b87a
- [x] Task: Implement address parsing logic to split `host:port` strings for both ComfyUI and the local listener. 129b87a
- [x] Task: Refactor `main.py` to pass the resolved host and port to the `demo.launch()` call. 129b87a
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation' (Protocol in workflow.md)

## Phase 3: Verification & Cleanup
- [x] Task: Run `pytest tests/test_cli_args.py` to ensure all precedence and parsing logic works as expected. 129b87a
- [x] Task: Run the full suite of UI and integration tests to ensure no regressions in server startup. 129b87a
- [x] Task: Format the code using `black .` to ensure compliance with project style guides. 129b87a
- [~] Task: Conductor - User Manual Verification 'Phase 3: Verification & Cleanup' (Protocol in workflow.md)
