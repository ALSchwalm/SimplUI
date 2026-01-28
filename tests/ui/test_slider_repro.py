import pytest
from playwright.sync_api import Page, expect
import time

def test_slider_change_triggers_multiple_updates(page: Page):
    """
    Reproduction test: Verify that moving a slider triggers multiple updates.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()
    
    # 2. Find the Batch Count slider
    # Gradio slider has a range input
    slider = page.get_by_label("Batch Count").locator("xpath=..").locator("input[type='range']")
    expect(slider).to_be_visible()
    
    # 3. Monitor network requests
    # We look for POST requests to /run/predict which Gradio uses for component updates
    request_urls = []
    def handle_request(request):
        if request.method == "POST":
            request_urls.append(request.url)
            
    page.on("request", handle_request)
    
    # 4. Move slider
    box = slider.bounding_box()
    start_x = box["x"] + 10
    end_x = box["x"] + box["width"] - 10
    y = box["y"] + box["height"] / 2
    
    page.mouse.move(start_x, y)
    page.mouse.down()
    # Move in steps to trigger multiple 'change' events
    steps = 10
    for i in range(steps + 1):
        page.mouse.move(start_x + (end_x - start_x) * (i / steps), y)
        page.wait_for_timeout(50) # Small delay to allow events to fire
    page.mouse.up()
    
    # Wait a bit for any trailing requests
    page.wait_for_timeout(500)
    
    print(f"DEBUG: Found {len(request_urls)} /run/predict requests")
    
    # Desired behavior: exactly 1 update on release
    assert len(request_urls) == 1, f"Expected exactly 1 update on release, but got {len(request_urls)}"

def test_dynamic_slider_triggers_one_update(page: Page):
    """
    Verify that dynamic sliders also only trigger one update on release.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()
    
    # 2. Find a dynamic slider (e.g. 'steps' which we mock in conftest)
    # The 'KSampler' node has 'steps'
    # Wait for the dynamic content to be rendered
    page.wait_for_selector("text=KSampler", timeout=10000)
    
    # Try to find any slider to see what's available
    sliders = page.locator("input[type='range']").all()
    print(f"DEBUG: Found {len(sliders)} range inputs")
    
    # In our mock, 'steps' is one of the sliders in KSampler
    # Let's find the one that is NOT the batch count slider (which has elem_id="batch-count-slider")
    slider = None
    for s in sliders:
        if s.get_attribute("id") != "batch-count-slider":
            slider = s
            break
            
    assert slider is not None, "Could not find dynamic slider"
    expect(slider).to_be_visible()
    
    # Move it to ensure it's in a known state
    box = slider.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_timeout(500)

    request_urls = []
    def handle_request(request):
        if request.method == "POST":
            print(f"DEBUG DYNAMIC: Request {request.method} {request.url}")
            request_urls.append(request.url)
    page.on("request", handle_request)
    
    # 3. Move slider
    page.mouse.move(box["x"] + 10, box["y"] + box["height"] / 2)
    page.mouse.down()
    for i in range(5):
        page.mouse.move(box["x"] + 10 + (box["width"] - 20) * (i / 5), box["y"] + box["height"] / 2)
        page.wait_for_timeout(100)
    page.mouse.up()
    
    page.wait_for_timeout(1000)
    
    print(f"DEBUG: Found {len(request_urls)} requests for dynamic slider")
    assert len(request_urls) == 1, f"Expected 1 update for dynamic slider, but got {len(request_urls)}"