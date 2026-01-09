import pytest
import gradio as gr
from ui import create_ui
from config_manager import ConfigManager
from unittest.mock import Mock

def test_ui_components():
    config = Mock(spec=ConfigManager)
    config.workflows = [
        {"name": "Workflow 1", "path": "path1"},
        {"name": "Workflow 2", "path": "path2"}
    ]
    
    demo = create_ui(config, Mock())
    
    # Check if it's a Blocks instance
    assert isinstance(demo, gr.Blocks)
    
    # Gradio doesn't provide a very easy way to inspect children without private APIs,
    # but we can check if certain strings are in the configuration
    config_json = demo.get_config_file()
    
    # Check for workflow names in dropdown choices
    assert "Workflow 1" in str(config_json)
    assert "Workflow 2" in str(config_json)
    
    # Check for Generate button
    assert "Generate" in str(config_json)
