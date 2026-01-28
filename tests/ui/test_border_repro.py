import pytest
from playwright.sync_api import Page, expect


def test_no_row_wrapper_for_advanced_controls(page: Page):
    """
    Verifies that the Advanced Controls checkbox is NOT wrapped in an unnecessary Row.
    The presence of this Row causes an unwanted border.
    """
    # page fixture already navigates to the app

    # Wait for the checkbox to appear
    checkbox_label = page.get_by_text("Advanced Controls")
    expect(checkbox_label).to_be_visible()

    # In the current (buggy) implementation, the checkbox is inside a gr.Row().
    # Gradio renders gr.Row() as a div with class 'row'.
    # We want to ensure that there is NO '.row' element that contains this checkbox label
    # as its direct or near-direct child.

    # We check for a .row that contains the label.
    # Note: If the entire page is a row, this might be tricky.
    # But looking at src/ui.py, this element is in a Column, which is likely in a Row, etc.
    # However, the SPECIFIC gr.Row() we want to remove is the immediate parent.

    # Let's count how many '.row' elements contain this text.
    # If the bug is present, we expect to see the specific wrapping row.
    # If fixed, that specific wrapping row is gone.

    # To be precise: The Checkbox component itself might have classes.
    # But the wrapper `with gr.Row():` adds a distinct div.

    # Let's try to verify if the direct parent (or close ancestor) is a row.
    # This locator finds a .row that contains the text "Advanced Controls".
    # In the buggy version, this should definitely find the wrapper row.
    rows_with_checkbox = page.locator(".row", has=page.get_by_text("Advanced Controls"))

    # We expect this count to be 0 for the "clean" layout (or at least fewer than before).
    # But wait, if there are outer rows, this might still return something.
    # Let's debug by printing the count or just asserting.

    # Better approach:
    # The 'buggy' row is a sibling of the 'Prompt' row.
    # It wraps ONLY the checkbox.
    # So if we find a .row that contains "Advanced Controls" AND nothing else (like "Prompt"),
    # that's likely the culprit.

    # "Prompt" is in the previous row.

    culprit_row = page.locator(".row", has=page.get_by_text("Advanced Controls")).filter(
        has_not=page.get_by_label("Prompt")
    )

    # We expect this row NOT to exist.
    expect(culprit_row).to_have_count(0)
