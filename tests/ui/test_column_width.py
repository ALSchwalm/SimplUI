import pytest
from playwright.sync_api import Page, expect

def test_main_column_width(page: Page):
    """
    Verifies that the main column expands to fill the available width (up to max-width).
    """
    # Set viewport to something wide to trigger max-width logic
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    # Wait for load
    expect(page.locator(".gradio-container")).to_be_visible()
    
    # Get container width
    container_width = page.locator(".gradio-container").evaluate("el => el.getBoundingClientRect().width")
    print(f"Container width: {container_width}")
    
    # Get gallery width (inside main col) - #gallery is a good proxy for main column width
    # Note: #gallery has CSS height: 50vh, but width should be auto/100%
    gallery_width = page.locator("#gallery").evaluate("el => el.getBoundingClientRect().width")
    print(f"Gallery width: {gallery_width}")
    
    # With sidebar hidden (default), gallery should take up most of the 1280px width.
    # If it's ~380px, this assertion will fail.
    assert gallery_width > 1000, f"Gallery is too narrow: {gallery_width}px (Container: {container_width}px)"
