import pytest
from unittest.mock import Mock, patch, mock_open
from ui import create_ui, extract_workflow_inputs
from config_manager import ConfigManager
import gradio as gr


def test_ui_resilience_missing_file():
    config = Mock(spec=ConfigManager)
    config.workflows = [{"name": "Workflow 1", "path": "missing.json"}]

    # We need to access the render function. This is hard without running the app.
    # Instead, let's verify extract_workflow_inputs raises/handles errors gracefully
    # or that the render function catches it.

    # In src/ui.py, render_advanced_params catches Exception and prints Markdown.
    # We can't easily unit test the inner render function of a gr.Blocks app without inspecting the Blocks object deeply.

    # However, we can verifying that create_ui doesn't crash on init with invalid config
    demo = create_ui(config, Mock())
    assert isinstance(demo, gr.Blocks)


def test_extract_workflow_inputs_malformed():

    # Malformed workflow (missing _meta, missing inputs)
    workflow = {"1": {}}

    extracted = extract_workflow_inputs(workflow)
    assert len(extracted) == 0
