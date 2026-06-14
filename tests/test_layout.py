import os
import re


def test_layout_card_order():
    html_path = "static/index.html"
    assert os.path.exists(html_path), "index.html must exist"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the positions of prompt-card and gallery-card in the DOM
    gallery_pos = content.find("gallery-card")
    prompt_pos = content.find("prompt-card")

    assert gallery_pos != -1, "gallery-card must exist in HTML"
    assert prompt_pos != -1, "prompt-card must exist in HTML"

    # We expect gallery-card to be positioned before prompt-card in the DOM structure
    assert (
        gallery_pos < prompt_pos
    ), "gallery-card should be defined before prompt-card in index.html"


def test_gallery_css_sizing():
    css_path = "static/styles.css"
    assert os.path.exists(css_path), "styles.css must exist"

    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    # We expect .gallery-card to have a height of 70vh and max-height of 70vh
    assert (
        re.search(r"\.gallery-card\s*\{[^}]*height:\s*70vh", content) is not None
    ), "gallery-card height should be 70vh"
    assert (
        re.search(r"\.gallery-card\s*\{[^}]*max-height:\s*70vh", content) is not None
    ), "gallery-card max-height should be 70vh"

    # We expect .gallery-item to not force a square aspect ratio (aspect-ratio: 1 / 1)
    # E.g., we look for aspect-ratio: 1 / 1 inside .gallery-item block and assert it's NOT present, or changed.
    gallery_item_match = re.search(r"\.gallery-item\s*\{([^}]*)\}", content)
    assert gallery_item_match is not None, ".gallery-item block must exist in CSS"
    gallery_item_rules = gallery_item_match.group(1)
    assert (
        "aspect-ratio: 1 / 1" not in gallery_item_rules
    ), ".gallery-item should not force aspect-ratio: 1 / 1"


def test_batch_count_relocated():
    html_path = "static/index.html"
    assert os.path.exists(html_path), "index.html must exist"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the positions of workflow-select, batch-count-slider, dynamic-controls-container, and settings-divider
    select_pos = content.find('id="workflow-select"')
    slider_pos = content.find('id="batch-count-slider"')
    dynamic_pos = content.find('id="dynamic-controls-container"')
    divider_pos = content.find('class="settings-divider"')

    assert select_pos != -1, "workflow-select must exist in HTML"
    assert slider_pos != -1, "batch-count-slider must exist in HTML"
    assert dynamic_pos != -1, "dynamic-controls-container must exist in HTML"
    assert divider_pos != -1, "settings-divider must exist in HTML"

    assert select_pos < slider_pos, "batch-count-slider should be positioned after workflow-select"
    assert (
        slider_pos < divider_pos
    ), "settings-divider should be positioned after batch-count-slider"
    assert (
        divider_pos < dynamic_pos
    ), "dynamic-controls-container should be positioned after settings-divider"


def test_divider_css_styling():
    css_path = "static/styles.css"
    assert os.path.exists(css_path), "styles.css must exist"

    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Assert settings-divider class exists and has border styling
    assert (
        re.search(r"\.settings-divider\s*\{[^}]*border-bottom:", content) is not None
    ), "settings-divider should have border-bottom style"
