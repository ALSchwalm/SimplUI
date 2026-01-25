import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

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

    with patch("builtins.open", new_callable=MagicMock) as mock_file_open:
        mock_f = MagicMock()
        mock_f.__enter__.return_value = mock_f
        mock_file_open.return_value = mock_f
        
        with patch("json.load", return_value=workflow_data):
            with patch("ui.Image.open") as mock_img_open:
                 mock_img_open.return_value = "ImageObject"
                 
                 updates = []
                 async for update in process_generation("test", "", overrides, 2, config, comfy_client, object_info):
                     updates.append(update)
                
                 assert comfy_client.generate_image.call_count == 2
                 
                 args1 = comfy_client.generate_image.call_args_list[0][0][0]
                 args2 = comfy_client.generate_image.call_args_list[1][0][0]
                 
                 seed1 = args1["1"]["inputs"]["seed"]
                 seed2 = args2["1"]["inputs"]["seed"]
                 
                 assert seed1 != seed2

@pytest.mark.asyncio
async def test_batch_aggregation_with_previews():
    config = MagicMock()
    config.workflows = [{"name": "test", "path": "test.json"}]
    config.sliders = {}
    
    comfy_client = MagicMock()
    comfy_client.interrupt = MagicMock()
    comfy_client.clear_queue = MagicMock()
    
    async def mock_gen(workflow):
        # Yield preview
        yield {"type": "preview", "data": b"prev"}
        # Yield final
        yield {"type": "image", "data": b"final"}
        
    comfy_client.generate_image = MagicMock(side_effect=mock_gen)
    comfy_client.get_object_info.return_value = {}
    
    workflow_data = {"1": {"inputs": {}, "class_type": "Node"}}
    
    with patch("builtins.open", new_callable=MagicMock) as mock_file_open:
        mock_f = MagicMock()
        mock_f.__enter__.return_value = mock_f
        mock_file_open.return_value = mock_f
        
        with patch("json.load", return_value=workflow_data):
            with patch("ui.Image.open") as mock_img_open:
                # Mock Image objects with names for easy identification
                def side_effect(io_bytes):
                    if io_bytes.getvalue() == b"prev":
                        return "Preview"
                    if io_bytes.getvalue() == b"final":
                        return "Final"
                    return "Unknown"
                mock_img_open.side_effect = side_effect
                
                updates = []
                async for update in process_generation("test", "", {}, 2, config, comfy_client, {}):
                    # update is (images, status, ...)
                    updates.append(update[0])
                
                # Verify aggregation sequence
                # Iter 1:
                # 1. Init: None
                # 2. Randomize: None
                # 3. [Preview]
                # 4. [Final] (Preview replaced by Final)
                # Iter 2:
                # 5. [Final, Preview]
                # 6. [Final, Final]
                
                # Filter out None updates
                image_updates = [u for u in updates if u is not None]
                
                # Note: process_generation yields status updates too (Init, Randomize) which yield None images
                
                assert ["Preview"] in image_updates
                assert ["Final"] in image_updates
                assert ["Final", "Preview"] in image_updates
                assert ["Final", "Final"] in image_updates