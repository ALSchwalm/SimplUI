import pytest
from playwright.sync_api import Page, expect
import re

def test_seed_value_updates_on_generation(page: Page):
    """
    Verifies that when randomize is checked and generation runs,
    unchecking randomize preserves the *generated* seed, not the old one.
    """
    # 1. Open Advanced Controls
    accordion = page.get_by_text("Advanced Controls")
    expect(accordion).to_be_visible()
    accordion.click()
    
    # 2. Find the seed input
    # Assuming the workflow has a 'seed' input. The default mock workflow has 'seed' in KSampler.
    seed_input = page.get_by_label("seed").first
    expect(seed_input).to_be_visible()
    
    # Debug initial value
    initial_val = seed_input.input_value()
    print(f"Initial Seed: {initial_val}")
    
    # 3. Enable Randomize
    randomize_checkbox = page.get_by_label("Randomize")
    expect(randomize_checkbox).to_be_visible()
    
    # Ensure it's checked (it might be false by default if value != 0)
    if not randomize_checkbox.is_checked():
        randomize_checkbox.check()
    
    # 4. Generate
    generate_btn = page.get_by_role("button", name="Generate")
    generate_btn.click()
    
    # 5. Wait for completion and capture seed
    status = page.get_by_text("Generation complete", exact=False).first
    expect(status).to_be_visible(timeout=10000)
    
    status_text = status.text_content()
    # Extract seed from "Generation complete (Seed: 12345)"
    # Note: Logic in ui.py adds seed to status
    match = re.search(r"Seed:\s*(\d+)", status_text)
    assert match, f"Could not find seed in status: {status_text}"
    generated_seed = match.group(1)
    print(f"Generated Seed: {generated_seed}")
    
    # 6. Uncheck Randomize
    randomize_checkbox.uncheck()
    
    # 7. Assert Seed Input Value
    # It should match generated_seed. If the bug exists, it will likely be the old value.
    current_value = seed_input.input_value()
    
    assert current_value == generated_seed, f"Expected seed {generated_seed}, but got {current_value}"