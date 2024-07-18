import threading
import urllib.request
import urllib.parse
import urllib.error
from PIL import Image
import json
import io
import numpy as np

def get_available_options(comfy_address):
    opts = {}
    with urllib.request.urlopen(f"http://{comfy_address}/object_info") as response:
        nodes = json.loads(response.read())
        opts["models"] = nodes["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
        opts["sampler"] = nodes["KSampler"]["input"]["required"]["sampler_name"][0]
        opts["scheduler"] = nodes["KSampler"]["input"]["required"]["scheduler"][0]
        opts["seed_max"] = nodes["KSampler"]["input"]["required"]["seed"][1]["max"]
        opts["loras"] = nodes["LoraLoaderModelOnly"]["input"]["required"]["lora_name"][0]
        opts["vaes"] = nodes["VAELoader"]["input"]["required"]["vae_name"][0]
        opts["skip_max"] = -1 * nodes["CLIPSetLastLayer"]["input"]["required"]["stop_at_clip_layer"][1]["min"]
    return opts

def get_model_details(comfy_address):
    def _get_model_details():
        req = urllib.request.Request(f"http://{comfy_address}/etn/model_info")
        value = json.loads(urllib.request.urlopen(req).read())
        # Well, it's python so we might as well mutate types
        threading.current_thread().result = value
    t = threading.Thread(target=_get_model_details)
    t.start()
    return t


def queue_prompt(comfy_address, prompt, client_id):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request(f"http://{comfy_address}/prompt", data=data)
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        print(e.fp.read())
        raise

def clear_queue(comfy_address, client_id):
    p = {"clear": True, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request(f"http://{comfy_address}/queue", data=data)
    urllib.request.urlopen(req)

def interrupt(comfy_address, client_id):
    p = {"client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request(f"http://{comfy_address}/interrupt", data=data)
    urllib.request.urlopen(req)


def send_prompts(comfy_address, prompt, client_id, seed, count, state):
    # Create an RNG with our seed so we can ensure we get consistent
    # results across the different submissions
    rng = np.random.RandomState(seed & (2**32-1))

    ids = []

    # Queue each prompt with a seed derived from the user seed
    for _ in range(count):
        prompt["sampler"]["inputs"]["seed"] = seed
        ids.append(queue_prompt(comfy_address, prompt, client_id)['prompt_id'])
        seed = int(rng.randint(state["options"]["seed_max"], dtype="uint64"))
    return ids

def render_node_text(node_data):
    match node_data["node"]:
        case "sampler":
            if "value" in node_data and "max" in node_data:
                return "Sampling Step {}/{}".format(node_data["value"], node_data["max"])
            else:
                return "Preparing sampling"
        case "negative_clip":
            return "Encoding negative"
        case "positive_clip":
            return "Encoding positive"
        case "loader":
            return "Loading model"
        case "vae":
            return "Rendering"
        case "save":
            return "Downloading image"
        case _:
            return ""

def stream_updates(ws, prompt_ids):
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
                    "prompt": current_prompt,
                    "text": render_node_text(data)
                }
            elif message['type'] == 'progress' and data["node"] == "sampler":
                max = data["max"]
                current = data["value"]
                progress = current/max * 100
                yield {
                    "node": current_node,
                    "progress": progress,
                    "prompt": current_prompt,
                    "text": render_node_text(data)
                }
        else:
            # A binary payload is always some kind of image
            yield {
                "node": current_node,
                "image": Image.open(io.BytesIO(out[8:])),
                "prompt": current_prompt,
                "text": render_node_text(data)
            }
