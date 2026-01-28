import pytest
from playwright.sync_api import Page, expect


def test_history_tab_exists(page: Page):
    """
    Verifies that the History tab exists in the Advanced Sidebar.
    """
    # 1. Open Advanced Controls
    page.get_by_text("Advanced Controls").click()

    # 2. Verify Node Controls tab is visible
    expect(page.get_by_role("tab", name="Node Controls")).to_be_visible()

    # 3. Verify History tab is visible
    history_tab = page.get_by_role("tab", name="History")
    expect(history_tab).to_be_visible()

    # 4. Click History tab
    history_tab.click()

    # 5. Verify History Gallery is visible
    expect(page.locator("#history-gallery")).to_be_visible()
