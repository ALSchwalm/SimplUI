import pytest
import gradio as gr
from ui import create_ui
from config_manager import ConfigManager
from unittest.mock import Mock

def test_layout_structure():
    config = Mock(spec=ConfigManager)
    config.workflows = [{"name": "Workflow 1", "path": "path1"}]
    config.sliders = {}
    client = Mock()
    client.get_object_info.return_value = {}

    demo = create_ui(config, client)
    conf = demo.get_config_file()
    components = conf["components"]
    
    # Root containers are usually rows/columns
    # We expect a top-level row containing main_col and sidebar_col
    
    # Let's find the first row and check its children
    rows = [c for c in components if c["type"] == "row"]
    assert len(rows) >= 1, "Should have at least one row"
    
    # In the new layout, the first row should contain two columns
    # We can check parent-child relationships in dependencies or by inspecting layout
    # Actually, Gradio config 'components' is a flat list, but 'layout' or children can be inferred.
    # In 4.x/5.x, it's often better to look at how components are nested.
    
    # A better way might be to look for the sidebar column and check its visibility
    columns = [c for c in components if c["type"] == "column"]
    assert len(columns) >= 2, "Should have at least two columns (main and sidebar)"
    
    # The sidebar should be invisible by default
    # We'll label it or find it by its content later, but for now just check count
    
    # Check for Advanced Controls checkbox
    checkboxes = [c for c in components if c["type"] == "checkbox" and c["props"].get("label") == "Advanced Controls"]
    assert len(checkboxes) == 1, "Should have an 'Advanced Controls' checkbox"

    # Check for vertical buttons column
    btn_cols = [c for c in components if c["type"] == "column" and "vertical-buttons" in c["props"].get("elem_classes", [])]
    assert len(btn_cols) == 1, "Should have a column with 'vertical-buttons' class"
    
    # Check for equal_height Row
    prompt_rows = [c for c in components if c["type"] == "row" and c["props"].get("equal_height") is True]
    assert len(prompt_rows) >= 1, "Prompt row should have equal_height=True"
    
    # Check for sidebar column and its visibility
    # The sidebar is the one containing the render block or the markdown "Advanced Controls"
    sidebar = next(c for c in components if c["type"] == "column" and c["props"].get("visible") is False)
    assert sidebar is not None, "Sidebar column should be invisible by default"

def test_vertical_stack():
    config = Mock(spec=ConfigManager)
    config.workflows = [{"name": "Workflow 1", "path": "path1"}]
    config.sliders = {}
    client = Mock()
    client.get_object_info.return_value = {}

    demo = create_ui(config, client)
    conf = demo.get_config_file()
    components = conf["components"]
    
    gallery = next(c for c in components if c["type"] == "gallery")
    prompt = next(c for c in components if c["type"] == "textbox" and c["props"].get("label") == "Prompt")
    
    # In a vertical stack, Gallery ID should likely be less than Prompt ID if they are in the same column
    # or we can check their relative positions if we had more layout info.
    # For now, let's just ensure they both exist.
    assert gallery is not None
    assert prompt is not None
