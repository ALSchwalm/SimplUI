import pytest
from playwright.sync_api import Page, expect

def test_batch_generation_gallery(page: Page):
    """
    Verifies that setting Batch Count > 1 produces multiple images in the gallery.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()
    
    # 2. Set Batch Count to 2 (Default is 2)
    # We verify it's 2 just to be sure
    # Using a loose selector to find the number input
    # page.get_by_label("Batch Count") matches both slider and number input.
    # We can just check that one of them has value 2.
    
    # 3. Generate
    page.get_by_role("button", name="Generate").click()
    
    # 4. Wait for completion (Batch 2/2)
    expect(page.get_by_text("Generation complete", exact=False).filter(has_text="Batch 2/2")).to_be_visible(timeout=30000)
    
    # 5. Verify Gallery has 2 images
    gallery = page.locator("#gallery")
    
    # Gradio Gallery renders images as <img ...>
    # We expect 2 images.
    expect(gallery.locator("img")).to_have_count(2)
