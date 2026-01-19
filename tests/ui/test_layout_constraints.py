import pytest
from playwright.sync_api import Page, expect

def test_header_removal(page: Page):
    """
    Verifies that the main header text is NOT present in the page body.
    """
    # We want to ensure the header text is not visible in the body.
    # Note: page.title() (browser tab) should still contain it, but we check the body.
    
    # We look for the text in a heading or markdown-like element.
    # Gradio Markdown usually renders as <h1> or similar.
    header = page.get_by_role("heading", name="Simpl2 ComfyUI Wrapper")
    
    # This should FAIL initially as the header currently exists.
    expect(header).not_to_be_visible()

def test_max_width_constraint(page: Page):
    """
    Verifies that the main container has a max-width constraint of 1280px.
    """
    # Dump classes for debugging
    divs = page.locator("div").all()
    print("\nAvailable div classes:")
    for d in divs[:20]:
        cls = d.get_attribute("class")
        if cls:
            print(f" - {cls}")
            
    # Try multiple common Gradio container classes
    for selector in [".gradio-container", ".container", "div[class*='container']", "body > div"]:
        container = page.locator(selector).first
        if container.count() > 0:
            max_width = container.evaluate("el => window.getComputedStyle(el).maxWidth")
            print(f"Selector '{selector}' computed maxWidth: {max_width}")
            if max_width == "1280px":
                return # SUCCESS
    
    # Final check
    container = page.locator(".gradio-container")
    max_width = container.evaluate("el => window.getComputedStyle(el).maxWidth")
    assert max_width == "1280px"
