import pytest
from playwright.sync_api import Page, expect


def test_gallery_responsive_columns(page: Page):
    """
    Verifies that the gallery adjusts its columns based on viewport width.
    """
    # Reveal advanced controls
    page.get_by_label("Advanced Controls").check()

    # Set Batch Count to 2
    page.get_by_label("number input for Batch Count").fill("2")

    page.get_by_label("Prompt").fill("Test prompt for responsive columns")
    page.get_by_role("button", name="Generate").click()

    # Wait for completion
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=15000)

    # Locate the gallery
    gallery = page.locator("#gallery")
    expect(gallery).to_be_visible()

    # Wait for images to be present
    expect(gallery.locator("img")).to_have_count(2, timeout=5000)

    # The grid container is usually a div inside the gallery with class 'grid-container' or similar,
    # or just a div with display: grid.
    # In recent Gradio versions, it might be the .grid-wrap or similar.
    # We will search for an element with display: grid inside #gallery.

    # Let's inspect the gallery structure.
    # Typically: #gallery -> .prose -> ... -> .grid-container

    # We can try to find the element that has 'display: grid'
    grid = gallery.locator("div").filter(has_text="").evaluate_all("""
        elements => elements.find(el => window.getComputedStyle(el).display === 'grid')
        """)

    # If we can't find it easily via evaluate_all (which returns handle), we can use a more robust locator strategy.
    # But first, let's try to set the viewport and check if we can see the change.

    # CASE 1: Wide Viewport (Desktop) -> Should be 2 columns
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.wait_for_timeout(500)  # Give UI a moment to react

    # We check the grid-template-columns property.
    # It should reflect 2 columns. e.g., "1fr 1fr" or "repeat(2, minmax(0, 1fr))" or simply computed pixel values.
    # If it's 2 columns, it will have 2 entries.

    # We need to find the grid element again because references might change if React re-renders,
    # although usually it's stable.

    # This JS snippet finds all gallery items and their positions
    get_item_positions = """
        () => {
            const gallery = document.querySelector('#gallery');
            if (!gallery) return [];
            
            const items = gallery.querySelectorAll('button.gallery-item');
            // If button.gallery-item doesn't exist, try just buttons inside the grid
            const grid = [...gallery.querySelectorAll('*')].find(el => window.getComputedStyle(el).display === 'grid');
            const children = grid ? [...grid.children] : [];
            
            return children.map(el => {
                const rect = el.getBoundingClientRect();
                return {
                    tagName: el.tagName,
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                };
            });
        }
    """

    items_wide = page.evaluate(get_item_positions)

    # If they are in 2 columns, at least two items should have the same Y but different X
    xs = set([round(i["x"]) for i in items_wide])

    # In 2 columns, we expect 2 distinct X positions
    assert len(xs) >= 2, f"Expected at least 2 columns (distinct X positions), got {len(xs)}."

    # CASE 2: Narrow Viewport (Mobile) -> Should be 1 column
    page.set_viewport_size({"width": 400, "height": 800})
    page.wait_for_timeout(500)

    items_narrow = page.evaluate(get_item_positions)

    xs_narrow = set([round(i["x"]) for i in items_narrow])
    assert len(xs_narrow) == 1, f"Expected 1 column (1 distinct X position), got {len(xs_narrow)}."


def test_history_gallery_responsive_columns(page: Page):
    """
    Verifies that the history gallery adjusts its columns based on viewport width.
    """
    # Trigger a generation to ensure the history is populated
    page.get_by_label("Prompt").fill("Test history responsive")
    page.get_by_role("button", name="Generate").click()
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=15000)

    # Open Advanced Controls and switch to History tab
    page.get_by_label("Advanced Controls").check()
    page.get_by_role("tab", name="History").click()

    gallery = page.locator("#history-gallery")
    expect(gallery).to_be_visible()
    expect(gallery.locator("img")).to_have_count(1, timeout=5000)

    # Generate another one to have 2 images
    page.get_by_role("button", name="Generate").click()
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=15000)
    expect(gallery.locator("img")).to_have_count(2, timeout=5000)

    # JS Helper
    get_item_positions = """
        () => {
            const gallery = document.querySelector('#history-gallery');
            if (!gallery) return [];

            const items = gallery.querySelectorAll('button.gallery-item');
            const grid = [...gallery.querySelectorAll('*')].find(el => window.getComputedStyle(el).display === 'grid');
            const children = grid ? [...grid.children] : [];

            return children.map(el => {
                const rect = el.getBoundingClientRect();
                return { x: rect.x, y: rect.y };
            });
        }
    """

    # CASE 1: Wide Viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.wait_for_timeout(500)

    items_wide = page.evaluate(get_item_positions)
    xs = set([round(i["x"]) for i in items_wide])
    assert len(xs) >= 2, f"History: Expected at least 2 columns, got {len(xs)}."

    # CASE 2: Narrow Viewport
    page.set_viewport_size({"width": 400, "height": 800})
    page.wait_for_timeout(500)

    items_narrow = page.evaluate(get_item_positions)
    xs_narrow = set([round(i["x"]) for i in items_narrow])
    assert len(xs_narrow) == 1, f"History: Expected 1 column, got {len(xs_narrow)}."
