import os
import pytest


@pytest.fixture(autouse=True)
def setup_routing(page):
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


def test_fresh_session_clears_local_storage(page):
    abs_path = os.path.abspath("static/index.html")
    page.goto(f"file://{abs_path}")

    # Set some state in localStorage
    page.evaluate("localStorage.setItem('simplui_overrides_test', '{\"test\": 123}')")
    assert page.evaluate("localStorage.getItem('simplui_overrides_test')") is not None

    # Reload the page to trigger initialization
    page.reload()

    # Assert that localStorage is cleared on initialization
    assert page.evaluate("localStorage.getItem('simplui_overrides_test')") is None
    assert page.evaluate("localStorage.length") == 0


def test_beforeunload_dialog_registered(page):
    abs_path = os.path.abspath("static/index.html")
    page.goto(f"file://{abs_path}")

    # Dispatch a cancelable beforeunload event and check if it gets default-prevented
    default_prevented = page.evaluate("""() => {
        const event = new Event('beforeunload', { cancelable: true });
        window.dispatchEvent(event);
        return event.defaultPrevented;
    }""")
    assert default_prevented is True
