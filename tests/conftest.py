import pytest
import threading
import time
import uvicorn
from unittest.mock import MagicMock, patch
from ui import create_ui
from config_manager import ConfigManager
from playwright.sync_api import Page

# Mock Config
@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigManager)
    config.workflows = [
        {"name": "Test Workflow", "path": "workflows/test.json"}
    ]
    # Ensure workflow file exists for reading
    import os
    if not os.path.exists("workflows"):
        os.makedirs("workflows")
    with open("workflows/test.json", "w") as f:
        f.write('{"3": {"inputs": {"seed": 5, "steps": 20, "sampler_name": "euler"}, "class_type": "KSampler", "_meta": {"title": "KSampler"}}}')
    return config

# Mock Comfy Client
@pytest.fixture
def mock_comfy_client():
    client = MagicMock()
    # Mock methods used by UI
    client.check_connection.return_value = True
    client.submit_workflow.return_value = "mock-prompt-id"
    
    # Mock Object Info for Smarter Controls
    client.get_object_info.return_value = {
        "KSampler": {
            "input": {
                "required": {
                    "sampler_name": [["euler", "ddim", "heun"]],
                    "scheduler": [["normal", "karras", "exponential"]],
                    "steps": ["INT", {"default": 20}]
                }
            }
        },
        "CheckpointLoaderSimple": {
            "input": {
                "required": {
                    "ckpt_name": [["v1-5.ckpt", "sdxl.safetensors"]]
                }
            }
        }
    }
    
    # Mock generator
    async def mock_generate(*args, **kwargs):
        print("MOCK: WS Starting...")
        yield {"type": "status", "data": {"status": {"exec_info": {"queue_remaining": 0}}}}
        import asyncio
        await asyncio.sleep(1)
        print("MOCK: WS Yielding progress...")
        yield {"type": "progress", "value": 5, "max": 10}
        await asyncio.sleep(1)
        print("MOCK: WS Yielding final image...")
        valid_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdcD\xfe\xe7\x00\x00\x00\x00IEND\xaeB`\x82'
        yield {"type": "image", "data": valid_png}
        print("MOCK: WS Done.")
    
    client.generate_image = MagicMock(side_effect=mock_generate)
    return client

@pytest.fixture(scope="session")
def app_port():
    return 7861  # Use a different port for testing

@pytest.fixture
def gradio_server(mock_config, mock_comfy_client, app_port):
    """
    Launches the Gradio app in a background thread.
    """
    demo = create_ui(mock_config, mock_comfy_client)
    
    # Launch in a thread
    # prevent_thread_lock=True ensures it doesn't block
    server_thread = threading.Thread(
        target=demo.launch,
        kwargs={
            "server_name": "127.0.0.1", 
            "server_port": app_port, 
            "prevent_thread_lock": True,
            "quiet": True
        }
    )
    server_thread.start()
    
    # Wait for server to start (simple sleep for now, or check connectivity)
    time.sleep(2) 
    
    yield f"http://127.0.0.1:{app_port}"
    
    # Cleanup
    demo.close()
    server_thread.join(timeout=2)

@pytest.fixture
def page(context, gradio_server):
    """
    Overrides the default page fixture to navigate to the gradio app.
    """
    page = context.new_page()
    page.goto(gradio_server)
    return page
