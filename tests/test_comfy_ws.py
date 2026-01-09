import pytest
import json
from comfy_client import ComfyClient
from unittest.mock import patch, Mock, AsyncMock

@pytest.mark.asyncio
async def test_listen_for_images_success():
    client = ComfyClient("http://localhost:8188")
    client.client_id = "conductor_client" # Need to ensure this attribute exists or is set
    prompt_id = "test-prompt-id"
    
    # Mock WebSocket connection and messages
    mock_ws = AsyncMock()
    mock_ws.__aenter__.return_value = mock_ws
    
    messages = [
        json.dumps({"type": "status", "data": {"status": {}}}),
        json.dumps({
            "type": "progress", 
            "data": {"prompt_id": prompt_id, "value": 1, "max": 10}
        }),
        json.dumps({
            "type": "executed", 
            "data": {
                "prompt_id": prompt_id, 
                "output": {
                    "images": [{"filename": "test_image.png", "subfolder": "", "type": "output"}]
                }
            }
        })
    ]
    
    mock_ws.recv.side_effect = messages
    
    # Mock image download
    image_bytes = b"fake_image_data"
    with patch("websockets.connect", return_value=mock_ws) as mock_connect:
        with patch("requests.get") as mock_get:
            mock_get.return_value.content = image_bytes
            
            events = []
            async for event in client.listen_for_images(prompt_id):
                events.append(event)
            
            # Check assertions
            assert len(events) == 2
            
            # Progress event
            assert events[0]["type"] == "progress"
            assert events[0]["value"] == 1
            assert events[0]["max"] == 10
            
            # Image event
            assert events[1]["type"] == "image"
            assert events[1]["data"] == image_bytes
            
            # Verify WS connection URL
            mock_connect.assert_called_once_with("ws://localhost:8188/ws?clientId=conductor_client")
            
            # Verify image download URL
            mock_get.assert_called_once_with(
                "http://localhost:8188/view", 
                params={"filename": "test_image.png", "subfolder": "", "type": "output"}
            )
