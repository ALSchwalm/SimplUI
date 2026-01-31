import pytest
from unittest.mock import Mock, patch, mock_open
from ui import handle_generation
from config_manager import ConfigManager
import io
from PIL import Image


@pytest.mark.asyncio
async def test_handle_generation_flicker_repro():
    config = Mock(spec=ConfigManager)
    config.workflows = [{"name": "Workflow 1", "path": "wf1.json"}]

    client = Mock()
    client.inject_prompt = Mock(return_value=True)

    # Simulate a sequence of events: Progress -> Preview -> Progress -> Preview
    async def mock_generate(workflow):
        # 1. Start
        yield {"type": "progress", "value": 1, "max": 10}

        # 2. Preview 1
        # Create a real small image for preview
        img = Image.new("RGB", (10, 10), color="red")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        yield {"type": "preview", "data": img_byte_arr.getvalue()}

        # 3. Progress Update (This currently clears the preview!)
        yield {"type": "progress", "value": 2, "max": 10}

        # 4. Preview 2
        img2 = Image.new("RGB", (10, 10), color="blue")
        img_byte_arr2 = io.BytesIO()
        img2.save(img_byte_arr2, format="PNG")
        yield {"type": "preview", "data": img_byte_arr2.getvalue()}

        # 5. Final Image
        yield {"type": "image", "data": img_byte_arr2.getvalue()}

    client.generate_image = Mock(return_value=mock_generate({}))

    with patch("builtins.open", mock_open(read_data="{}")):
        with patch("json.load", return_value={"mock": "workflow"}):
            updates = []
            async for update in handle_generation("Workflow 1", "Prompt", config, client):
                updates.append(update)

            # Analyze updates
            # Update 0: Progress 1. Expected: [] images, None preview
            assert updates[0][0] == []
            assert updates[0][1] is None

            # Update 1: Preview 1. Expected: [] images, [Preview1]
            assert updates[1][0] == []
            assert updates[1][1] is not None

            # Update 2: Progress 2.
            # Preview should persist
            assert updates[2][1] is not None, "Preview image disappeared during progress update!"
