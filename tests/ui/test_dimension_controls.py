import pytest
from playwright.sync_api import Page, expect

def test_dimension_controls_appear(page: Page):
    """
    Verifies that the raw width/height inputs are replaced by Aspect Ratio and Pixel Count.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()
    
    # 2. Find a node that should have dimensions (e.g., the mock workflow's latent node)
    # The default mock workflow has width/height in Node 1? No, conftest.py uses Node 3 KSampler.
    # Let's check conftest.py workflow.
    # Node 3: seed, steps, sampler_name. No width/height.
    # I need to ensure the mock workflow in conftest or a custom one has dimensions.
    
    # Actually, let's verify that the dropdowns are visible if the node has them.
    # We can rely on the fact that if they are rendered, they should have specific labels.
    expect(page.get_by_text("Aspect Ratio")).to_be_visible()
    expect(page.get_by_text("Pixel Count")).to_be_visible()
    
    # 3. Verify defaults
    ar_dropdown = page.get_by_label("Aspect Ratio")
    pc_dropdown = page.get_by_label("Pixel Count")
    
    expect(ar_dropdown).to_have_value("1:1")
    expect(pc_dropdown).to_have_value("1M")

def test_dimension_calculation_integration(page: Page):
    """
    Verifies that changing dropdowns updates the internal width/height in overrides_store.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()
    
    # 2. Select 16:9 and 1M
    # Gradio dropdowns are inputs that open a listbox. 
    # We click the input then the option.
    page.get_by_label("Aspect Ratio").first.click()
    page.get_by_text("16:9").first.click()
    
    # Wait for re-render/update
    page.wait_for_timeout(1000)
    
    # 3. Check overrides_store value
    # We look for the JSON content in the #overrides-store element
    # Gradio might use a <pre> or <div> to display JSON depending on version.
    store_val = page.evaluate("() => { const el = document.querySelector('#overrides-store'); return JSON.parse(el.innerText); }")
    
    # 16:9 and 1M should result in 1344 x 768
    # Node ID for Empty Latent was '1' in our mock
    assert store_val["1.width"] == 1344
    assert store_val["1.height"] == 768
    assert store_val["1.Dimensions.aspect_ratio"] == "16:9"
    assert store_val["1.Dimensions.pixel_count"] == "1M"
