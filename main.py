import argparse
import gradio as gr
import uuid
import json
from websockets.sync.client import connect
import random
import modules.styles
import modules.utils
import modules.html
import modules.comfy

ALLOWED_RESOLUTIONS = [
    '512 x 512', '704 x 1408', '704 x 1344', '768 x 1344', '768 x 1280', '832 x 1216',
    '832 x 1152', '896 x 1152', '896 x 1088', '960 x 1088', '960 x 1024', '1024 x 1024',
    '1024 x 960', '1088 x 960', '1088 x 896', '1152 x 896', '1152 x 832', '1216 x 832',
    '1280 x 768', '1344 x 768', '1344 x 704', '1408 x 704', '1472 x 704', '1536 x 640',
    '1600 x 640', '1664 x 576', '1728 x 576']
DEFAULT_RESOLUTION="1024 x 1024"

def generate_progress_bar(value, message):
    template = '''
    <div class="loader-container">
      <div class="progress-container">
        <progress value="{value}" max="100"></progress>
      </div>
      <span>{message}</span>
    </div>
    '''

    return template.format(value=value, message=message)

prompt_text = """
{
    "sampler": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8,
            "denoise": 1,
            "latent_image": [
                "latent_image",
                0
            ],
            "model": [
                "loader",
                0
            ],
            "negative": [
                "negative_clip",
                0
            ],
            "positive": [
                "positive_clip",
                0
            ],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 0,
            "steps": 0
        }
    },
    "loader": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": ""
        }
    },
    "latent_image": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "batch_size": 0,
            "height": 0,
            "width": 0
        }
    },
    "positive_clip": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "loader",
                1
            ],
            "text": ""
        }
    },
    "negative_clip": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "loader",
                1
            ],
            "text": ""
        }
    },
    "vae": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": [
                "sampler",
                0
            ],
            "vae": [
                "loader",
                2
            ]
        }
    },
    "save": {
        "class_type": "SaveImageWebsocket",
        "inputs": {
            "images": [
                "vae",
                0
            ]
        }
    }
}
"""

def set_initial_state(comfy_address):
    state = {}
    state["client_id"] = str(uuid.uuid4())
    state["seed"] = str()

    options = modules.comfy.get_available_options(comfy_address)
    state["options"] = options
    state["positive_styles"] = []
    state["negative_styles"] = []

    model = gr.Dropdown(choices=options["models"],
                        value=options["models"][0],
                        interactive=True)

    sampler = gr.Dropdown(value="euler_ancestral",
                          choices=options["sampler"],
                          interactive=True)

    scheduler = gr.Dropdown(value="normal",
                            choices=options["scheduler"],
                            interactive=True)


    seed = gr.Number(value=random.randrange(0, options["seed_max"]))
    return state, model, sampler, scheduler, seed


CSS_PATH = modules.utils.absolute_from_root_relative("./assets/style.css")
JS_PATH = modules.utils.absolute_from_root_relative("./assets/script.js")

def run(comfy_address):
    with gr.Blocks(head=modules.html.HEAD, css=CSS_PATH, js=JS_PATH) as server:
        state = gr.State({})

        with gr.Row():
            with gr.Column(scale=2):
                with gr.Row():
                    preview_window = gr.Image(label='Preview', show_label=True, visible=False,
                                              height=768)
                    gallery = gr.Gallery(label='Gallery', show_label=False, object_fit='contain', visible=True, height=768,
                                         elem_classes=['resizable_area', 'main_view', 'final_gallery', 'image_gallery'],
                                         elem_id='final_gallery')

                progress = gr.HTML(visible=False, elem_id='progress-bar', elem_classes='progress-bar')

                with gr.Row():
                    with gr.Column(scale=17):
                        prompt = gr.Textbox(label="Prompt", lines=2, visible=True)

                    with gr.Column(scale=3):
                        generate_btn = gr.Button("Generate", variant="primary", elem_id='generate-btn',
                                                 elem_classes='generate-btn', visible=True)
                        skip_btn = gr.Button("Skip", visible=False)
                        stop_btn = gr.Button("Stop", variant="stop", visible=False)

                with gr.Row():
                    advanced_checkbox = gr.Checkbox(label="Advanced", container=False)

            with gr.Column(scale=1, visible=False) as advanced_column:
                with gr.Tab(label='Setting'):
                    performance_rd = gr.Radio(["Quality", "Speed", "Hyper"], value="Speed", label="Performance")
                    negative_prompt = gr.Textbox(label="Negative Prompt", lines=2, visible=True)
                    with gr.Row():
                        count = gr.Slider(1, 10, 2, step=1, label="Count")
                        resolution = gr.Dropdown(choices=ALLOWED_RESOLUTIONS,
                                                 value=DEFAULT_RESOLUTION,
                                                 label="Resolution",
                                                 interactive=True,
                                                 allow_custom_value=False,
                                                 filterable=False)

                        model = gr.Dropdown(label="Model",
                                            allow_custom_value=False,
                                            filterable=False)

                    with gr.Row():
                        steps = gr.Slider(1, 80, 30, step=1, label="Steps")
                        sampler = gr.Dropdown(label="Sampler", allow_custom_value=False,
                                              filterable=False)
                        scheduler = gr.Dropdown(label="Scheduler", allow_custom_value=False,
                                                filterable=False)
                    with gr.Row():
                        seed = gr.Number(label="Seed")
                with gr.Tab(label='Styles', elem_classes=['style_selections_tab']):
                    style_search_bar = gr.Textbox(show_label=False, container=False,
                                                  placeholder="\U0001F50E Type here to search styles ...",
                                                  value="",
                                                  label='Search Styles')
                    styles_list, _ = modules.styles.generate_styles_list([], "", {})

        server.load(lambda: set_initial_state(comfy_address),
                    outputs=[state, model, sampler, scheduler, seed])

        style_search_bar.change(modules.styles.generate_styles_list,
                                inputs=[styles_list, style_search_bar, state],
                                outputs=[styles_list, state],
                                queue=False,
                                show_progress="hidden")
        styles_list.change(modules.styles.update_styles_state,
                           inputs=[styles_list, state],
                           outputs=[state])

        advanced_checkbox.change(lambda x: gr.update(visible=x), advanced_checkbox, advanced_column,
                                 queue=False, show_progress=False)

        @performance_rd.input(inputs=[performance_rd, state], outputs=[state, steps])
        def performance(performance_rd, state):
            if performance_rd == "Quality":
                return [state, 60]
            elif performance_rd == "Speed":
                return [state, 30]
            elif performance_rd == "Hyper":
                return [state, 4]

        @stop_btn.click(inputs=[state])
        def stop(state):
            modules.comfy.clear_queue(comfy_address, state["client_id"])
            modules.comfy.interrupt(comfy_address, state["client_id"])

        @skip_btn.click(inputs=[state])
        def skip(state):
            modules.comfy.interrupt(comfy_address, state["client_id"])

        @generate_btn.click(inputs=[prompt, count, resolution, model, steps, sampler,
                                    scheduler, negative_prompt, state, seed, stop_btn,
                                    skip_btn, generate_btn, performance_rd],
                            outputs=[gallery, progress, preview_window, stop_btn,
                                     skip_btn, generate_btn, state])
        def generate(text, count, resolution, model, steps, sampler, scheduler, negative_prompt,
                     state, seed, stop_btn, skip_btn, generate_btn, performance_rd):
            client_id = state["client_id"]
            prompt = json.loads(prompt_text)

            prompt["sampler"]["inputs"]["sampler_name"] = sampler
            prompt["sampler"]["inputs"]["scheduler"] = scheduler
            prompt["sampler"]["inputs"]["steps"] = steps

            # FIXME: for now just stick hyper in here
            if performance_rd == "Hyper":
                new_node = {
                    "hyper": {
                        "class_type": "LoraLoaderModelOnly",
                        "inputs": {
                            "lora_name": "sdxl_lightning_4step_lora.safetensors",
                            "strength_model": 1.0,
                            "model": [
                                "loader",
                                0
                            ],

                        }
                    }
                }
                prompt.update(new_node)
                prompt["sampler"]["inputs"]["model"][0] = "hyper"
                prompt["sampler"]["inputs"]["cfg"] = 1.0
                prompt["sampler"]["inputs"]["sampler_name"] = "dpmpp_2m_sde"
                prompt["sampler"]["inputs"]["scheduler"] = "sgm_uniform"

            width, height = resolution.split(" x ")

            prompt["loader"]["inputs"]["ckpt_name"] = model
            prompt["latent_image"]["inputs"]["width"] = width
            prompt["latent_image"]["inputs"]["height"] = height

            prompt["positive_clip"]["inputs"]["text"] = modules.styles.render_styles_prompt(
                text, state["positive_styles"])
            prompt["negative_clip"]["inputs"]["text"] = modules.styles.render_styles_prompt(
                negative_prompt, state["negative_styles"])

            # For now, always use a batch of 1 and queue a request for
            # each image. This way we can skip/cancel and get previews
            prompt["latent_image"]["inputs"]["batch_size"] = 1

            ws = connect("ws://{}/ws?clientId={}".format(comfy_address, client_id), max_size=3000000)

            from pprint import pprint
            pprint(prompt)

            completed_images = []
            current_preview = None
            current_progress = 0

            prompt_ids = modules.comfy.send_prompts(comfy_address, prompt, client_id,
                                                    seed, count, state)

            for resp in modules.comfy.stream_updates(ws, prompt_ids):
                state.update({"prompt_id": resp["prompt"]})
                if resp["node"] is None:
                    # We've finished an item
                    continue

                if "image" in resp:
                    if resp["node"] == "save":
                        completed_images.append(resp["image"])
                        current_progress = 0
                    elif resp["node"] == "sampler":
                        current_preview = resp["image"]
                elif "progress" in resp:
                    current_progress = resp["progress"]

                total_progress = len(completed_images) * 100 / count + current_progress / count
                progress = generate_progress_bar(total_progress, resp["text"])

                preview = gr.Image(current_preview, visible=current_preview is not None)
                progress = gr.HTML(progress, visible=True)
                stop_btn = gr.Button(visible=True)
                skip_btn = gr.Button(visible=True)
                generate_btn = gr.Button(visible=False)

                yield [completed_images, progress, preview, stop_btn, skip_btn,
                       generate_btn, state]

            yield [
                completed_images,
                gr.HTML(visible=False),
                gr.Image(visible=False),
                gr.Button(visible=False),
                gr.Button(visible=False),
                gr.Button(visible=True),
                state
            ]
    server.launch(allowed_paths=[
        modules.utils.absolute_from_root_relative("./styles/samples")
    ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run comfy-minimal')
    parser.add_argument('--listen', default="127.0.0.1",
                        help='set the address to listen on')
    parser.add_argument('--comfy-addr', default="127.0.0.1:8188",
                        help='The address of the comfy instance')
    args = parser.parse_args()
    run(args.comfy_addr)
