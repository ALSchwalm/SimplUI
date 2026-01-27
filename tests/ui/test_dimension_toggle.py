import pytest
from playwright.sync_api import Page, expect

def test_dimension_defaults(page: Page):
    """
    Verifies default view mode based on initial values.
    """
    page.get_by_text("Advanced Controls").click()
    
    # Node 1 (1024x1024) should default to Simplified -> Button: "Show Exact Dimensions"
    # Node 2 (1000x1000) should default to Exact -> Button: "Show Aspect Ratio"
    
    expect(page.get_by_role("button", name="Show Exact Dimensions")).to_have_count(1)
    expect(page.get_by_role("button", name="Show Aspect Ratio")).to_have_count(1)

def test_dimension_toggle_snap(page: Page):
    """
    Verifies toggling from Exact to Simplified snaps values.
    """
    page.get_by_text("Advanced Controls").click()
    
    # Find the "Show Aspect Ratio" button (Node 2)
    toggle = page.get_by_role("button", name="Show Aspect Ratio")
    toggle.click()
    
    # Wait for update
    page.wait_for_timeout(500)
    
    # Now both should be Simplified
    expect(page.get_by_role("button", name="Show Exact Dimensions")).to_have_count(2)
    
    # Verify Node 2 snapped from 1000x1000 to 1024x1024 (1:1 1M)
    store_val = page.evaluate("() => { const el = document.querySelector('#overrides-store'); return JSON.parse(el.innerText); }")
    
    # Node 2
    assert store_val["2.width"] == 1024
    assert store_val["2.height"] == 1024
    assert store_val["2.Dimensions.aspect_ratio"] == "1:1"
    assert store_val["2.Dimensions.pixel_count"] == "1M"
    
    # Verify mode is stored
    assert store_val["2.Dimensions.mode"] == "simplified"
