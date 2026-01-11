import pytest
from playwright.sync_api import Page, expect

def test_basic_layout_and_generation(page: Page):
    """
    Verifies that the main UI components are visible and interaction triggers generation.
    """
    # 1. Verify Page Title/Header
    expect(page.get_by_text("Simpl2 ComfyUI Wrapper", exact=False).first).to_be_visible()
    
    # 2. Verify Workflow Dropdown
    expect(page.get_by_label("Select Workflow")).to_be_visible()
    
    # 3. Verify Prompt Textarea
    expect(page.get_by_label("Prompt")).to_be_visible()
    
    # 4. Verify Generate and Stop Buttons
    generate_btn = page.get_by_role("button", name="Generate")
    expect(generate_btn).to_be_visible()
    
    # Stop button should be hidden initially
    # Use CSS selector to be precise
    stop_btn = page.locator("button.stop")
    expect(stop_btn).to_be_hidden()
    
    # 5. Interaction: Click Generate
    page.get_by_label("Prompt").fill("Test prompt for automation")
    generate_btn.click()
    
    # 6. Verify Status Updates
    # We wait for either Initializing or Processing
    expect(page.get_by_text("Initializing").first).to_be_visible()
    
    # Stop button should become visible during generation
    expect(stop_btn).to_be_visible()
    
    # Wait for completion
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=10000)
    
    # Wait for completion
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=10000)
    
    # Stop button should hide again
    expect(stop_btn).not_to_be_visible()

def test_advanced_controls_toggle(page: Page):
    """
    Verifies that the Advanced Controls accordion can be opened.
    """
    accordion = page.get_by_text("Advanced Controls")
    expect(accordion).to_be_visible()
    
    # Click to open
    accordion.click()
    
    # Verify that a node parameter appears (e.g. "steps")
    # Using a slightly looser search since it's dynamic
    expect(page.get_by_text("KSampler")).to_be_visible()
    expect(page.get_by_label("steps")).to_be_visible()
