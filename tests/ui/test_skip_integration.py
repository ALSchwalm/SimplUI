import pytest
from playwright.sync_api import Page, expect


def test_skip_generation_integration(page: Page):
    """
    Verifies that clicking Skip drops the current image and moves to next.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()

    # 2. Set Batch Count to 2 (Default is 2)

    # 3. Generate
    page.get_by_role("button", name="Generate").click()

    # 4. Wait for Skip button (Batch 1 started)
    skip_btn = page.get_by_role("button", name="Skip")
    expect(skip_btn).to_be_visible()

    # 5. Click Skip immediately
    skip_btn.click()

    # 6. Wait for completion
    expect(page.get_by_text("Generation complete", exact=False)).to_be_visible(timeout=30000)

    # 7. Verify Gallery
    # Should have 1 image (Batch 1 skipped, Batch 2 completed)
    gallery = page.locator("#gallery")
    expect(gallery.locator("img")).to_have_count(1)
