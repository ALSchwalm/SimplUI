import pytest
from playwright.sync_api import Page, expect
import time


def test_history_integration(page: Page):
    """
    Verifies that the History gallery accumulates final images across multiple runs.
    """
    # 1. Open Advanced Controls and go to History tab
    page.get_by_text("Advanced Controls").click()
    history_tab = page.get_by_role("tab", name="History")
    history_tab.click()

    # 2. Verify History is initially empty
    history_gallery = page.locator("#history-gallery")
    expect(history_gallery.locator("img")).to_have_count(0)

    # 3. Generate first batch (Batch Count = 2)
    # Go back to Node Controls to see Generate button?
    # Actually Generate button is visible regardless of tab.
    generate_btn = page.get_by_role("button", name="Generate")
    generate_btn.click()

    # Wait for completion of Batch 2/2
    expect(
        page.get_by_text("Generation complete", exact=False).filter(has_text="Batch 2/2")
    ).to_be_visible(timeout=30000)

    # 4. Verify History has 2 images
    expect(history_gallery.locator("img")).to_have_count(2)

    # 5. Generate second batch (Batch Count = 2)
    generate_btn.click()

    # Wait for completion of Batch 2/2
    expect(
        page.get_by_text("Generation complete", exact=False).filter(has_text="Batch 2/2")
    ).to_be_visible(timeout=30000)

    # 6. Verify History now has 4 images
    expect(history_gallery.locator("img")).to_have_count(4)

    # 7. Verify no previews in history (by proxy - mock yields 1 preview per batch item)
    # If previews were added, we would have 8 images.
    # Since we have 4, we know previews were likely excluded.
