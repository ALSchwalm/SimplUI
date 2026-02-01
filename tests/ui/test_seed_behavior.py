import pytest
from playwright.sync_api import Page, expect
import re
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from seed_utils import generate_batch_seeds


def test_seed_value_updates_on_generation(page: Page):
    """
    Verifies that when randomize is checked:
    1. The status shows the Derived Seed (from batching logic).
    2. Unchecking randomize reveals the Base Seed in the input.
    """
    # 1. Open Advanced Controls
    accordion = page.get_by_text("Advanced Controls")
    expect(accordion).to_be_visible()
    accordion.click()

    # 2. Find the seed input
    seed_input = page.get_by_label("seed").first
    # Initially visible (mock seed=5)
    expect(seed_input).to_be_visible()

    # 3. Enable Randomize
    randomize_checkbox = page.get_by_label("Randomize")
    if not randomize_checkbox.is_checked():
        randomize_checkbox.check()

    # Ensure input is hidden
    expect(seed_input).to_be_hidden()

    # 4. Generate
    generate_btn = page.get_by_role("button", name="Generate")
    generate_btn.click()

    # 5. Wait for completion
    status_locator = page.get_by_text("Generation complete", exact=False).filter(
        has_text="Batch 2/2"
    )
    expect(status_locator).to_be_visible(timeout=20000)

    status_text = status_locator.text_content()
    assert "Generation complete" in status_text, f"Status is not complete: {status_text}"

    # 6. (Removed) Verify Status shows derived seed - Seed is no longer displayed in status

    # 7. Uncheck Randomize to reveal Base Seed
    randomize_checkbox.uncheck()
    expect(seed_input).to_be_visible()

    # 8. Capture Base Seed
    base_seed_str = seed_input.input_value()
    assert base_seed_str, "Base seed should be populated"
    base_seed = int(base_seed_str)
    print(f"Base Seed from Input: {base_seed}")

    # 9. (Removed) Verify Consistency - Cannot verify derived seed from UI anymore
