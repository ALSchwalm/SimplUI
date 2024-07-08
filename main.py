import gradio as gr
import websocket
import uuid
import json
import urllib.request
import urllib.parse
from websockets.sync.client import connect
from PIL import Image
import io
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

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt, progress, client_id):
    prompt_id = queue_prompt(prompt, client_id)['prompt_id']
    print(prompt_id)

    output_images = {}
    current_node = ""
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            print(message)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break #Execution is done
                    else:
                        current_node = data['node']
            elif message['type'] == 'progress':
                if message["data"]["node"] == "sampler":
                    progress_message = "Generating"
                elif message["data"]["node"] == "save":
                    progress_message = "Receiving"
                else:
                    progress_message = None
                max = message["data"]["max"]
                current = message["data"]["value"]
                progress(current/max, progress_message)
        else:
            if current_node == 'save':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output
            else:
                yield [Image.open(io.BytesIO(out[8:]))]
                print("Got binary message: ", current_node)
    print("returning full image")
    yield [Image.open(io.BytesIO(d)) for d in output_images["save"]]

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

with gr.Blocks() as server:
    state = gr.State({})

    gallery = gr.Gallery(label='Gallery', show_label=False, object_fit='contain', visible=True, height=768,
                         elem_classes=['resizable_area', 'main_view', 'final_gallery', 'image_gallery'],
                         elem_id='final_gallery')
    progress = gr.Progress()

    prompt = gr.Textbox(label="Prompt", lines=2, visible=True)
    generate_btn = gr.Button("Generate")
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

    @generate_btn.click(inputs=[prompt, count, resolution, model, steps, sampler,
                                scheduler, negative_prompt, state, seed],
                        outputs=gallery)
    def generate(text, count, resolution, model, steps, sampler, scheduler, negative_prompt, state, seed):
        client_id = state["client_id"]
        prompt = json.loads(prompt_text)

        prompt["sampler"]["inputs"]["seed"] = seed
        prompt["sampler"]["inputs"]["sampler_name"] = sampler
        prompt["sampler"]["inputs"]["scheduler"] = scheduler
        prompt["sampler"]["inputs"]["steps"] = steps

        width, height = resolution.split(" x ")

        prompt["loader"]["inputs"]["ckpt_name"] = model
        prompt["latent_image"]["inputs"]["batch_size"] = count
        prompt["latent_image"]["inputs"]["width"] = width
        prompt["latent_image"]["inputs"]["height"] = height
        prompt["positive_clip"]["inputs"]["text"] = text
        prompt["negative_clip"]["inputs"]["text"] = negative_prompt

        ws = connect("ws://{}/ws?clientId={}".format(server_address, client_id), max_size=3000000)
        images = get_images(ws, prompt, progress, client_id)
        for img_list in images:
            print("got a list of images: ", len(img_list))
            yield img_list

server.launch()
