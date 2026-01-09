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
    client.submit_workflow = Mock(return_value="prompt-123")
    
    async def mock_listen(prompt_id):
        yield {"type": "progress", "value": 5, "max": 10}
        yield {"type": "image", "data": b"fake-data"}
    
    client.listen_for_images = Mock(return_value=mock_listen("prompt-123"))
    
    # Mock open and json.load
    with patch("builtins.open", mock_open(read_data='{"mock": "workflow"}')):
        with patch("json.load", return_value={"mock": "workflow"}):
            updates = []
            async for update in handle_generation("Workflow 1", config, client):
                updates.append(update)
            
            assert len(updates) == 2
            assert updates[0] == (None, "Progress: 5/10")
            assert updates[1] == (b"fake-data", "Generation complete")
            
            client.submit_workflow.assert_called_once_with({"mock": "workflow"})
            client.listen_for_images.assert_called_once_with("prompt-123")

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
    assert "Generate" in str(config_json)
