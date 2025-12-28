import json

SDXL_HYPER_LORA = "Hyper-SDXL-4steps-lora.safetensors"
SD15_HYPER_LORA = "Hyper-SD15-4steps-lora.safetensors"

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
    "aura_shift": {
        "class_type": "ModelSamplingAuraFlow",
        "inputs": {
            "model": [
                "loader",
                0
            ],
            "shift": 1.0
        }
    },
    "upscale_sampler": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8,
            "denoise": 0.3,
            "latent_image": [
                "upscale_vae_encode",
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
            "sampler_name": "dpmpp_2m",
            "scheduler": "simple",
            "seed": 0,
            "steps": 1
        }
    },
    "upscale_vae_decode": {
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
    "upscale_vae_encode": {
        "class_type": "VAEEncode",
        "inputs": {
            "pixels": [
                "upscaler",
                0
            ],
            "vae": [
                "loader",
                2
            ]
        }
    },
    "upscaler" : {
        "class_type": "ImageScaleBy",
        "inputs": {
            "image": [
                "upscale_vae_decode",
                0
            ],
            "upscale_method": "nearest-exact",
            "scale_by": 0.0
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
                "skip_clip",
                0
            ],
            "text": ""
        }
    },
    "negative_clip": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "skip_clip",
                0
            ],
            "text": ""
        }
    },
    "vae_decode": {
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
    "skip_clip": {
        "class_type": "CLIPSetLastLayer",
        "inputs": {
            "clip": [
                "loader",
                 1
            ],
            "stop_at_clip_layer": -2
        }
    },
    "clip": {
        "class_type": "CLIPLoader",
        "inputs": {
            "clip_name": "",
            "clip_type": ""
        }
    },
    "save": {
        "class_type": "SaveImageWebsocket",
        "inputs": {
            "images": [
                "vae_decode",
                0
            ]
        }
    }
}
"""


def link_lora_to_workflow(node_name, workflow, lora_name, weight):
    prior_node_name = workflow["sampler"]["inputs"]["model"][0]
    new_node = {
        node_name: {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "lora_name": lora_name,
                "strength_model": weight,
                "model": [prior_node_name, 0],
            },
        }
    }
    workflow.update(new_node)
    workflow["sampler"]["inputs"]["model"][0] = node_name


async def render(
    model,
    sampler,
    scheduler,
    steps,
    upscale_steps,
    width,
    height,
    scale,
    positive,
    negative,
    cfg,
    vae,
    skip_clip,
    clip,
    clip_type,
    aura_shift,
    perf_lora,
    model_details,
    loras,
):
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

    clip_source = ["loader", 1]

    # If there is a specific clip, then that is the source
    if clip != "Builtin":
        workflow["clip"]["inputs"]["clip_name"] = clip
        workflow["clip"]["inputs"]["type"] = clip_type
        clip_source = ["clip", 0]
    else:
        del workflow["clip"]

    # The skip clip takes from the source
    workflow["skip_clip"]["inputs"]["clip"] = clip_source

    # But if skip clip is off, just bypass the whole skip node
    if skip_clip != 0:
        workflow["skip_clip"]["inputs"]["stop_at_clip_layer"] = skip_clip * -1
    else:
        workflow["positive_clip"]["inputs"]["clip"] = clip_source
        workflow["negative_clip"]["inputs"]["clip"] = clip_source

    # For now, always use a batch of 1 and queue a request for
    # each image. This way we can skip/cancel and get previews
    workflow["latent_image"]["inputs"]["batch_size"] = 1

    # If there is an aura shift, use it
    if aura_shift != 0:
        workflow["sampler"]["inputs"]["model"] = ["aura_shift", 0]

    for i in range(0, len(loras), 3):
        enabled, value, weight = loras[i : i + 3]
        if not enabled:
            continue
        lora_node_name = f"lora_{i}"
        link_lora_to_workflow(lora_node_name, workflow, value, weight)

    if perf_lora is not None:
        match perf_lora:
            case "Hyper":
                details = await model_details
                base_model = details[model]["base_model"]
                if base_model == "sdxl":
                    link_lora_to_workflow(perf_lora, workflow, SDXL_HYPER_LORA, 1.0)
                elif base_model == "sd15":
                    link_lora_to_workflow(perf_lora, workflow, SD15_HYPER_LORA, 1.0)
                else:
                    # TODO: show an error here
                    pass

    if vae != "Builtin":
        vae_node = {
            "vae_load": {
                "class_type": "VAELoader",
                "inputs": {
                    "vae_name": vae,
                },
            }
        }
        workflow.update(vae_node)
        workflow["vae_decode"]["inputs"]["vae"][0] = "vae_load"
        workflow["vae_decode"]["inputs"]["vae"][1] = 0

    if scale > 1.0:
        workflow["vae_decode"]["inputs"]["samples"][0] = "upscale_sampler"
        workflow["upscaler"]["inputs"]["scale_by"] = scale
        workflow["upscale_sampler"]["inputs"]["steps"] = upscale_steps

    return workflow
