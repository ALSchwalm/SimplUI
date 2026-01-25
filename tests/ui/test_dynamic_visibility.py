import pytest
from playwright.sync_api import Page, expect

def test_dynamic_seed_visibility(page: Page):
    """
    Verifies that the seed input visibility toggles with the Randomize checkbox.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()
    
    # 2. Check Initial State (Mock workflow seed=5 -> Randomize=False)
    seed_input = page.get_by_label("seed").first
    randomize = page.get_by_label("Randomize")
    
    expect(seed_input).to_be_visible()
    expect(randomize).not_to_be_checked()
    
    # 3. Check Randomize -> Input Hidden
    randomize.check()
    expect(seed_input).to_be_hidden()
    
    # 4. Uncheck Randomize -> Input Visible
    randomize.uncheck()
    expect(seed_input).to_be_visible()
