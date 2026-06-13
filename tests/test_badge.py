import os
import re


def test_preview_badge_removal_in_js():
    # Verify that app.js contains logic to remove the preview-badge when prompt execution completes.
    app_js_path = "static/app.js"
    assert os.path.exists(app_js_path), "static/app.js should exist"

    with open(app_js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # We expect code to find the preview-badge element and remove it
    # E.g., slot.querySelector('.preview-badge').remove() or badge.remove()
    assert "preview-badge" in content, "preview-badge should be referenced in app.js"

    # The following assertion should fail in the Red Phase as the removal logic does not yet exist.
    assert (
        re.search(r"badge\s*\.remove\(\)", content) is not None
    ), "app.js should call badge.remove() to clear the generating badge"
