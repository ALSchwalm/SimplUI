import glob
import os
import json
import gradio as gr
import modules.utils

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

def update_preset_state(preset, model, sampler, scheduler, cfg, prompt,
                        negative_prompt, styles, performance, *loras):
    preset = PRESETS[preset]

    if "model" in preset:
        model = preset["model"]

    if "sampler" in preset:
        sampler = preset["sampler"]

    if "scheduler" in preset:
        scheduler = preset["scheduler"]

    if "cfg" in preset:
        cfg = preset["cfg"]

    if "prompt"in preset:
        prompt = preset["prompt"]

    if "negative_prompt" in preset:
        negative_prompt = preset["negative_prompt"]

    if "styles" in preset:
        styles = preset["styles"]

    loras = list(loras)
    if "loras" in preset:
        for i in range(0, len(loras), 3):
            lora_idx = i//3
            if lora_idx >= len(preset["loras"]):
                enabled = False
                lora_name = "None"
                weight = 1.0
            else:
                preset_lora = preset["loras"][lora_idx]
                enabled = True
                lora_name = preset_lora["lora_name"]
                weight = preset_lora["weight"]
            loras[i] = enabled
            loras[i+1] = lora_name
            loras[i+2] = weight

    if "performance" in preset:
        performance = preset["performance"]

    return (model, sampler, scheduler, cfg, prompt, negative_prompt,
            styles, performance, *loras)
