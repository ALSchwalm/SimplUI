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
        // Mock gallery images (2 completed, 1 preview, 1 completed)
        const gallery = document.getElementById('gallery-grid');
        gallery.innerHTML = '';
        gallery.classList.remove('hidden');
        
        // Slot 0: completed
        const slot0 = document.createElement('div');
        slot0.className = 'gallery-item';
        slot0.id = 'gallery-slot-0';
        const img0 = document.createElement('img');
        img0.src = 'img1.jpg';
        slot0.appendChild(img0);
        gallery.appendChild(slot0);

        // Slot 1: completed
        const slot1 = document.createElement('div');
        slot1.className = 'gallery-item';
        slot1.id = 'gallery-slot-1';
        const img1 = document.createElement('img');
        img1.src = 'img2.jpg';
        slot1.appendChild(img1);
        gallery.appendChild(slot1);

        // Slot 2: preview (has preview-badge)
        const slot2 = document.createElement('div');
        slot2.className = 'gallery-item';
        slot2.id = 'gallery-slot-2';
        const badge = document.createElement('span');
        badge.className = 'preview-badge';
        badge.textContent = 'Generating...';
        slot2.appendChild(badge);
        const img2 = document.createElement('img');
        img2.src = 'preview.jpg';
        slot2.appendChild(img2);
        gallery.appendChild(slot2);

        // Slot 3: completed
        const slot3 = document.createElement('div');
        slot3.className = 'gallery-item';
        slot3.id = 'gallery-slot-3';
        const img3 = document.createElement('img');
        img3.src = 'img3.jpg';
        slot3.appendChild(img3);
        gallery.appendChild(slot3);

        // Mock history state
        state.history = ['hist1.jpg', 'hist2.jpg'];
    }""")

    # Verify lightbox is initially hidden
    lightbox = page.locator("#lightbox")
    assert "hidden" in lightbox.get_attribute("class")

    # Click preview image and verify it does NOT open the lightbox
    page.locator("#gallery-slot-2 img").click()
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

    # Click right zone again (should skip preview.jpg and go to img3.jpg)
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

    # Simulating a new image generation completion while lightbox is open
    page.evaluate("""() => {
        const gallery = document.getElementById('gallery-grid');
        const slot4 = document.createElement('div');
        slot4.className = 'gallery-item';
        slot4.id = 'gallery-slot-4';
        const img4 = document.createElement('img');
        img4.src = 'img4.jpg';
        slot4.appendChild(img4);
        gallery.appendChild(slot4);

        // Trigger completed image handler
        handleCompletedImage('img4.jpg', 4);
    }""")

    # Click right zone: it should now navigate to img4.jpg
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("img4.jpg")

    # Click right zone again: it should loop to img1.jpg
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("img1.jpg")

    # Click close button and verify lightbox is hidden
    page.locator("#lightbox-close").click()
    assert "hidden" in lightbox.get_attribute("class")

    # Switch to history tab
    page.locator(".tab-btn[data-tab='history']").click()

    # Open it again by clicking the second history image (which is hist1.jpg)
    page.locator("#history-grid .history-item img").nth(1).click()
    assert "hidden" not in lightbox.get_attribute("class")
    assert lightbox_image.get_attribute("src").endswith("hist1.jpg")

    # Click right zone and verify it navigates through history images (context-aware)
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("hist2.jpg")

    # Loop back (includes img4.jpg as it is now part of the history context)
    page.locator("#lightbox-right-zone").click()
    assert lightbox_image.get_attribute("src").endswith("img4.jpg")

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
