import pytest
from playwright.sync_api import Page, expect
import time

def test_interaction_during_generation(page: Page):
    """
    Reproduction test: Verify that interacting with controls during generation
    does not cause state reversion or errors.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()

    # 2. Locate controls
    # Use 'Batch Count' as a stable slider to test
    slider_label = page.get_by_text("Batch Count")
    slider_input = page.locator("input[type='range']").first
    # Use 'Show Exact Dimensions' as a toggle to test visibility changes
    exact_dims_checkbox = page.get_by_label("Show Exact Dimensions")
    
    # 3. Start a generation (Mock backend should be slow enough)
    # The 'Generate' button might change to 'Skip', so we find by role
    generate_btn = page.get_by_role("button", name="Generate")
    generate_btn.click()

    # Wait for generation to start (button becomes 'Skip' or loader appears)
    # Using a simple timeout for now, or check for 'Skip' if implemented
    page.wait_for_timeout(1000) 

    # 4. Interact while generating
    
    # Interaction A: Change Slider
    # Get initial value
    initial_value = slider_input.input_value()
    # Move slider
    box = slider_input.bounding_box()
    page.mouse.move(box["x"] + 10, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.up()
    
    # Wait for a potential preview update (which might trigger the reversion)
    page.wait_for_timeout(2000)
    
    # Check if value persisted
    current_value = slider_input.input_value()
    assert current_value != initial_value, "Slider value should have changed"
    
    # Interaction B: Toggle Visibility
    # Toggle 'Show Exact Dimensions'
    # Check initial state
    width_input = page.get_by_label("Width")
    expect(width_input).to_be_hidden()
    
    exact_dims_checkbox.check()
    
    # Wait for potential update
    page.wait_for_timeout(1000)
    
    # Expect Width input to be visible
    expect(width_input).to_be_visible()
    
    # 5. Ensure no error toasts are visible
    # Gradio error toasts usually have class 'toast-error' or similar
    error_toast = page.locator(".toast-error")
    expect(error_toast).to_be_hidden()

    # Wait for generation to likely finish or just stop
    page.get_by_role("button", name="Skip").click()
