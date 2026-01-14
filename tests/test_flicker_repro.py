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
        img = Image.new('RGB', (10, 10), color = 'red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        yield {"type": "preview", "data": img_byte_arr.getvalue()}
        
        # 3. Progress Update (This currently clears the preview!)
        yield {"type": "progress", "value": 2, "max": 10}
        
        # 4. Preview 2
        img2 = Image.new('RGB', (10, 10), color = 'blue')
        img_byte_arr2 = io.BytesIO()
        img2.save(img_byte_arr2, format='PNG')
        yield {"type": "preview", "data": img_byte_arr2.getvalue()}
        
        # 5. Final Image
        yield {"type": "image", "data": img_byte_arr2.getvalue()}
    
    client.generate_image = Mock(return_value=mock_generate({}))
    
    with patch("builtins.open", mock_open(read_data='{}')):
         with patch("json.load", return_value={"mock": "workflow"}):
            updates = []
            async for update in handle_generation("Workflow 1", "Prompt", config, client):
                updates.append(update)
            
            # Analyze updates
            # Update 0: Progress 1. Expected: [] images (or just previous state? but initially empty)
            assert updates[0][0] == []
            
            # Update 1: Preview 1. Expected: [Preview1]
            assert len(updates[1][0]) == 1
            
            # Update 2: Progress 2. 
            # CURRENT BUG: This yields list(completed_images), which is still [].
            # So the preview disappears.
            print(f"Update 2 images: {updates[2][0]}")
            
            # If the bug exists, this assertion will pass (confirming the bad behavior)
            # OR I can write the assertion for the *correct* behavior and watch it fail.
            # TDD says write the test that expects correct behavior and watch it fail.
            
            # Correct behavior: The preview should persist until a new one comes or a final image is added.
            # So Update 2 should still contain the preview image (or at least NOT be empty).
            
            # However, since 'completed_images' only stores FINAL images, logic needs to change.
            # The test expecting correct behavior:
            assert len(updates[2][0]) == 1, "Preview image disappeared during progress update!"
