import gradio as gr
import websocket
import uuid
import json
import urllib.request
import urllib.parse
from websockets.sync.client import connect
from PIL import Image
import io
import numpy as np
import random



ALLOWED_RESOLUTIONS = [
    '512 x 512', '704 x 1408', '704 x 1344', '768 x 1344', '768 x 1280', '832 x 1216',
    '832 x 1152', '896 x 1152', '896 x 1088', '960 x 1088', '960 x 1024', '1024 x 1024',
    '1024 x 960', '1088 x 960', '1088 x 896', '1152 x 896', '1152 x 832', '1216 x 832',
    '1280 x 768', '1344 x 768', '1344 x 704', '1408 x 704', '1472 x 704', '1536 x 640',
    '1600 x 640', '1664 x 576', '1728 x 576']
DEFAULT_RESOLUTION="1024 x 1024"

def get_available_options():
    opts = {}
    with urllib.request.urlopen("http://{}/object_info".format(server_address)) as response:
        nodes = json.loads(response.read())
        opts["models"] = nodes["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
        opts["sampler"] = nodes["KSampler"]["input"]["required"]["sampler_name"][0]
        opts["scheduler"] = nodes["KSampler"]["input"]["required"]["scheduler"][0]
        opts["seed_max"] = nodes["KSampler"]["input"]["required"]["seed"][1]["max"]
    return opts

def queue_prompt(prompt, client_id):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def comfy_clear_queue(client_id):
    p = {"clear": True, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/queue".format(server_address), data=data)
    urllib.request.urlopen(req)

def comfy_interrupt(client_id):
    p = {"client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/interrupt".format(server_address), data=data)
    urllib.request.urlopen(req)

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

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


def comfy_send_prompts(prompt, client_id, seed, count, state):
    # Create an RNG with our seed so we can ensure we get consistent
    # results across the different submissions
    rng = np.random.RandomState(seed & (2**32-1))

    ids = []

    # Queue each prompt with a seed derived from the user seed
    for _ in range(count):
        seed = int(rng.randint(state["options"]["seed_max"], dtype="uint64"))
        prompt["sampler"]["inputs"]["seed"] = seed

        ids.append(queue_prompt(prompt, client_id)['prompt_id'])
    return ids

def comfy_stream_updates(ws, prompt_ids):
    current_node = ""
    current_prompt = ""

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            print(message)
            if "data" not in message:
                continue
            data = message["data"]

            # There is nothing left in the queue and its not the start message
            if ("status" in data and
                "exec_info" in data["status"] and
                "queue_remaining" in data["status"]["exec_info"] and
                data["status"]["exec_info"]["queue_remaining"] == 0 and
                "sid" not in data):
                break

            if "prompt_id" not in data:
                continue
            if data["prompt_id"] not in prompt_ids:
                continue

            current_prompt = data["prompt_id"]

            if message['type'] == 'executing':
                current_node = data['node']
                yield {
                    "node": current_node,
                    "prompt": current_prompt
                }
            elif message['type'] == 'progress':
                max = data["max"]
                current = data["value"]
                progress = current/max * 100
                yield {
                    "node": current_node,
                    "progress": progress,
                    "prompt": current_prompt
                }
        else:
            # A binary payload is always some kind of image
            yield {
                "node": current_node,
                "image": Image.open(io.BytesIO(out[8:])),
                "prompt": current_prompt
            }

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
            "steps": 20
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
            "text": "bad hands"
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

def set_initial_state():
    state = {}
    state["client_id"] = str(uuid.uuid4())
    state["seed"] = str()

    options = get_available_options()
    state["options"] = options

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

css = """
.loader-container {
  display: flex; /* Use flex to align items horizontally */
  align-items: center; /* Center items vertically within the container */
  white-space: nowrap; /* Prevent line breaks within the container */
}

.progress-bar > .generating {
  display: none !important;
}

.progress-bar{
  height: 30px !important;
}

.progress-bar span {
    text-align: right;
    width: 215px;
}

/* Style the progress bar */
progress {
  appearance: none; /* Remove default styling */
  height: 20px; /* Set the height of the progress bar */
  border-radius: 5px; /* Round the corners of the progress bar */
  background-color: #f3f3f3; /* Light grey background */
  width: 100%;
  vertical-align: middle !important;
}

/* Style the progress bar container */
.progress-container {
  margin-left: 20px;
  margin-right: 20px;
  flex-grow: 1; /* Allow the progress container to take up remaining space */
}

/* Set the color of the progress bar fill */
progress::-webkit-progress-value {
  background-color: #3498db; /* Blue color for the fill */
}

progress::-moz-progress-bar {
  background-color: #3498db; /* Blue color for the fill in Firefox */
}

.generate-btn {
  height: 100%;
}
"""

with gr.Blocks(css=css) as server:
    state = gr.State({})

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


    with gr.Accordion("Advanced", open=False):
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
            steps = gr.Slider(1, 80, 20, step=1, label="Steps")
            sampler = gr.Dropdown(label="Sampler", allow_custom_value=False,
                                  filterable=False)
            scheduler = gr.Dropdown(label="Scheduler", allow_custom_value=False,
                                    filterable=False)
        with gr.Row():
            seed = gr.Number(label="Seed")

    server.load(set_initial_state, outputs=[state, model, sampler, scheduler, seed])

    @stop_btn.click(inputs=[state])
    def stop(state):
        comfy_clear_queue(state["client_id"])
        comfy_interrupt(state["client_id"])

    @skip_btn.click(inputs=[state])
    def skip(state):
        comfy_interrupt(state["client_id"])

    @generate_btn.click(inputs=[prompt, count, resolution, model, steps, sampler,
                                scheduler, negative_prompt, state, seed, stop_btn,
                                skip_btn, generate_btn],
                        outputs=[gallery, progress, preview_window, stop_btn,
                                 skip_btn, generate_btn, state])
    def generate(text, count, resolution, model, steps, sampler, scheduler, negative_prompt,
                 state, seed, stop_btn, skip_btn, generate_btn):
        client_id = state["client_id"]
        prompt = json.loads(prompt_text)

        prompt["sampler"]["inputs"]["sampler_name"] = sampler
        prompt["sampler"]["inputs"]["scheduler"] = scheduler
        prompt["sampler"]["inputs"]["steps"] = steps

        width, height = resolution.split(" x ")

        prompt["loader"]["inputs"]["ckpt_name"] = model
        prompt["latent_image"]["inputs"]["width"] = width
        prompt["latent_image"]["inputs"]["height"] = height
        prompt["positive_clip"]["inputs"]["text"] = text
        prompt["negative_clip"]["inputs"]["text"] = negative_prompt

        # For now, always use a batch of 1 and queue a request for
        # each image. This way we can skip/cancel and get previews
        prompt["latent_image"]["inputs"]["batch_size"] = 1

        ws = connect("ws://{}/ws?clientId={}".format(server_address, client_id), max_size=3000000)

        completed_images = []
        current_preview = None
        current_progress = 0

        prompt_ids = comfy_send_prompts(prompt, client_id, seed, count, state)

        for resp in comfy_stream_updates(ws, prompt_ids):
            state.update({"prompt_id": resp["prompt"]})
            if resp["node"] is None:
                # We've finished an item
                continue

            if "image" in resp:
                if resp["node"] == "save":
                    completed_images.append(resp["image"])
                elif resp["node"] == "sampler":
                    current_preview = resp["image"]
            elif "progress" in resp:
                current_progress = resp["progress"]

            progress = generate_progress_bar(current_progress, "Generating")

            preview = gr.Image(current_preview, visible=True)
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

server.launch()
