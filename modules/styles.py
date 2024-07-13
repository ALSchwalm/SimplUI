import os
import glob
import json
import gradio as gr

styles_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../styles/'))

def render_name(style_name):
    style_name = [p.title() for p in style_name.replace(" ", "-").split("-")]
    if style_name[0].lower() in ("mre", "mk", "sai"):
        style_name[0] = style_name[0].upper()
    return " ".join(style_name)

def read_styles():
    files = glob.glob("*.json", root_dir=styles_path)
    styles = []
    for file in files:
        with open(os.path.join(styles_path, file)) as f:
            file_styles = json.loads(f.read())
            for style in file_styles:
                style["name"] = render_name(style["name"])
                styles.append(style)
    return sorted(styles, key=lambda style: style["name"])

styles = read_styles()

def update_styles_state(selected, state):
    state["positive_styles"] = []
    state["negative_styles"] = []
    for style in styles:
        name = style["name"]
        if name not in selected:
            continue

        positive_prompt = style.get("prompt")
        if positive_prompt is not None:
            state["positive_styles"].append(positive_prompt)

        negative_prompt = style.get("negative_prompt")
        if negative_prompt is not None:
            state["negative_styles"].append(negative_prompt)

    return state

def generate_styles_list(selected, searched, state):
    output = []
    state["positive_styles"] = []
    state["negative_styles"] = []
    for style in styles:
        name = style["name"]
        if not searched or name in selected or searched.lower() in name.lower():
            output.append(name)

    state = update_styles_state(selected, state)

    return gr.CheckboxGroup(label="Styles", choices=output,
                            elem_classes=['style_selections'],
                            show_label=False, container=False), state

def render_styles_prompt(prompt, styles):
    for style in styles:
        if "{prompt}" in style:
            prompt = style.format(prompt=prompt)
        else:
            prompt += " " + style
    return prompt
