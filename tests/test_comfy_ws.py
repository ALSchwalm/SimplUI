import pytest
import json
from comfy_client import ComfyClient
from unittest.mock import patch, Mock, AsyncMock


@pytest.mark.asyncio
async def test_generate_image_success():

    client = ComfyClient("http://localhost:8188")

    # client.client_id is gone

    prompt_id = "test-prompt-id"

    workflow = {"test": "workflow"}

    # Mock WebSocket connection and messages

    mock_ws = AsyncMock()

    mock_ws.__aenter__.return_value = mock_ws

    messages = [
        json.dumps({"type": "status", "data": {"status": {}}}),
        json.dumps(
            {
                "type": "progress",
                "data": {"prompt_id": prompt_id, "value": 1, "max": 10},
            }
        ),
        json.dumps(
            {
                "type": "executed",
                "data": {
                    "prompt_id": prompt_id,
                    "output": {
                        "images": [
                            {
                                "filename": "test_image.png",
                                "subfolder": "",
                                "type": "output",
                            }
                        ]
                    },
                },
            }
        ),
    ]

    mock_ws.recv.side_effect = messages

    # Mock image download and submit_workflow

    image_bytes = b"fake_image_data"

    with patch("uuid.uuid4", return_value="dynamic-client-id"):

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

                    # Verify WS connection URL with dynamic ID

                    mock_connect.assert_called_once_with(
                        "ws://localhost:8188/ws?clientId=dynamic-client-id",
                        max_size=10485760,
                    )

                    # Verify workflow submission uses dynamic ID

                    # We can check call args

                    call_args = mock_post.call_args

                    assert call_args[1]["json"]["client_id"] == "dynamic-client-id"


@pytest.mark.asyncio
async def test_generate_image_with_previews():

    client = ComfyClient("http://localhost:8188")

    # client.client_id is gone

    prompt_id = "test-prompt-id"

    workflow = {"test": "workflow"}

    # Mock WebSocket connection and messages

    mock_ws = AsyncMock()

    mock_ws.__aenter__.return_value = mock_ws

    preview_bytes = b"\x00\x00\x00\x01\x00\x00\x00\x02fake_preview_data"

    messages = [
        json.dumps({"type": "status", "data": {"status": {}}}),
        preview_bytes,  # Binary message
        json.dumps(
            {
                "type": "executed",
                "data": {"prompt_id": prompt_id, "output": {"images": []}},
            }
        ),
    ]

    mock_ws.recv.side_effect = messages

    with patch("uuid.uuid4", return_value="dynamic-client-id"):

        with patch("websockets.connect", return_value=mock_ws):

            with patch("requests.post") as mock_post:

                mock_post.return_value.status_code = 200

                mock_post.return_value.json.return_value = {"prompt_id": prompt_id}

                events = []

                async for event in client.generate_image(workflow):

                    events.append(event)

                # Check for preview event

                assert any(e["type"] == "preview" for e in events)

                preview_event = next(e for e in events if e["type"] == "preview")

                # We strip the 8-byte header in implementation

                assert preview_event["data"] == preview_bytes[8:]
