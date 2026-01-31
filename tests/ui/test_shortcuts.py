import pytest
from playwright.sync_api import Page, expect


def test_ctrl_enter_shortcut(page: Page):
    """
    Verifies that Ctrl+Enter in the prompt box triggers generation and stop.
    """
    prompt_box = page.get_by_label("Prompt")
    generate_btn = page.get_by_role("button", name="Generate")
    stop_btn = page.locator("#stop-btn")

    # 1. Focus Prompt and Press Ctrl+Enter
    prompt_box.click()
    prompt_box.fill("Test Shortcut")

    # DEBUG: Print structure of prompt box
    # print(page.locator("#prompt-box").inner_html())

    # Press Ctrl+Enter
    prompt_box.press("Control+Enter")

    # 2. Verify Generation Starts
    # Generate button should hide, Stop button should appear
    expect(generate_btn).to_be_hidden()
    expect(stop_btn).to_be_visible()

    # Status should indicate processing
    expect(page.get_by_text("Initializing")).to_be_visible()

    # 3. Press Ctrl+Enter Again to Stop
    # Ensure prompt is still focused (it might lose focus if UI updates, but let's re-focus or assume user keeps focus)
    # The user might need to click back if focus was lost, but usually it stays or user is typing.
    # Let's force focus just in case to test the shortcut specifically.
    prompt_box.click()
    prompt_box.press("Control+Enter")

    # 4. Verify Stopped State
    # Stop button should hide, Generate button should appear
    expect(stop_btn).to_be_hidden()
    expect(generate_btn).to_be_visible()
    expect(page.get_by_text("Interrupted")).to_be_visible()


def test_cmd_enter_shortcut_mac(page: Page):
    """
    Verifies that Meta+Enter (Cmd+Enter) works.
    Playwright 'Meta' maps to Command on Mac and Windows key on others.
    """
    prompt_box = page.get_by_label("Prompt")
    generate_btn = page.get_by_role("button", name="Generate")

    prompt_box.click()
    prompt_box.press("Meta+Enter")

    expect(generate_btn).to_be_hidden()
    expect(page.get_by_text("Initializing")).to_be_visible()
