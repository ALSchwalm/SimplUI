import argparse
import gradio as gr
import uuid
from websockets.client import connect
from pprint import pprint
import random
import math
import modules.styles
import modules.html
import modules.comfy
import modules.workflow
import modules.presets

# Show the bar 10% full after starting
STATIC_PROGRESS = 10

BASE_RESOLUTIONS = [
    '704×1408', '704×1344', '768×1344', '768×1280', '832×1216',
    '832×1152', '896×1152', '896×1088', '960×1088', '960×1024', '1024×1024',
    '1024×960', '1088×960', '1088×896', '1152×896', '1152×832', '1216×832',
    '1280×768', '1344×768', '1344×704', '1408×704', '1472×704', '1536×640',
    '1600×640', '1664×576', '1728×576']

SCALES = ["0.5 (SD1.5)", "0.75", "1.0 (SDXL)", "1.25", "1.5"]
DEFAULT_SCALE = "1.0 (SDXL)"
DEFAULT_RATIO = "7:9"

def as_ratio(resolution, scale):
    a, b = resolution.split("×")
    a = int(a)
    b = int(b)
    g = math.gcd(a, b)
    ratio = f"{a // g}:{b // g}"
    return f"{ratio} \U00002223 {int(a * scale)}×{int(b * scale)}"

def get_ratios_for_scale(scale):
    scale = float(scale.split(" ")[0])
    return [
        as_ratio(r, scale) for r in BASE_RESOLUTIONS
    ]

def resolution_from_ratio(ratio):
    return ratio.split(" ")[-1]

def get_matching_ratio(ratio, ratio_list):
    return next(r for r in ratio_list if r.split(" ")[0] == ratio)

HEAD, ALLOWED_PATHS = modules.html.render_head()

def run(comfy_address):
    async def set_initial_state():
        state = {}
        state["client_id"] = str(uuid.uuid4())
        state["seed"] = str()

        options = await modules.comfy.get_available_options(comfy_address)
        state["options"] = options
        state["positive_styles"] = []
        state["negative_styles"] = []
        state["perf_lora"] = None

        # Getting this info can take a while, so store a task
        # that we'll await when we actually need the info
        state["model_details"] = await modules.comfy.get_model_details(comfy_address)

        fallback_model = options["models"][0]
        fallback_sampler = "euler_ancestral"
        fallback_scheduler = "normal"
        fallback_cfg = 8.0
        fallback_prompt = ""
        fallback_negative_prompt = ""
        fallback_styles = []
        fallback_loras = [False, "None", 1.0] * 6
        fallback_performance = "Speed"
        fallback_vae = "Builtin"
        fallback_skip_clip = 2

        model, sampler, scheduler, cfg, prompt, negative_prompt, styles, performance, *loras = \
            modules.presets.update_preset_state(
                "default", fallback_model, fallback_sampler, fallback_scheduler,
                fallback_cfg, fallback_prompt, fallback_negative_prompt, fallback_styles,
                fallback_performance, *fallback_loras)

        model = gr.Dropdown(choices=options["models"],
                            value=model)

        sampler = gr.Dropdown(value=fallback_sampler,
                              choices=options["sampler"])

        scheduler = gr.Dropdown(value=fallback_scheduler,
                                choices=options["scheduler"])

        vae = gr.Dropdown(value=fallback_vae,
                                choices=options["vaes"] + ["Builtin"])

        scale = gr.Dropdown(choices=SCALES, value=DEFAULT_SCALE)

        ratio_list = get_ratios_for_scale(DEFAULT_SCALE)
        default_ratio = get_matching_ratio(DEFAULT_RATIO, ratio_list)
        ratio = gr.Dropdown(choices=ratio_list, value=default_ratio)

        cfg = gr.Slider(value=cfg)
        skip_clip = gr.Slider(value=fallback_skip_clip, maximum=options["skip_max"])

        pprint(options)

        styles, _ = modules.styles.generate_styles_list(styles, "", {})

        for i in range(0, len(loras), 3):
            _, value, _ = loras[i:i+3]
            loras[i+1] = gr.Dropdown(choices=options["loras"] + ["None"],
                                     value=value)

        return (state, model, sampler, scheduler, cfg, prompt,
                negative_prompt, styles, performance, vae, skip_clip,
                ratio, scale, *loras)

    with gr.Blocks(head=HEAD) as server:
        state = gr.State({})

        with gr.Row():
            with gr.Column(scale=2):
                with gr.Row():
                    preview_window = gr.Image(label='Preview', show_label=True, visible=False,
                                              height=768, elem_id="preview-image")
                    gallery = gr.Gallery(label='Gallery', show_label=False, object_fit='contain', height=768,
                                         elem_classes=['resizable_area', 'main_view', 'final_gallery', 'image_gallery'],
                                         elem_id='final_gallery')

                progress_bar = gr.HTML(visible=False, elem_id='progress-bar', elem_classes='progress-bar')

                with gr.Row():
                    with gr.Column(scale=17):
                        prompt = gr.Textbox(label="Prompt", lines=2)

                    with gr.Column(scale=3):
                        generate_btn = gr.Button("Generate", variant="primary", elem_id='generate-btn',
                                                 elem_classes='generate-btn')
                        skip_btn = gr.Button("Skip", visible=False)
                        stop_btn = gr.Button("Stop", variant="stop", visible=False, elem_id='stop-btn')

                with gr.Row():
                    advanced_checkbox = gr.Checkbox(label="Advanced", container=False)

            with gr.Column(scale=1, visible=False) as advanced_column:
                with gr.Tab(label='Setting'):
                    with gr.Group():
                        presets = modules.presets.generate_preset_dropdown()
                        performance_rd = gr.Radio(["Quality", "Speed", "Hyper"],
                                                  value="Speed", label="Performance")

                    with gr.Row():
                        ratio = gr.Dropdown(label="Aspect Ratio",
                                            allow_custom_value=False,
                                            filterable=False)

                        scale = gr.Dropdown(label="Scale",
                                            allow_custom_value=False,
                                            filterable=False)

                    with gr.Group():
                        count = gr.Slider(1, 10, 2, step=1, label="Count")
                        negative_prompt = gr.Textbox(label="Negative Prompt", lines=2)
                        with gr.Row():
                            seed_random = gr.Checkbox(label='Random Seed', value=True, scale=1)

                            # Work around https://github.com/gradio-app/gradio/issues/5354
                            seed = gr.Text(label="Seed", max_lines=1, value="0", visible=False, scale=2)

                with gr.Tab(label='Styles', elem_classes=['style_selections_tab']):
                    style_search_bar = gr.Textbox(show_label=False, container=False,
                                                  placeholder="\U0001F50E Type here to search styles ...",
                                                  value="",
                                                  label='Search Styles')
                    styles_list, _ = modules.styles.generate_styles_list([], "", {})

                    # "fake" element used to trigger re-sorting of the styles on blur
                    gradio_receiver_style_selections = gr.Textbox(elem_id='gradio_receiver_style_selections', visible=False)

                with gr.Tab(label='Models'):
                    with gr.Group():
                        model = gr.Dropdown(label="Model",
                                            allow_custom_value=False,
                                            filterable=False)

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

                with gr.Tab(label='Advanced'):
                    with gr.Row():
                        steps = gr.Slider(1, 80, 30, step=1, label="Steps")
                        sampler = gr.Dropdown(label="Sampler", allow_custom_value=False,
                                              filterable=False)
                    with gr.Row():
                        cfg = gr.Slider(minimum=1.0, maximum=10, step=0.1, label="Cfg")
                        scheduler = gr.Dropdown(label="Scheduler", allow_custom_value=False,
                                                filterable=False)

                    with gr.Row():
                        vae = gr.Dropdown(label="VAE", allow_custom_value=False, filterable=False)
                        skip_clip = gr.Slider(minimum=1, step=1, label="Skip CLIP")

        server.load(set_initial_state, outputs=[state, model, sampler, scheduler, cfg,
                                                prompt, negative_prompt, styles_list,
                                                performance_rd, vae, skip_clip,
                                                ratio, scale] + lora_ctrls)

        style_search_bar.change(modules.styles.generate_styles_list,
                                inputs=[styles_list, style_search_bar, state],
                                outputs=[styles_list, state],
                                queue=False,
                                show_progress="hidden")
        styles_list.change(modules.styles.update_styles_state,
                           inputs=[styles_list, state],
                           outputs=[state])

        seed_random.change(lambda rand: gr.Text(visible=rand is False),
                           inputs=[seed_random],
                           outputs=[seed],
                           queue=False,
                           show_progress="hidden")

        presets.change(modules.presets.update_preset_state,
                       inputs=[presets, model, sampler, scheduler, cfg, prompt, negative_prompt,
                               styles_list, performance_rd, *lora_ctrls],
                       outputs=[model, sampler, scheduler, cfg, prompt, negative_prompt, styles_list,
                                performance_rd, *lora_ctrls],
                       show_progress=False)

        advanced_checkbox.change(lambda x: gr.update(visible=x), advanced_checkbox, advanced_column,
                                 queue=False, show_progress=False)

        @gradio_receiver_style_selections.change(inputs=[styles_list, style_search_bar],
                                                 outputs=[styles_list])
        def style_blur(selected_styles, searched_styles):
            styles_list, _ = modules.styles.generate_styles_list(selected_styles,
                                                                 searched_styles, {})
            return styles_list

        @scale.change(inputs=[scale, ratio], outputs=[ratio], show_progress=False)
        def ratio_change(scale, ratio):
            ratio_list = get_ratios_for_scale(scale)
            ratio = ratio.split(" ")[0]
            new_ratio = get_matching_ratio(ratio, ratio_list)
            return gr.Dropdown(choices=ratio_list, value=new_ratio)

        @performance_rd.input(inputs=[performance_rd, state],
                              outputs=[state, steps, cfg, scheduler, sampler],
                              show_progress=False)
        async def performance(performance_rd, state):
            match performance_rd:
                case "Quality":
                    state["perf_lora"] = None
                    return [state, 60, 8.0, "normal", "euler_ancestral"]
                case "Speed":
                    state["perf_lora"] = None
                    return [state, 30, 8.0, "normal", "euler_ancestral"]
                case "Hyper":
                    state["perf_lora"] = "Hyper"
                    return [state, 4, 1.0, "sgm_uniform", "dpmpp_2m_sde"]

        @stop_btn.click(inputs=[state])
        async def stop(state):
            await modules.comfy.clear_queue(comfy_address, state["client_id"])
            await modules.comfy.interrupt(comfy_address, state["client_id"])

        @skip_btn.click(inputs=[state])
        async def skip(state):
            await modules.comfy.interrupt(comfy_address, state["client_id"])

        async def generate_fn(text, count, ratio, model, steps, sampler, scheduler, negative_prompt,
                     state, seed, seed_random, stop_btn, skip_btn, generate_btn, cfg, vae,
                     skip_clip, *lora_ctrls):
            client_id = state["client_id"]

            width, height = resolution_from_ratio(ratio).split("×")

            positive = modules.styles.render_styles_prompt(text, state["positive_styles"])
            negative = modules.styles.render_styles_prompt(negative_prompt, state["negative_styles"])

            workflow = await modules.workflow.render(model, sampler, scheduler, steps, width, height,
                                                     positive, negative, cfg, vae, skip_clip, state["perf_lora"],
                                                     state["model_details"], lora_ctrls)
            pprint(workflow)

            # Just show something so we quickly get the progress bar up
            progress = modules.html.generate_progress_bar(0, "Starting...")
            progress = gr.HTML(progress, visible=True)
            yield {
                progress_bar: progress
            }

            # Make max size large enough for the images
            ws = await connect(f"ws://{comfy_address}/ws?clientId={client_id}", max_size=3000000)

            completed_images = []
            current_preview = None
            current_progress = 0

            if seed_random:
                # generate a new one and return it
                seed = random.randrange(0, state["options"]["seed_max"])

            prompt_ids = await modules.comfy.send_prompts(comfy_address, workflow, client_id,
                                                          int(seed), count, state)

            try:
                async for resp in modules.comfy.stream_updates(ws, prompt_ids):
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

                    total_progress = STATIC_PROGRESS + (1-STATIC_PROGRESS/100) * \
                        (len(completed_images) * 100 / count + current_progress / count)
                    progress = modules.html.generate_progress_bar(total_progress, resp["text"])

                    preview = gr.Image(current_preview, visible=current_preview is not None)
                    progress = gr.HTML(progress, visible=True)
                    stop_btn = gr.Button(visible=True)
                    skip_btn = gr.Button(visible=True)
                    generate_btn = gr.Button(visible=False)

                    # Hide the gallery if we don't have a completed image yet
                    if len(completed_images) == 0 and current_preview is not None:
                        output_images = gr.Gallery(visible=False)
                    else:
                        output_images = gr.Gallery(completed_images, visible=True)

                    yield [output_images, progress, preview, stop_btn, skip_btn,
                           generate_btn, state, seed]

                yield [
                    gr.Gallery(completed_images, visible=True),
                    gr.HTML(visible=False),
                    gr.Image(visible=False),
                    gr.Button(visible=False),
                    gr.Button(visible=False),
                    gr.Button(visible=True),
                    state,
                    seed
                ]
            except GeneratorExit:
                modules.comfy.clear_queue(comfy_address, state["client_id"])
                modules.comfy.interrupt(comfy_address, state["client_id"])
                ws.close()
                raise

        generate_btn.click(generate_fn,
                       inputs=[prompt, count, ratio, model, steps, sampler,
                               scheduler, negative_prompt, state, seed, seed_random,
                               stop_btn, skip_btn, generate_btn, cfg, vae, skip_clip, *lora_ctrls],
                       outputs=[gallery, progress_bar, preview_window, stop_btn,
                                skip_btn, generate_btn, state, seed],
                       show_progress="hidden")
    server.launch(allowed_paths=ALLOWED_PATHS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run comfy-minimal')
    parser.add_argument('--listen', default="127.0.0.1",
                        help='set the address to listen on')
    parser.add_argument('--comfy-addr', default="127.0.0.1:8188",
                        help='The address of the comfy instance')
    args = parser.parse_args()
    run(args.comfy_addr)
