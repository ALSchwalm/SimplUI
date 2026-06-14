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
                body='{"comfy_url": "http://localhost:8188", "workflows": [], "sliders": {}}',
            )
        else:
            route.continue_()

    page.route("**", handle_route)


def test_history_excludes_previews_on_completion(page):
    abs_path = os.path.abspath("static/index.html")
    page.goto(f"file://{abs_path}")

    # Set up a gallery slot and mock state
    page.evaluate("""() => {
        state.isConnected = true;
        state.isGenerating = true;
        state.batchCount = 1;
        state.currentBatchIndex = 0;
        
        // Initialize a slot
        createGallerySlot(0);
        
        // Set a live preview in it
        updateLivePreview('blob:preview-url-1', 0);
        
        // Mock activePrompts entry to represent our current prompt
        state.activePrompts['prompt-1'] = {
            index: 0,
            resolve: () => {}
        };
    }""")

    # Simulate websocket event: executing node === null (prompt completion)
    # when only the live preview is present in the slot (no final image was processed).
    page.evaluate("""() => {
        handleWebSocketMessage({
            type: 'executing',
            data: {
                node: null,
                prompt_id: 'prompt-1'
            }
        });
    }""")

    # Assert that history DOES NOT contain the preview blob URL
    history = page.evaluate("state.history")
    assert "blob:preview-url-1" not in history
    assert len(history) == 0


def test_history_only_contains_successful_final_images(page):
    abs_path = os.path.abspath("static/index.html")
    page.goto(f"file://{abs_path}")

    # Set up a gallery slot and mock state
    page.evaluate("""() => {
        state.isConnected = true;
        state.isGenerating = true;
        state.batchCount = 1;
        state.currentBatchIndex = 0;
        
        // Initialize slot
        createGallerySlot(0);
        
        // Set a live preview in it
        updateLivePreview('blob:preview-url-1', 0);
        
        state.activePrompts['prompt-1'] = {
            index: 0,
            resolve: () => {}
        };
    }""")

    # Now simulate a completed image event first (e.g. executed event)
    page.evaluate("""() => {
        handleCompletedImage('final-image-1.jpg', 0);
    }""")

    # Now simulate the prompt completion message
    page.evaluate("""() => {
        handleWebSocketMessage({
            type: 'executing',
            data: {
                node: null,
                prompt_id: 'prompt-1'
            }
        });
    }""")

    # History should contain exactly the final image and NOT the preview
    history = page.evaluate("state.history")
    assert "final-image-1.jpg" in history
    assert "blob:preview-url-1" not in history
    assert len(history) == 1
