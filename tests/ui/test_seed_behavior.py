import pytest
from playwright.sync_api import Page, expect
import re
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from seed_utils import generate_batch_seeds

def test_seed_value_updates_on_generation(page: Page):
    """
    Verifies that when randomize is checked:
    1. The UI input updates to the new random Base Seed.
    2. The status shows the Derived Seed (from batching logic).
    """
    # 1. Open Advanced Controls
    accordion = page.get_by_text("Advanced Controls")
    expect(accordion).to_be_visible()
    accordion.click()
    
    # 2. Find the seed input
    seed_input = page.get_by_label("seed").first
    expect(seed_input).to_be_visible()
    
    # 3. Enable Randomize
    randomize_checkbox = page.get_by_label("Randomize")
    if not randomize_checkbox.is_checked():
        randomize_checkbox.check()
    
    # 4. Generate
    generate_btn = page.get_by_role("button", name="Generate")
    generate_btn.click()
    
    # 5. Wait for completion
    # Default batch count is 2. We need to wait for the SECOND batch to finish.
    # The status will show "Generation complete (Batch 2/2 ...)"
    # We use a locator that requires both strings to be present
    status_locator = page.get_by_text("Generation complete", exact=False).filter(has_text="Batch 2/2")
    expect(status_locator).to_be_visible(timeout=20000)
    
    status_text = status_locator.text_content()
    # Ensure it's the final complete state
    assert "Generation complete" in status_text, f"Status is not complete: {status_text}"

    # 6. Capture Base Seed from Input
    # The UI updates the input with the randomized base seed
    base_seed_str = seed_input.input_value()
    assert base_seed_str, "Base seed should be populated"
    base_seed = int(base_seed_str)
    print(f"Base Seed from Input: {base_seed}")
    
    # 7. Verify Status shows derived seed
    # Default batch count is 2. Status shows Batch 2/2 at the end.
    # So it shows the 2nd derived seed.
    status_text = status_locator.text_content()
    match = re.search(r"[Ss]eed:\s*(\d+)", status_text)
    assert match, f"Could not find seed in status: {status_text}"
    status_seed = int(match.group(1))
    print(f"Status Seed: {status_seed}")
    
    expected_seeds = generate_batch_seeds(base_seed, 2)
    # The status shows the seed of the last batch iteration (Batch 2)
    assert status_seed == expected_seeds[1], f"Status seed {status_seed} does not match expected derived seed {expected_seeds[1]} from base {base_seed}"