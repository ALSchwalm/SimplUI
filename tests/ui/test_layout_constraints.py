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

    # We wrapped the app in a Column with ID app_container

    container = page.locator("#app_container")

    

    # Check computed style

    max_width = container.evaluate("el => window.getComputedStyle(el).maxWidth")

    

    # This should FAIL initially if not implemented, or PASS if implemented correctly

    assert max_width == "1280px"


