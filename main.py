import argparse
import gradio as gr
import uuid
from websockets.sync.client import connect
import random
import modules.styles
import modules.utils
import modules.html
import modules.comfy
import modules.workflow

ALLOWED_RESOLUTIONS = [
    '512 x 512', '704 x 1408', '704 x 1344', '768 x 1344', '768 x 1280', '832 x 1216',
    '832 x 1152', '896 x 1152', '896 x 1088', '960 x 1088', '960 x 1024', '1024 x 1024',
    '1024 x 960', '1088 x 960', '1088 x 896', '1152 x 896', '1152 x 832', '1216 x 832',
    '1280 x 768', '1344 x 768', '1344 x 704', '1408 x 704', '1472 x 704', '1536 x 640',
    '1600 x 640', '1664 x 576', '1728 x 576']
DEFAULT_RESOLUTION="1024 x 1024"

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

    loras = []
    for _ in range(6):
        loras.append(False)

        loras.append(gr.Dropdown(choices=state["options"]["loras"] + ["None"],
                                 interactive=True, value="None"))

        loras.append(1.0)

    seed = gr.Number(value=random.randrange(0, options["seed_max"]))
    return state, model, sampler, scheduler, seed, *loras

HEAD, ALLOWED_PATHS = modules.html.render_head()

def run(comfy_address):
    with gr.Blocks(head=HEAD) as server:
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
                    performance_rd = gr.Radio(["Quality", "Speed", "Lightening"], value="Speed", label="Performance")
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
                    with gr.Row():
                        cfg = gr.Slider(1.0, 10, 8, step=0.1, label="Cfg")
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

                with gr.Tab(label='Loras'):
                    with gr.Group():
                        lora_ctrls = []

                        for i in range(6):
                            with gr.Row():
                                lora_enabled = gr.Checkbox(label='Enable', value=False, scale=1,
                                                           elem_classes=['lora_enable', 'min_check'])
                                lora_model = gr.Dropdown(label=f'LoRA {i + 1}',
                                                         scale=5, elem_classes='lora_model')
                                lora_weight = gr.Slider(label='Weight', minimum=0, maximum=2.0, step=0.01,
                                                        value=1.0, scale=5, elem_classes='lora_weight', interactive=True)
                                lora_ctrls += [lora_enabled, lora_model, lora_weight]

        server.load(lambda: set_initial_state(comfy_address),
                    outputs=[state, model, sampler, scheduler, seed] + lora_ctrls)

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

        @performance_rd.input(inputs=[performance_rd, state, *lora_ctrls[-3:]],
                              outputs=[state, steps, cfg, scheduler, sampler, *lora_ctrls[-3:]])
        def performance(performance_rd, state, lora_enabled, lora_model, lora_weight):
            if performance_rd == "Quality":
                return [state, 60, 8.0, "normal", "euler_ancestral",
                        lora_enabled, lora_model, lora_weight]
            elif performance_rd == "Speed":
                return [state, 30, 8.0, "normal", "euler_ancestral",
                        lora_enabled, lora_model, lora_weight]
            elif performance_rd == "Lightening":
                return [state, 4, 1.0, "sgm_uniform", "dpmpp_2m_sde",
                        True, "sdxl_lightning_4step_lora.safetensors", 1.0]

        @stop_btn.click(inputs=[state])
        def stop(state):
            modules.comfy.clear_queue(comfy_address, state["client_id"])
            modules.comfy.interrupt(comfy_address, state["client_id"])

        @skip_btn.click(inputs=[state])
        def skip(state):
            modules.comfy.interrupt(comfy_address, state["client_id"])

        @generate_btn.click(inputs=[prompt, count, resolution, model, steps, sampler,
                                    scheduler, negative_prompt, state, seed, stop_btn,
                                    skip_btn, generate_btn, cfg, *lora_ctrls],
                            outputs=[gallery, progress, preview_window, stop_btn,
                                     skip_btn, generate_btn, state])
        def generate(text, count, resolution, model, steps, sampler, scheduler, negative_prompt,
                     state, seed, stop_btn, skip_btn, generate_btn, cfg, *lora_ctrls):
            client_id = state["client_id"]

            width, height = resolution.split(" x ")

            positive = modules.styles.render_styles_prompt(text, state["positive_styles"])
            negative = modules.styles.render_styles_prompt(negative_prompt, state["negative_styles"])

            workflow = modules.workflow.render(model, sampler, scheduler, steps, width, height,
                                               positive, negative, cfg, lora_ctrls)

            # Make max size large enough for the images
            ws = connect("ws://{}/ws?clientId={}".format(comfy_address, client_id), max_size=3000000)

            from pprint import pprint
            pprint(prompt)

            completed_images = []
            current_preview = None
            current_progress = 0

            prompt_ids = modules.comfy.send_prompts(comfy_address, workflow, client_id,
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
                progress = modules.html.generate_progress_bar(total_progress, resp["text"])

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
    server.launch(allowed_paths=ALLOWED_PATHS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run comfy-minimal')
    parser.add_argument('--listen', default="127.0.0.1",
                        help='set the address to listen on')
    parser.add_argument('--comfy-addr', default="127.0.0.1:8188",
                        help='The address of the comfy instance')
    args = parser.parse_args()
    run(args.comfy_addr)
