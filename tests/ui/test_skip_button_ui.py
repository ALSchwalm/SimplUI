import pytest
from playwright.sync_api import Page, expect

def test_skip_button_visibility(page: Page):
    """
    Verifies that the Skip button appears during generation and replaces Generate.
    """
    # 1. Check initial state
    generate_btn = page.get_by_role("button", name="Generate")
    skip_btn = page.get_by_role("button", name="Skip")
    # Stop button might have class 'stop' or text 'Stop'
    stop_btn = page.locator("#stop-btn")
    
    expect(generate_btn).to_be_visible()
    expect(skip_btn).to_be_hidden()
    expect(stop_btn).to_be_hidden()
    
    # 2. Start Generation
    generate_btn.click()
    
    # 3. Verify Generating State
    # Wait for status to change to Initializing or Processing
    expect(page.get_by_text("Initializing")).to_be_visible()
    
    expect(generate_btn).to_be_hidden()
    expect(skip_btn).to_be_visible()
    expect(stop_btn).to_be_visible()
    
    # 4. Wait for completion (default batch 2)
    # Status: Generation complete
    expect(page.get_by_text("Generation complete", exact=False)).to_be_visible(timeout=30000)
    
    # 5. Verify End State
    expect(generate_btn).to_be_visible()
    expect(skip_btn).to_be_hidden()
    expect(stop_btn).to_be_hidden()

def test_skip_button_stop_behavior(page: Page):
    """
    Verifies that stopping hides the Skip button.
    """
    generate_btn = page.get_by_role("button", name="Generate")
    skip_btn = page.get_by_role("button", name="Skip")
    stop_btn = page.locator("#stop-btn")
    
    # Start
    generate_btn.click()
    expect(skip_btn).to_be_visible()
    
    # Stop
    stop_btn.click()
    
    # Verify Stopped State
    expect(page.get_by_text("Interrupted")).to_be_visible()
    expect(generate_btn).to_be_visible()
    expect(skip_btn).to_be_hidden()
    expect(stop_btn).to_be_hidden()
