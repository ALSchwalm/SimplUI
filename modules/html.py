import modules.utils
import os

JS_PATH = modules.utils.absolute_from_root_relative("./assets/script.js")
SAMPLE_PATH = modules.utils.absolute_from_root_relative("./styles/samples/fooocus_v2.jpg")

HEAD = rf"""
<meta name="samples-path" content="gradio_api/file={SAMPLE_PATH}">
<script type="text/javascript" src="gradio_api/file={JS_PATH}"></script>
"""


def render_head():
    return HEAD, [JS_PATH, os.path.dirname(SAMPLE_PATH)]


def generate_progress_bar(value, message):
    template = """
    <div class="loader-container">
      <div class="progress-container">
        <progress value="{value}" max="100"></progress>
      </div>
      <span>{message}</span>
    </div>
    """

    return template.format(value=value, message=message)
