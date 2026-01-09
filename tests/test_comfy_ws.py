import pytest
import json
from comfy_client import ComfyClient
from unittest.mock import patch, Mock, AsyncMock

@pytest.mark.asyncio
async def test_generate_image_success():
    client = ComfyClient("http://localhost:8188")
    client.client_id = "conductor_client"
    prompt_id = "test-prompt-id"
    workflow = {"test": "workflow"}
    
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
    
    # Mock image download and submit_workflow
    image_bytes = b"fake_image_data"
    with patch("websockets.connect", return_value=mock_ws) as mock_connect:
        with patch("requests.get") as mock_get:
            with patch("requests.post") as mock_post:
                # Mock submit_workflow response
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {"prompt_id": prompt_id}
                
                mock_get.return_value.content = image_bytes
                
                events = []
                async for event in client.generate_image(workflow):
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
                mock_connect.assert_called_once_with("ws://localhost:8188/ws?clientId=conductor_client", max_size=10485760)
                
                # Verify image download URL
                mock_get.assert_called_once_with(
                    "http://localhost:8188/view", 
                    params={"filename": "test_image.png", "subfolder": "", "type": "output"}
                )
                
                # Verify workflow submission
                mock_post.assert_called_once()