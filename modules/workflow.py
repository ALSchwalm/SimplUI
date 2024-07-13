import json

BASIC_WORKFLOW = """
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

def render(model, sampler, scheduler, steps, width,
           height, positive, negative, cfg, loras):
    workflow = json.loads(BASIC_WORKFLOW)
    workflow["sampler"]["inputs"]["sampler_name"] = sampler
    workflow["sampler"]["inputs"]["scheduler"] = scheduler
    workflow["sampler"]["inputs"]["steps"] = steps

    workflow["loader"]["inputs"]["ckpt_name"] = model
    workflow["latent_image"]["inputs"]["width"] = width
    workflow["latent_image"]["inputs"]["height"] = height
    workflow["sampler"]["inputs"]["cfg"] = cfg

    workflow["positive_clip"]["inputs"]["text"] = positive
    workflow["negative_clip"]["inputs"]["text"] = negative

    # For now, always use a batch of 1 and queue a request for
    # each image. This way we can skip/cancel and get previews
    workflow["latent_image"]["inputs"]["batch_size"] = 1

    prior_node_name = "loader"
    for i in range(0, len(loras), 3):
        enabled, value, weight = loras[i:i+3]
        if not enabled:
            continue
        lora_node_name = f"lora_{i}"

        new_node = {
            lora_node_name: {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "lora_name": value,
                    "strength_model": weight,
                    "model": [
                        prior_node_name,
                        0
                    ],
                }
            }
        }
        prior_node_name = lora_node_name
        workflow.update(new_node)
        workflow["sampler"]["inputs"]["model"][0] = lora_node_name

    return workflow
