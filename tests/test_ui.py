import pytest
import gradio as gr
from ui import create_ui, handle_generation
from config_manager import ConfigManager
from unittest.mock import Mock, AsyncMock, patch, mock_open
import json

@pytest.mark.asyncio
async def test_handle_generation_success():
    config = Mock(spec=ConfigManager)
    config.workflows = [{"name": "Workflow 1", "path": "wf1.json"}]
    
    client = Mock()
    client.inject_prompt = Mock(return_value=True)
    
    async def mock_generate(workflow):
        yield {"type": "progress", "value": 5, "max": 10}
        yield {"type": "preview", "data": b"fake-preview-data"}
        yield {"type": "image", "data": b"fake-data"}
    
    client.generate_image = Mock(return_value=mock_generate({}))
    
    # Mock open and json.load
    with patch("builtins.open", mock_open(read_data='{"mock": "workflow"}')):
        with patch("json.load", return_value={"mock": "workflow"}):
            with patch("ui.Image.open", side_effect=["mock_preview_image", "mock_pil_image"]):
                updates = []
                async for update in handle_generation("Workflow 1", "User Prompt", config, client):
                    updates.append(update)
                
                assert len(updates) == 3
                assert updates[0] == (None, "Progress: 5/10")
                assert updates[1] == ("mock_preview_image", "Progress: 5/10")
                assert updates[2] == ("mock_pil_image", "Generation complete")
                
                client.inject_prompt.assert_called_once_with({"mock": "workflow"}, "User Prompt")
                client.generate_image.assert_called_once_with({"mock": "workflow"})

def test_ui_components():
    config = Mock(spec=ConfigManager)
    config.workflows = [
        {"name": "Workflow 1", "path": "path1"},
        {"name": "Workflow 2", "path": "path2"}
    ]
    
    demo = create_ui(config, Mock())
    assert isinstance(demo, gr.Blocks)
    config_json = demo.get_config_file()
    assert "Workflow 1" in str(config_json)
    # Check for Generate button
    assert "Generate" in str(config_json)
    # Check for Prompt textarea
    assert "Prompt" in str(config_json)
    # Check for Advanced Controls
    assert "Advanced Controls" in str(config_json)