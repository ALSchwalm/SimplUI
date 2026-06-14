import os
import re


def test_lightbox_html_structure():
    html_path = "static/index.html"
    assert os.path.exists(html_path), "index.html must exist"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "lightbox" in content, "Lightbox element must exist in index.html"
    assert "lightbox-close" in content, "Lightbox close button must exist in index.html"
    assert "lightbox-image" in content, "Lightbox image element must exist in index.html"


def test_lightbox_css_styles():
    css_path = "static/styles.css"
    assert os.path.exists(css_path), "styles.css must exist"

    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for .lightbox-overlay styling properties
    assert (
        re.search(r"\.lightbox-overlay\s*\{", content) is not None
    ), ".lightbox-overlay styling block must exist"
    assert (
        "rgba(0, 0, 0, 0.85)" in content
    ), "Lightbox overlay must have rgba(0, 0, 0, 0.85) background color"
    assert "blur(8px)" in content, "Lightbox overlay must use blur(8px) filter"
