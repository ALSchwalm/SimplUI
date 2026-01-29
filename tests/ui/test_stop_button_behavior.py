import pytest
from playwright.sync_api import Page, expect


def test_stop_button_hides_after_success(page: Page):
    """
    Verifies that the Stop button hides and Generate button reappears
    after a successful generation.
    """
    generate_btn = page.get_by_role("button", name="Generate")
    stop_btn = page.locator("button.stop")

    # 1. Start Generation
    page.get_by_label("Prompt").fill("Test prompt for success")
    generate_btn.click()

    # 2. Wait for Processing
    expect(page.get_by_text("Initializing").first).to_be_visible()
    expect(stop_btn).to_be_visible()
    expect(generate_btn).to_be_hidden()

    # 3. Wait for Completion
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=10000)

    # 4. Verify Stop Button Hides (This is expected to FAIL currently)
    expect(stop_btn).to_be_hidden()
    expect(generate_btn).to_be_visible()
    expect(generate_btn).to_be_enabled()
