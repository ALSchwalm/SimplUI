import pytest
from playwright.sync_api import Page, expect
from unittest.mock import MagicMock
import asyncio

def test_preview_clears_on_stop(page: Page, mock_comfy_client):
    """
    Verifies that the preview image is removed from the gallery when the Stop button is clicked.
    """
    # 1. Setup the mock generator to yield a preview and then hang
    async def mock_generate_preview_and_hang(*args, **kwargs):
        # Yield a preview
        # A simple red 1x1 pixel png
        valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdcD\xfe\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
        
        # Initial status
        yield {"type": "status", "data": {"status": {"exec_info": {"queue_remaining": 1}}}}
        await asyncio.sleep(0.1)

        # Yield preview
        yield {"type": "preview", "data": valid_png}
        
        # Hang to simulate generation in progress
        while True:
            await asyncio.sleep(0.1)

    # Patch the generate_image method on the existing mock client instance
    mock_comfy_client.generate_image = MagicMock(side_effect=mock_generate_preview_and_hang)

    # 2. Start Generation
    page.get_by_label("Prompt").fill("Test preview persistence")
    page.get_by_role("button", name="Generate").click()

    # 3. Wait for Preview to appear
    # The gallery items are usually buttons or imgs. 
    # In Gradio 4/5, gallery items are often within a grid.
    # We can check if an image is present in the gallery.
    # The gallery id is 'gallery'.
    gallery = page.locator("#gallery")
    # Wait for at least one image to be visible
    expect(gallery.locator("img")).to_have_count(1, timeout=5000)

    # 4. Click Stop
    stop_btn = page.locator("#stop-btn")
    expect(stop_btn).to_be_visible()
    stop_btn.click()

    # 5. Assert Preview is Removed
    # After stopping, the gallery should be empty because no image completed.
    expect(gallery.locator("img")).to_have_count(0, timeout=5000)

def test_preview_clears_on_skip(page: Page, mock_comfy_client):
    """
    Verifies that the preview image is removed from the gallery when the Skip button is clicked.
    """
    call_count = 0
    
    async def mock_generate_smart(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdcD\xfe\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
        yield {"type": "status", "data": {"status": {"exec_info": {"queue_remaining": 1}}}}
        await asyncio.sleep(0.1)

        if call_count == 1:
            # First run: Hang with preview
            yield {"type": "preview", "data": valid_png}
            while True:
                await asyncio.sleep(0.1)
        else:
            # Second run: Finish immediately with NO image
            yield {"type": "status", "data": {"status": {"exec_info": {"queue_remaining": 0}}}}

    # Patch the generate_image method
    mock_comfy_client.generate_image = MagicMock(side_effect=mock_generate_smart)

    # 2. Start Generation with Batch Count (Default is 2)
    page.get_by_label("Prompt").fill("Test skip preview persistence")
    page.get_by_role("button", name="Generate").click()

    # 3. Wait for Preview to appear (First run)
    gallery = page.locator("#gallery")
    expect(gallery.locator("img")).to_have_count(1, timeout=5000)

    # 4. Click Skip
    skip_btn = page.locator("#skip-btn")
    expect(skip_btn).to_be_visible()
    skip_btn.click()

    # 5. Assert Preview is Removed
    # After skipping, we move to 2nd run which yields nothing.
    # So gallery should be empty.
    expect(gallery.locator("img")).to_have_count(0, timeout=5000)


