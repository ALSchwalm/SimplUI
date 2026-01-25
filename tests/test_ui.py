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
                
                # Now updates contain lists of images
                assert len(updates) == 3
                # First update: progress, empty images?
                assert updates[0][0] == []
                assert updates[0][1] == "Progress: 5/10"
                
                # Second update: preview
                assert updates[1][0] == ["mock_preview_image"]
                assert updates[1][1] == "Progress: 5/10"
                
                # Third update: final image
                assert updates[2][0] == ["mock_pil_image"]
                assert updates[2][1] == "Generation complete"
                
                # Note: test_handle_generation_success tests handle_generation directly,
                # which still returns 2 values.
                # The on_generate wrapper returns 3. 
                # This test is still valid for handle_generation.
                
                client.inject_prompt.assert_called_once_with({"mock": "workflow"}, "User Prompt")
                client.generate_image.assert_called_once_with({"mock": "workflow"})

@pytest.mark.asyncio
async def test_handle_generation_multiple_images():
    config = Mock(spec=ConfigManager)
    config.workflows = [{"name": "Workflow 1", "path": "wf1.json"}]
    client = Mock()
    client.inject_prompt = Mock(return_value=True)
    
    async def mock_generate(workflow):
        yield {"type": "progress", "value": 5, "max": 10}
        yield {"type": "image", "data": b"img1"}
        yield {"type": "image", "data": b"img2"}
    
    client.generate_image = Mock(return_value=mock_generate({}))
    
    # Mock open and json.load
    with patch("builtins.open", mock_open(read_data='{"mock": "workflow"}')):
        with patch("json.load", return_value={"mock": "workflow"}):
            with patch("ui.Image.open", side_effect=["pil_img1", "pil_img2"]):
                updates = []
                async for update in handle_generation("Workflow 1", "User Prompt", config, client):
                    updates.append(update)
                
                # We expect updates to contain growing list of images
                # Update 1: Progress -> No images yet? Or None?
                # Update 2: Image 1 -> [img1]
                # Update 3: Image 2 -> [img1, img2]
                
                assert len(updates) == 3
                
                # Check status
                assert updates[0][1] == "Progress: 5/10"
                assert updates[0][0] is None or updates[0][0] == []
                
                # Check first image yield
                images_1 = updates[1][0]
                assert isinstance(images_1, list)
                assert len(images_1) == 1
                assert images_1[0] == "pil_img1"
                
                # Check second image yield
                images_2 = updates[2][0]
                assert isinstance(images_2, list)
                assert len(images_2) == 2
                assert images_2[0] == "pil_img1"
                assert images_2[1] == "pil_img2"

def test_ui_components():
    config = Mock(spec=ConfigManager)
    config.workflows = [
        {"name": "Workflow 1", "path": "path1"},
        {"name": "Workflow 2", "path": "path2"}
    ]
    
    # We need to mock open since gr.render might trigger a read if we were running a server,
    # but in dry run it shouldn't. However, let's be safe.
    demo = create_ui(config, Mock())
    assert isinstance(demo, gr.Blocks)
    config_json = demo.get_config_file()
    assert "Workflow 1" in str(config_json)
    
    # Generate button and Prompt textarea are static again
    assert "Generate" in str(config_json)
    assert "Prompt" in str(config_json)
    assert "Advanced Controls" in str(config_json)

def test_apply_random_seeds():
    from ui import apply_random_seeds
    
    overrides = {
        "1.steps": 30,
        "1.seed": 123,
        "1.seed.randomize": True,
        "2.noise_seed": 456,
        "2.noise_seed.randomize": False
    }
    
    updated = apply_random_seeds(overrides)
    
    # 1.seed should be changed (randomized)
    assert updated["1.seed"] != 123
    assert isinstance(updated["1.seed"], str)
    
    # 2.noise_seed should NOT be changed
    assert updated["2.noise_seed"] == 456
    
    # Other values should persist
    assert updated["1.steps"] == 30

def test_extract_workflow_inputs_randomize_default():
    from ui import extract_workflow_inputs
    workflow = {
        "1": {
            "_meta": {"title": "KSampler"},
            "inputs": {"seed": 0},
            "class_type": "KSampler"
        }
    }
    extracted = extract_workflow_inputs(workflow)
    # 0 -> randomize=True
    assert extracted[0]["inputs"][0]["randomize"] is True
    
    workflow_nonzero = {
        "1": {
            "_meta": {"title": "KSampler"},
            "inputs": {"seed": 123},
            "class_type": "KSampler"
        }
    }
    extracted_nz = extract_workflow_inputs(workflow_nonzero)
    # 123 -> randomize=False
    assert extracted_nz[0]["inputs"][0]["randomize"] is False
