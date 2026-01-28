import pytest
from playwright.sync_api import Page, expect


def test_gallery_height_constraint(page: Page):
    """
    Verifies that the gallery component has a height constraint of 70vh.
    """
    # The gallery is created with elem_id="gallery"
    gallery = page.locator("#gallery")
    expect(gallery).to_be_visible()

    # We evaluate the style property directly on the element to see if our forced style is applied.
    # Note: Gradio might apply it to a wrapper, but usually elem_id targets the main container.
    # If the user sets height="70vh" in python, it should reflect in the styles.

    # We check if the height style is explicitly set to 70vh
    # We look at the inline style or computed style if we can trace it back to the rule.
    # Check computed height against viewport.

    # We'll assert that the element or its parent has the height restriction.
    # Let's start by checking the #gallery element.

    # We wait for it to be visible first
    expect(gallery).to_be_visible()

    # We use a custom expectation: "height" style should be "70vh"
    # This might fail if Gradio puts it on a wrapper.
    # If so, we'll adjust the test (and the implementation) to match.

    # We check computed height to allow for CSS class/stylesheet application
    computed_height_px = gallery.evaluate("el => window.getComputedStyle(el).height")

    viewport = page.viewport_size
    assert viewport is not None
    expected_px = viewport["height"] * 0.7

    # Clean up the string (e.g., "500px")
    if computed_height_px and "px" in computed_height_px:
        actual_px = float(computed_height_px.replace("px", ""))
    else:
        actual_px = 0

    # Allow margin (e.g. 2 pixels for rounding)
    assert (
        abs(actual_px - expected_px) < 5
    ), f"Expected approx {expected_px}px (70vh), got {actual_px}px (from {computed_height_px})"


def test_gallery_image_contain(page: Page):
    """
    Verifies that images within the gallery have object-fit: contain.
    """
    # Trigger a generation to get an image
    page.get_by_label("Prompt").fill("Test prompt for layout")
    page.get_by_role("button", name="Generate").click()

    # Wait for completion
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=10000)

    # Find the image element inside the gallery
    image = page.locator("#gallery img").first
    expect(image).to_be_visible()

    # Check object-fit style
    object_fit = image.evaluate("el => window.getComputedStyle(el).objectFit")
    assert object_fit == "contain", f"Expected object-fit 'contain', got '{object_fit}'"


def test_gallery_image_fits_container(page: Page):
    """
    Verifies that the generated image dimensions do not exceed the gallery container dimensions.
    """
    # Trigger a generation to get an image
    page.get_by_label("Prompt").fill("Test prompt for fitting")
    page.get_by_role("button", name="Generate").click()

    # Wait for completion
    expect(page.get_by_text("Generation complete").first).to_be_visible(timeout=10000)

    gallery = page.locator("#gallery")
    image = gallery.locator("img").first
    expect(image).to_be_visible()

    # Get bounding boxes
    g_box = gallery.bounding_box()
    i_box = image.bounding_box()

    # Debug styles
    styles = image.evaluate("""el => {
        const s = window.getComputedStyle(el);
        return { height: s.height, width: s.width, display: s.display, visibility: s.visibility, opacity: s.opacity };
    }""")
    print(f"DEBUG: Image styles: {styles}")
    print(f"DEBUG: Image box: {i_box}")
    print(f"DEBUG: Gallery box: {g_box}")

    # Allow small margin for borders/padding (e.g. 5px)
    assert (
        i_box["height"] <= g_box["height"] + 5
    ), f"Image height {i_box['height']} > Gallery height {g_box['height']}"
    assert (
        i_box["width"] <= g_box["width"] + 5
    ), f"Image width {i_box['width']} > Gallery width {g_box['width']}"

    # Ensure image is not collapsed
    assert (
        i_box["height"] > 100
    ), f"Image height {i_box['height']} is too small! Image might be hidden."
    assert (
        i_box["width"] > 100
    ), f"Image width {i_box['width']} is too small! Image might be hidden."

    # Check vertical alignment (ensure it's not pushed down significantly)
    # Allows 100px for label/padding
    assert (
        i_box["y"] < g_box["y"] + 100
    ), f"Image is pushed down too far (y={i_box['y']} vs gallery y={g_box['y']}). Likely vertical centering issue."
