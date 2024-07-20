import glob
import os
import json
import gradio as gr
import modules.utils
import modules.styles

PRESET_PATH = modules.utils.absolute_from_root_relative("./presets")


def read_presets():
    files = glob.glob("*.json", root_dir=PRESET_PATH)
    presets = {}
    for file in files:
        with open(os.path.join(PRESET_PATH, file)) as f:
            name = file.rstrip(".json")
            presets[name] = json.loads(f.read())
    return presets


PRESETS = read_presets()


def generate_preset_dropdown():
    return gr.Dropdown(label="Preset", value="default", choices=list(PRESETS.keys()))


def update_preset_state(
    preset,
    model_comp,
    sampler_comp,
    scheduler_comp,
    cfg_comp,
    prompt_comp,
    negative_prompt_comp,
    styles_comp,
    performance_comp,
    ratio_comp,
    scale_comp,
    vae_comp,
    skip_clip_comp,
    steps_comp,
    *lora_comps
):
    preset = PRESETS[preset]

    output = {}

    if "model" in preset:
        output[model_comp] = preset["model"]

    if "sampler" in preset:
        output[sampler_comp] = preset["sampler"]

    if "scheduler" in preset:
        output[scheduler_comp] = preset["scheduler"]

    if "cfg" in preset:
        output[cfg_comp] = preset["cfg"]

    if "prompt" in preset:
        output[prompt_comp] = preset["prompt"]

    if "negative_prompt" in preset:
        output[negative_prompt_comp] = preset["negative_prompt"]

    if "styles" in preset:
        styles, _ = modules.styles.generate_styles_list(preset["styles"], "", {})
        output[styles_comp] = styles

    if "performance" in preset:
        output[performance_comp] = preset["performance"]

    if "ratio" in preset:
        output[ratio_comp] = preset["ratio"]

    if "scale" in preset:
        output[scale_comp] = preset["scale"]

    if "vae" in preset:
        output[vae_comp] = preset["vae"]

    if "skip_clip" in preset:
        output[skip_clip_comp] = preset["skip_clip"]

    if "steps" in preset:
        output[steps_comp] = preset["steps"]

    if "loras" in preset:
        for i in range(0, len(lora_comps), 3):
            lora_idx = i // 3
            if lora_idx >= len(preset["loras"]):
                enabled = False
                lora_name = "None"
                weight = 1.0
            else:
                preset_lora = preset["loras"][lora_idx]
                enabled = True
                lora_name = preset_lora["lora_name"]
                weight = preset_lora["weight"]
            output[lora_comps[i]] = enabled
            output[lora_comps[i + 1]] = lora_name
            output[lora_comps[i + 2]] = weight

    return output
