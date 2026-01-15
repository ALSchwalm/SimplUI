import pytest
from playwright.sync_api import Page, expect

def test_seed_value_updates_on_generation(page: Page):
    """
    Verifies that when Randomize is checked, the seed input updates to the generated value.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()
    
    # 2. Find the seed input and randomize checkbox
    # Assuming 'seed' is the label for the number input
    seed_input = page.get_by_label("seed", exact=True)
    # The checkbox is likely labeled "Randomize" and is near the seed input.
    # In my implementation: random_box = gr.Checkbox(label="Randomize", ...)
    # But there might be multiple "Randomize" boxes if multiple seeds.
    # We'll use the first one for now or scope it.
    random_box = page.get_by_label("Randomize").first
    
    expect(seed_input).to_be_visible()
    
    # Get initial value
    initial_value = seed_input.input_value()
    
    # 3. Check Randomize
    # Note: Logic says if seed is 0, it defaults to True. Test workflow has seed=5, so defaults to False.
    if not random_box.is_checked():
        random_box.check()
        
    # 4. Click Generate
    page.get_by_role("button", name="Generate").click()
    
    # 5. Wait for generation to start/finish
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=10000)
    
    # 6. Check if seed input value changed
    final_value = seed_input.input_value()
    
    # Assert it changed (it's extremely unlikely random int matches 5)
    assert final_value != initial_value, f"Seed value did not update! Initial: {initial_value}, Final: {final_value}"
    
    # 7. Uncheck Randomize
    random_box.uncheck()
    
    # 8. Check value again - it should STILL be the random value
    value_after_uncheck = seed_input.input_value()
    assert value_after_uncheck == final_value, f"Seed reverted after unchecking! Got {value_after_uncheck}, expected {final_value}"
    
    # 9. Click Generate again
    page.get_by_role("button", name="Generate").click()
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=10000)
    
    # 10. Check value again - should not change
    final_value_2 = seed_input.input_value()
    assert final_value_2 == final_value, "Seed changed despite Randomize being unchecked!"
