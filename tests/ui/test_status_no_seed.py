import pytest
from playwright.sync_api import Page, expect


def test_status_does_not_contain_seed(page: Page):
    """
    Verifies that the status text does NOT contain the word 'Seed' during or after generation.
    """
    # 1. Trigger a generation
    page.get_by_label("Prompt").fill("Test prompt for status check")
    page.get_by_role("button", name="Generate").click()

    # 2. Wait for completion
    # We wait for the "Generation complete" message
    status_locator = page.get_by_text("Generation complete", exact=False)
    expect(status_locator).to_be_visible(timeout=20000)

    # 3. Get the status text
    status_text = status_locator.text_content()

    # 4. Assert that "Seed" is NOT in the status text
    # Note: Currently this IS expected to be there, so this test should FAIL in the Red phase.
    assert "Seed" not in status_text, f"Status text contained 'Seed': {status_text}"
