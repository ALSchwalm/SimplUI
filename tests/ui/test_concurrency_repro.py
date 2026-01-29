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

    # Wait for dynamic controls to render
    page.wait_for_selector("text=KSampler", timeout=10000)

    # 2. Locate dynamic controls
    # 'steps' input in KSampler node
    steps_input = page.get_by_role("spinbutton", name="number input for steps")

    # Verify interaction works without generation
    initial_value = steps_input.input_value()
    steps_input.fill("42")
    steps_input.press("Enter")
    page.wait_for_timeout(500)
    set_value = steps_input.input_value()
    assert set_value == "42", f"Input should change when NOT generating. Got {set_value}"

    # 3. Start a generation
    generate_btn = page.get_by_role("button", name="Generate")
    generate_btn.click()

    # Wait for generation to start and a preview to potentially arrive
    page.wait_for_timeout(1000)

    # 4. Interact while generating

    # Interaction A: Change Input
    steps_input.fill("50")
    steps_input.press("Enter")

    # Wait for JS and potential re-renders
    page.wait_for_timeout(500)

    # Get the value we set it to
    set_value = steps_input.input_value()
    assert set_value == "50", f"Input value should have changed from 42 to 50"

    # Wait for a potential preview update (which might trigger the reversion)
    # The mock yields every 1s
    page.wait_for_timeout(3000)

    # Check if value persisted
    current_value = steps_input.input_value()
    assert current_value == "50", f"Input value reverted! Expected 50, got {current_value}"

    # Interaction B: Toggle Dimensions
    # 'Show Exact Dimensions' toggle
    exact_dims_btn = page.get_by_role("button", name="Show Exact Dimensions").first
    exact_dims_btn.click()

    # Wait and check if Width is visible
    # Using get_by_label as found in previous logs
    width_input = page.get_by_label("Width").first
    expect(width_input).to_be_visible()

    # Check if value persisted (A) again
    assert steps_input.input_value() == "50", "Steps value reverted after dimension toggle!"

    # 5. Ensure no error toasts are visible
    error_toast = page.locator(".toast-error")
    expect(error_toast).to_be_hidden()

    # Stop generation if still running, otherwise ignore
    stop_btn = page.get_by_role("button", name="Stop")
    if stop_btn.is_visible():
        stop_btn.click()
