import gradio as gr
import websocket
import uuid
import json
import urllib.request
import urllib.parse
from websockets.sync.client import connect
from PIL import Image
import io

#TODO: this should be separate
client_id = str(uuid.uuid4())

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
    return opts

def queue_prompt(prompt):
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

def get_images(ws, prompt, progress):
    prompt_id = queue_prompt(prompt)['prompt_id']
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
            elif message['type'] == 'progress' and message["data"]["node"] == "3":
                max = message["data"]["max"]
                current = message["data"]["value"]
                progress(current/max)

        else:
            if current_node == 'save_image_websocket_node':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output
    return output_images

prompt_text = """
{
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8,
            "denoise": 1,
            "latent_image": [
                "latent_image",
                0
            ],
            "model": [
                "4",
                0
            ],
            "negative": [
                "7",
                0
            ],
            "positive": [
                "6",
                0
            ],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 8566257,
            "steps": 20
        }
    },
    "4": {
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
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": ""
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": "bad hands"
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": [
                "3",
                0
            ],
            "vae": [
                "4",
                2
            ]
        }
    },
    "save_image_websocket_node": {
        "class_type": "SaveImageWebsocket",
        "inputs": {
            "images": [
                "8",
                0
            ]
        }
    }
}
"""

with gr.Blocks() as demo:
    options = get_available_options()

    gallery = gr.Gallery(label='Gallery', show_label=False, object_fit='contain', visible=True, height=768,
                         elem_classes=['resizable_area', 'main_view', 'final_gallery', 'image_gallery'],
                         elem_id='final_gallery')
    progress = gr.Progress()
    prompt = gr.Textbox(label="Prompt", lines=2, visible=True)
    generate_btn = gr.Button("Generate")
    with gr.Row():
        count = gr.Slider(1, 10, 2, step=1, label="Count")
        resolution = gr.Dropdown(choices=ALLOWED_RESOLUTIONS,
                                 value=DEFAULT_RESOLUTION,
                                 label="Resolution",
                                 interactive=True,
                                 allow_custom_value=False,
                                 filterable=False)

        model = gr.Dropdown(choices=options["models"],
                            value=options["models"][0],
                            label="Model",
                            interactive=True,
                            allow_custom_value=False,
                            filterable=False)

    with gr.Row():
        steps = gr.Slider(1, 80, 20, step=1, label="Steps")
        sampler = gr.Dropdown(choices=options["sampler"], value="euler_ancestral", label="Sampler")
        scheduler = gr.Dropdown(choices=options["scheduler"], value="normal", label="Scheduler")

    @generate_btn.click(inputs=[prompt, count, resolution, model, steps, sampler, scheduler], outputs=gallery)
    def generate(text, count, resolution, model, steps, sampler, scheduler):
        prompt = json.loads(prompt_text)

        #set the seed for our KSampler node
        prompt["3"]["inputs"]["seed"] = 5
        prompt["3"]["inputs"]["sampler_name"] = sampler
        prompt["3"]["inputs"]["scheduler"] = scheduler
        prompt["3"]["inputs"]["steps"] = steps

        width, height = resolution.split(" x ")

        prompt["4"]["inputs"]["ckpt_name"] = model
        prompt["latent_image"]["inputs"]["batch_size"] = count
        prompt["latent_image"]["inputs"]["width"] = width
        prompt["latent_image"]["inputs"]["height"] = height
        prompt["6"]["inputs"]["text"] = text

        ws = connect("ws://{}/ws?clientId={}".format(server_address, client_id), max_size=3000000)
        images = get_images(ws, prompt, progress)
        for node_id in images:
            return [Image.open(io.BytesIO(d)) for d in images[node_id]]


demo.launch()
