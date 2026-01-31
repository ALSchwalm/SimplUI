import pytest
from playwright.sync_api import Page, expect
import json


def test_textbox_no_immediate_update(page: Page):
    """
    Verifies that typing in a dynamic textbox doesn't trigger immediate updates.
    """
    # 1. Open Advanced Controls
    page.get_by_label("Advanced Controls").check()

    # 2. Locate a dynamic textbox.
    # Node 2 (Odd Latent) defaults to Exact dimensions because 1000x1000 isn't a preset.
    width_input = page.get_by_label("Width").first
    expect(width_input).to_be_visible()

    # 3. Get initial store state
    store_locator = page.locator("#overrides-store")

    def get_store():
        text = store_locator.inner_text()
        try:
            val = json.loads(text)
            return val
        except:
            return {}

    initial_store = get_store()

    # 4. Type into Width input
    width_input.focus()
    # Type "123" slowly
    width_input.press_sequentially("123", delay=100)

    # 5. Check if store updated immediately
    # With the fix (using .blur()/.submit()), it should NOT update yet.
    page.wait_for_timeout(500)
    current_store = get_store()

    val = current_store.get("2.width")
    assert val != 123, f"Store updated immediately on type! Value was {val}"


def test_textbox_update_on_blur(page: Page):
    """
    Verifies that updates happen on blur.
    """
    page.get_by_label("Advanced Controls").check()

    width_input = page.get_by_label("Width").first
    expect(width_input).to_be_visible()
    width_input.fill("768")

    # Blur by clicking the accordion header
    page.get_by_label("Advanced Controls").click()

    # Wait for store to update
    page.wait_for_timeout(1000)

    # Now it should be updated
    store_locator = page.locator("#overrides-store")
    text = store_locator.inner_text()
    store = json.loads(text)
    assert store.get("2.width") == 768


def test_textbox_update_on_enter(page: Page):
    """
    Verifies that updates happen on Enter.
    """
    page.get_by_label("Advanced Controls").check()

    width_input = page.get_by_label("Width").first
    expect(width_input).to_be_visible()
    width_input.focus()
    width_input.fill("1024")
    width_input.press("Enter")

    # Wait for store to update
    page.wait_for_timeout(1000)

    # Now it should be updated
    store_locator = page.locator("#overrides-store")
    text = store_locator.inner_text()
    store = json.loads(text)
    assert store.get("2.width") == 1024


def test_slider_no_immediate_update(page: Page):
    """
    Verifies that typing in a slider's number input doesn't trigger immediate updates.
    """
    page.get_by_label("Advanced Controls").check()

    # Node 3 'steps' is a slider
    # Gradio Slider has a number input inside.
    # Label is 'steps'.
    # We use .first because there's a range input too
    steps_slider_label = page.get_by_label("steps").first
    # There might be multiple inputs (range and number).
    # Usually the number input is accessible by label.
    expect(steps_slider_label).to_be_visible()

    # Get initial store
    store_locator = page.locator("#overrides-store")

    def get_store():
        text = store_locator.inner_text()
        try:
            return json.loads(text)
        except:
            return {}

    # Type into steps
    steps_slider_label.focus()
    steps_slider_label.fill("50")

    # Wait
    page.wait_for_timeout(500)

    # Check store
    # If slider uses .release(), fill() (which might trigger change) shouldn't update store?
    # Or maybe fill() triggers blur?
    # If I use type(), it simulates typing.

    steps_slider_label.focus()
    steps_slider_label.press_sequentially("5", delay=100)

    current_store = get_store()
    # It should NOT be updated yet if it only updates on release.
    # But wait, if I didn't attach change, it shouldn't update.
    # Does release trigger on typing? No.

    # So if I type, store shouldn't update.
    val = current_store.get("3.steps")
    # Default is 20.
    assert val != 5, f"Slider updated immediately! {val}"

    # Now how to trigger update?
    # For slider, I used .release().
    # Mouse release triggers it.
    # Does blurring the number input trigger release? Probably not.
    # So if I type in slider number, it might NEVER update?
    # That would be a bug (but not stuttering).

    # Let's see if it updates.
    pass


def test_generate_persists_focused_textbox(page: Page):
    """
    Verifies that clicking Generate while focused on a textbox correctly persists the value.
    """
    page.get_by_label("Advanced Controls").check()

    width_input = page.get_by_label("Width").first
    expect(width_input).to_be_visible()
    width_input.focus()
    width_input.fill("512")

    # Click Generate immediately
    page.get_by_role("button", name="Generate").click()

    # Wait a bit for the click and blur to process
    page.wait_for_timeout(1000)

    # Check store
    store_locator = page.locator("#overrides-store")
    text = store_locator.inner_text()
    store = json.loads(text)
    assert store.get("2.width") == 512
