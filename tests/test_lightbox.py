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


def test_lightbox_js_behavior(page):
    # Set up request interception to mock unpkg.com, static assets, and api/config
    def handle_route(route):
        url = route.request.url
        if "unpkg.com/lucide" in url:
            route.fulfill(
                content_type="application/javascript",
                body="window.lucide = { createIcons: () => {} };",
            )
        elif url.endswith("/static/app.js"):
            with open("static/app.js", "r", encoding="utf-8") as f:
                route.fulfill(content_type="application/javascript", body=f.read())
        elif url.endswith("/static/styles.css"):
            with open("static/styles.css", "r", encoding="utf-8") as f:
                route.fulfill(content_type="text/css", body=f.read())
        elif "api/config" in url:
            route.fulfill(
                content_type="application/json",
                body='{"comfy_url": "", "workflows": [], "sliders": {}}',
            )
        else:
            route.continue_()

    page.route("**", handle_route)

    # Load the static index.html file
    abs_path = os.path.abspath("static/index.html")
    page.goto(f"file://{abs_path}")

    # Set up some test images in gallery grid and history grid via page.evaluate
    page.evaluate("""() => {
        // Mock gallery images
        const gallery = document.getElementById('gallery-grid');
        gallery.innerHTML = '';
        gallery.classList.remove('hidden');
        ['img1.jpg', 'img2.jpg', 'img3.jpg'].forEach((src, idx) => {
            const slot = document.createElement('div');
            slot.className = 'gallery-item';
            slot.id = `gallery-slot-${idx}`;
            const img = document.createElement('img');
            img.src = src;
            slot.appendChild(img);
            gallery.appendChild(slot);
        });

        // Mock history state
        state.history = ['hist1.jpg', 'hist2.jpg'];
    }""")

    # Verify lightbox is initially hidden
    lightbox = page.locator("#lightbox")
    assert "hidden" in lightbox.get_attribute("class")

    # Click first image in gallery
    page.locator("#gallery-slot-0 img").click()
    assert "hidden" not in lightbox.get_attribute("class")

    # Verify lightbox image source
    lightbox_image = page.locator("#lightbox-image")
    assert lightbox_image.get_attribute("src").endswith("img1.jpg")

    # Click right zone to navigate to next image
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("img2.jpg")

    # Click right zone again
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("img3.jpg")

    # Loop around to the first image
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("img1.jpg")

    # Click left zone to loop back to the last image
    page.locator("#lightbox-left-zone").click()
    assert lightbox_image.get_attribute("src").endswith("img3.jpg")

    # Press ArrowLeft key to go back
    page.keyboard.press("ArrowLeft")
    assert lightbox_image.get_attribute("src").endswith("img2.jpg")

    # Press ArrowRight key to go forward
    page.keyboard.press("ArrowRight")
    assert lightbox_image.get_attribute("src").endswith("img3.jpg")

    # Click close button and verify lightbox is hidden
    page.locator("#lightbox-close").click()
    assert "hidden" in lightbox.get_attribute("class")

    # Switch to history tab
    page.locator(".tab-btn[data-tab='history']").click()

    # Open it again by clicking a history image
    page.locator("#history-grid .history-item img").first.click()
    assert "hidden" not in lightbox.get_attribute("class")
    assert lightbox_image.get_attribute("src").endswith("hist1.jpg")

    # Click right zone and verify it navigates through history images (context-aware)
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("hist2.jpg")

    # Loop back
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("hist1.jpg")

    # Press Escape key and verify it closes
    page.keyboard.press("Escape")
    assert "hidden" in lightbox.get_attribute("class")

    # Test browser back interception
    page.locator("#gallery-slot-0 img").click()
    assert "hidden" not in lightbox.get_attribute("class")

    # Navigate back
    page.evaluate("window.history.back()")
    # Wait for the popstate event to propagate and hide the lightbox
    page.wait_for_function("document.getElementById('lightbox').classList.contains('hidden')")
    assert "hidden" in lightbox.get_attribute("class")
