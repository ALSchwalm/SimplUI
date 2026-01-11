import pytest
from playwright.sync_api import Page, expect

def test_sampler_name_is_dropdown(page: Page):
    """
    Verifies that sampler_name is rendered as a dropdown when metadata is available.
    """
    # 1. Open Advanced Controls
    accordion = page.get_by_text("Advanced Controls")
    expect(accordion).to_be_visible()
    accordion.click()
    
    # 2. Verify KSampler section
    expect(page.get_by_text("KSampler")).to_be_visible()
    
    # 3. Verify sampler_name is a dropdown (role combobox in many UI frameworks, 
    # but Gradio uses specific structure. We can check if it has 'choices' or just use get_by_label)
    sampler_dropdown = page.get_by_label("sampler_name")
    expect(sampler_dropdown).to_be_visible()
    
    # Verify it has dropdown-like behavior or specific class if needed.
    # In Gradio, a dropdown might be a div with role=combobox or a select.
    # We can check for the existence of options by clicking it.
    sampler_dropdown.click()
    
    # Check for options from mock (euler, ddim, heun)
    expect(page.get_by_text("ddim")).to_be_visible()
    expect(page.get_by_text("heun")).to_be_visible()
