# Specification: CLI Argument Integration

## Overview
Currently, the application configuration (ComfyUI address, etc.) is managed primarily through `config.json`. This track adds command-line arguments to `main.py` using `argparse` to allow users to specify connectivity and listening parameters dynamically. Arguments provided via the CLI will take precedence over those in `config.json`.

## Functional Requirements
- **CLI Parsing:** Use the standard `argparse` library to handle command-line inputs.
- **Dynamic Configuration:**
  - `--comfy-addr`: Specify the ComfyUI server address (e.g., `127.0.0.1:8188`).
  - `--listen-addr`: Specify the local host and port for the Simpl2 UI to listen on (e.g., `0.0.0.0:7860`).
  - `--config`: Specify a custom path to the `config.json` file.
- **Precedence Logic:**
  1. Use value from CLI argument if provided.
  2. Fall back to `config.json` if CLI argument is missing.
  3. Fall back to internal defaults if neither is present.
- **Address Parsing:** The application must correctly split the combined address:port strings into separate host and port components where required by the underlying server (Gradio `launch`).

## Non-Functional Requirements
- **Robustness:** Gracefully handle malformed address strings or missing config files.
- **User Experience:** Provide helpful `--help` output describing the new flags.

## Acceptance Criteria
- [ ] Running `python main.py --help` displays the new arguments.
- [ ] Providing `--comfy-addr` successfully overrides the URL used to connect to ComfyUI.
- [ ] Providing `--listen-addr` successfully changes the host/port the Gradio app binds to.
- [ ] Providing `--config` loads configuration from the specified path.
- [ ] Existing `config.json` functionality remains intact when no CLI arguments are used.

## Out of Scope
- Environment variable support (to be handled in a separate track if needed).
- Validation of the ComfyUI server's availability during argument parsing (handled at runtime).
