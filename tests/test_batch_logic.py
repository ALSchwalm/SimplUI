import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# We expect this to be refactored out
from ui import process_generation

@pytest.mark.asyncio
async def test_batch_generation_calls():
    # Setup
    config = MagicMock()
    config.workflows = [{"name": "test", "path": "test.json"}]
    config.sliders = {}
    
    comfy_client = MagicMock()
    comfy_client.interrupt = MagicMock()
    comfy_client.clear_queue = MagicMock()
    
    # Mock generate_image to yield valid updates
    async def mock_gen(workflow):
        yield {"type": "progress", "value": 1, "max": 1}
        yield {"type": "image", "data": b"fake"}
        
    comfy_client.generate_image = MagicMock(side_effect=mock_gen)
    comfy_client.get_object_info.return_value = {}
    
    overrides = {"1.seed": "100"}
    object_info = {
        "KSampler": {
            "input": {
                "required": {
                    "seed": ["INT", {"default": 0}]
                }
            }
        }
    }
    
    workflow_data = {
        "1": {
            "inputs": {"seed": 0}, 
            "class_type": "KSampler", 
            "_meta": {"title": "KSampler"}
        }
    }

    # Mock open/json
    with patch("builtins.open", new_callable=MagicMock) as mock_file_open:
        mock_f = MagicMock()
        mock_f.__enter__.return_value = mock_f
        mock_file_open.return_value = mock_f
        
        with patch("json.load", return_value=workflow_data):
             # Act
             updates = []
             async for update in process_generation("test", "", overrides, 2, config, comfy_client, object_info):
                 updates.append(update)
            
             # Assert
             assert comfy_client.generate_image.call_count == 2
             
             # Verify seeds were different
             args1 = comfy_client.generate_image.call_args_list[0][0][0]
             args2 = comfy_client.generate_image.call_args_list[1][0][0]
             
             seed1 = args1["1"]["inputs"]["seed"]
             seed2 = args2["1"]["inputs"]["seed"]
             
             assert seed1 != seed2
