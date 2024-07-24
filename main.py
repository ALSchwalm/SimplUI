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
    "704×1408",
    "704×1344",
    "768×1344",
    "768×1280",
    "832×1216",
    "832×1152",
    "896×1152",
    "896×1088",
    "960×1088",
    "960×1024",
    "1024×1024",
    "1024×960",
    "1088×960",
    "1088×896",
    "1152×896",
    "1152×832",
    "1216×832",
    "1280×768",
    "1344×768",
    "1344×704",
    "1408×704",
    "1472×704",
    "1536×640",
    "1600×640",
    "1664×576",
    "1728×576",
]

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
    return [as_ratio(r, scale) for r in BASE_RESOLUTIONS]


def resolution_from_ratio(ratio):
    return ratio.split(" ")[-1]


def get_matching_ratio(ratio, ratio_list):
    return next(r for r in ratio_list if r.split(" ")[0] == ratio)


HEAD, ALLOWED_PATHS = modules.html.render_head()


def run(comfy_address, host, port):
    async def set_initial_state(
        state_comp,
        server_state_comp,
        model_comp,
        sampler_comp,
        scheduler_comp,
        cfg_comp,
        prompt_comp,
        negative_prompt_comp,
        styles_list_comp,
        performance_rd_comp,
        ratio_comp,
        scale_comp,
        vae_comp,
        skip_clip_comp,
        steps_comp,
        *lora_comps,
    ):
        state = {}
        state["client_id"] = str(uuid.uuid4())
        state["seed"] = str()

        options = await modules.comfy.get_available_options(comfy_address)
        pprint(options)

        state["options"] = options
        state["positive_styles"] = []
        state["negative_styles"] = []
        state["perf_lora"] = None

        # Getting this info can take a while, so store a task
        # that we'll await when we actually need the info. This
        # is not plain data, so it must be stored server side.
        server_state = {
            "model_details": await modules.comfy.get_model_details(comfy_address)
        }

        ratio_list = get_ratios_for_scale(DEFAULT_SCALE)
        default_ratio = get_matching_ratio(DEFAULT_RATIO, ratio_list)

        output = {
            model_comp: options["models"][0],
            sampler_comp: "euler_ancestral",
            scheduler_comp: "normal",
            cfg_comp: 8.0,
            prompt_comp: "",
            negative_prompt_comp: "",
            styles_list_comp: [],
            performance_rd_comp: "Speed",
            scale_comp: DEFAULT_SCALE,
            ratio_comp: default_ratio,
            vae_comp: "Builtin",
            skip_clip_comp: 2,
            steps_comp: 30,
        }

        preset = modules.presets.update_preset_state(
            "default",
            model_comp,
            sampler_comp,
            scheduler_comp,
            cfg_comp,
            prompt_comp,
            negative_prompt_comp,
            styles_list_comp,
            performance_rd_comp,
            ratio_comp,
            scale_comp,
            vae_comp,
            skip_clip_comp,
            steps_comp,
            *lora_comps,
        )
        output.update(preset)

        output[model_comp] = gr.Dropdown(
            choices=options["models"], value=output[model_comp]
        )

        output[sampler_comp] = gr.Dropdown(
            choices=options["sampler"], value=output[sampler_comp]
        )

        output[scheduler_comp] = gr.Dropdown(
            choices=options["scheduler"], value=output[scheduler_comp]
        )

        output[cfg_comp] = gr.Slider(value=output[cfg_comp])

        output[vae_comp] = gr.Dropdown(
            value=output[vae_comp], choices=options["vaes"] + ["Builtin"]
        )

        output[scale_comp] = gr.Dropdown(choices=SCALES, value=output[scale_comp])

        output[ratio_comp] = gr.Dropdown(choices=ratio_list, value=output[ratio_comp])
        output[skip_clip_comp] = gr.Slider(
            value=output[skip_clip_comp], maximum=options["skip_max"]
        )

        for i in range(0, len(lora_comps), 3):
            _, value_comp, _ = lora_comps[i : i + 3]
            if value_comp in output:
                lora_value = output[value_comp]
            else:
                lora_value = "None"
            output[lora_comps[i + 1]] = gr.Dropdown(
                choices=options["loras"] + ["None"], value=lora_value
            )

        output[state_comp] = state
        output[server_state_comp] = server_state
        return output

    with gr.Blocks(head=HEAD, title="SimplUI") as server:
        # Avoid using gr.State here, because that is lost if the server
        # restarts or after the timeout. But we know the client state is
        # actually all just available, we don't really keep anything. So
        # just let the client feed it back to us through this invisible
        # json component. Only downside here is that all "state" has to
        # be plain data.
        state_comp = gr.JSON({}, visible=False)

        # For things that are not plain data, we store them in this, but
        # keep in mind it will be lost if the client doesn't send anything
        # for a while. Ensure that isn't an error
        server_state_comp = gr.State()

        with gr.Row():
            with gr.Column(scale=2):
                with gr.Row():
                    preview_window_comp = gr.Image(
                        label="Preview",
                        show_label=True,
                        visible=False,
                        height=768,
                        elem_id="preview-image",
                    )
                    gallery_comp = gr.Gallery(
                        label="Gallery",
                        show_label=False,
                        object_fit="contain",
                        height=768,
                        elem_classes=[
                            "resizable_area",
                            "main_view",
                            "final_gallery",
                            "image_gallery",
                        ],
                        elem_id="final-gallery",
                    )

                progress_bar_comp = gr.HTML(
                    visible=False, elem_id="progress-bar", elem_classes="progress-bar"
                )

                with gr.Row():
                    with gr.Column(scale=17):
                        prompt_comp = gr.Textbox(label="Prompt", lines=2)

                    with gr.Column(scale=3):
                        generate_btn_comp = gr.Button(
                            "Generate",
                            variant="primary",
                            elem_id="generate-btn",
                            elem_classes="generate-btn",
                        )
                        skip_btn_comp = gr.Button("Skip", visible=False)
                        stop_btn_comp = gr.Button(
                            "Stop", variant="stop", visible=False, elem_id="stop-btn"
                        )

                with gr.Row():
                    advanced_checkbox_comp = gr.Checkbox(
                        label="Advanced", container=False
                    )

            with gr.Column(scale=1, visible=False) as advanced_column_comp:
                with gr.Tab(label="Setting"):
                    with gr.Group():
                        presets_comp = modules.presets.generate_preset_dropdown()
                        performance_rd_comp = gr.Radio(
                            ["Quality", "Speed", "Hyper"],
                            value="Speed",
                            label="Performance",
                        )

                    with gr.Row():
                        ratio_comp = gr.Dropdown(
                            label="Aspect Ratio",
                            allow_custom_value=False,
                            filterable=False,
                        )

                        scale_comp = gr.Dropdown(
                            label="Scale", allow_custom_value=False, filterable=False
                        )

                    with gr.Group():
                        count_comp = gr.Slider(1, 10, 2, step=1, label="Count")
                        negative_prompt_comp = gr.Textbox(
                            label="Negative Prompt", lines=2
                        )
                        with gr.Row():
                            seed_random_comp = gr.Checkbox(
                                label="Random Seed", value=True, scale=1
                            )

                            # Work around https://github.com/gradio-app/gradio/issues/5354
                            seed_comp = gr.Text(
                                label="Seed",
                                max_lines=1,
                                value="0",
                                visible=False,
                                scale=2,
                            )

                with gr.Tab(label="Styles", elem_classes=["style_selections_tab"]):
                    style_search_bar_comp = gr.Textbox(
                        show_label=False,
                        container=False,
                        placeholder="\U0001F50E Type here to search styles ...",
                        value="",
                        label="Search Styles",
                    )
                    styles_list_comp, _ = modules.styles.generate_styles_list([], "", {})

                    # "fake" element used to trigger re-sorting of the styles on blur
                    gradio_receiver_style_selections_comp = gr.Textbox(
                        elem_id="gradio_receiver_style_selections", visible=False
                    )

                with gr.Tab(label="Models"):
                    with gr.Group():
                        model_comp = gr.Dropdown(
                            label="Model", allow_custom_value=False, filterable=False
                        )

                        lora_comps = []

                        for i in range(6):
                            with gr.Row():
                                lora_enabled_comp = gr.Checkbox(
                                    label="Enable",
                                    value=False,
                                    scale=1,
                                    elem_classes=["lora_enable", "min_check"],
                                )
                                lora_model_comp = gr.Dropdown(
                                    label=f"LoRA {i + 1}",
                                    scale=5,
                                    elem_classes="lora_model",
                                )
                                lora_weight_comp = gr.Slider(
                                    label="Weight",
                                    minimum=0,
                                    maximum=2.0,
                                    step=0.01,
                                    value=1.0,
                                    scale=5,
                                    elem_classes="lora_weight",
                                    interactive=True,
                                )
                                lora_comps += [
                                    lora_enabled_comp,
                                    lora_model_comp,
                                    lora_weight_comp,
                                ]

                with gr.Tab(label="Advanced"):
                    with gr.Row():
                        steps_comp = gr.Slider(1, 80, 30, step=1, label="Steps")
                        sampler_comp = gr.Dropdown(
                            label="Sampler", allow_custom_value=False, filterable=False
                        )
                    with gr.Row():
                        cfg_comp = gr.Slider(
                            minimum=1.0, maximum=10, step=0.1, label="Cfg"
                        )
                        scheduler_comp = gr.Dropdown(
                            label="Scheduler", allow_custom_value=False, filterable=False
                        )

                    with gr.Row():
                        vae_comp = gr.Dropdown(
                            label="VAE", allow_custom_value=False, filterable=False
                        )
                        skip_clip_comp = gr.Slider(minimum=1, step=1, label="Skip CLIP")

        presetable_comps = [
            model_comp,
            sampler_comp,
            scheduler_comp,
            cfg_comp,
            prompt_comp,
            negative_prompt_comp,
            styles_list_comp,
            performance_rd_comp,
            ratio_comp,
            scale_comp,
            vae_comp,
            skip_clip_comp,
            steps_comp,
            *lora_comps,
        ]

        async def set_initial_state_apply():
            return await set_initial_state(
                state_comp, server_state_comp, *presetable_comps
            )

        server.load(
            set_initial_state_apply,
            outputs=[state_comp, server_state_comp] + presetable_comps,
        )

        style_search_bar_comp.change(
            modules.styles.generate_styles_list,
            inputs=[styles_list_comp, style_search_bar_comp, state_comp],
            outputs=[styles_list_comp, state_comp],
            queue=False,
            show_progress="hidden",
        )
        styles_list_comp.change(
            modules.styles.update_styles_state,
            inputs=[styles_list_comp, state_comp],
            outputs=[state_comp],
        )

        seed_random_comp.change(
            lambda rand: gr.Text(visible=rand is False),
            inputs=[seed_random_comp],
            outputs=[seed_comp],
            queue=False,
            show_progress="hidden",
        )

        presets_comp.change(
            lambda preset: modules.presets.update_preset_state(preset, *presetable_comps),
            inputs=[presets_comp],
            outputs=presetable_comps,
            show_progress=False,
        )

        advanced_checkbox_comp.change(
            lambda x: gr.update(visible=x),
            advanced_checkbox_comp,
            advanced_column_comp,
            queue=False,
            show_progress=False,
        )

        @gradio_receiver_style_selections_comp.change(
            inputs=[styles_list_comp, style_search_bar_comp], outputs=[styles_list_comp]
        )
        def style_blur(selected_styles, searched_styles):
            styles_list, _ = modules.styles.generate_styles_list(
                selected_styles, searched_styles, {}
            )
            return styles_list

        @scale_comp.change(
            inputs=[scale_comp, ratio_comp], outputs=[ratio_comp], show_progress=False
        )
        def ratio_change(scale, ratio):
            ratio_list = get_ratios_for_scale(scale)
            ratio = ratio.split(" ")[0]
            new_ratio = get_matching_ratio(ratio, ratio_list)
            return gr.Dropdown(choices=ratio_list, value=new_ratio)

        @performance_rd_comp.input(
            inputs=[performance_rd_comp, state_comp],
            outputs=[state_comp, steps_comp, cfg_comp, scheduler_comp, sampler_comp],
            show_progress=False,
        )
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

        @stop_btn_comp.click(inputs=[state_comp])
        async def stop(state):
            await modules.comfy.clear_queue(comfy_address, state["client_id"])
            await modules.comfy.interrupt(comfy_address, state["client_id"])

        @skip_btn_comp.click(inputs=[state_comp])
        async def skip(state):
            await modules.comfy.interrupt(comfy_address, state["client_id"])

        async def generate_fn(
            text,
            count,
            ratio,
            model,
            steps,
            sampler,
            scheduler,
            negative_prompt,
            state,
            server_state,
            seed,
            seed_random,
            stop_btn,
            skip_btn,
            generate_btn,
            cfg,
            vae,
            skip_clip,
            *lora_ctrls,
        ):
            # TODO: this is reflected from the client so we probably shouldn't
            # trust it.
            client_id = state["client_id"]

            width, height = resolution_from_ratio(ratio).split("×")

            positive = modules.styles.render_styles_prompt(text, state["positive_styles"])
            negative = modules.styles.render_styles_prompt(
                negative_prompt, state["negative_styles"]
            )

            # If the server has restarted or the client has timed out, there won't be
            # any server state object, so start the details gather task in case we need
            # it in the renderer
            if server_state is None or "model_details" not in server_state:
                model_details = await modules.comfy.get_model_details(comfy_address)
                # And go ahead and yield here to update the component so we don't
                # need to do this again
                yield {server_state_comp: {"model_details": model_details}}
            else:
                model_details = server_state["model_details"]

            workflow = await modules.workflow.render(
                model,
                sampler,
                scheduler,
                steps,
                width,
                height,
                positive,
                negative,
                cfg,
                vae,
                skip_clip,
                state["perf_lora"],
                model_details,
                lora_ctrls,
            )
            pprint(workflow)

            # Just show something so we quickly get the progress bar up
            progress = modules.html.generate_progress_bar(0, "Starting...")
            progress = gr.HTML(progress, visible=True)
            yield {progress_bar_comp: progress}

            # Make max size large enough for the images
            ws = await connect(
                f"ws://{comfy_address}/ws?clientId={client_id}", max_size=3000000
            )

            completed_images = []
            current_preview = None
            current_progress = 0

            if seed_random:
                # generate a new one and return it
                seed = random.randrange(0, int(state["options"]["seed_max"]))

            prompt_ids = await modules.comfy.send_prompts(
                comfy_address, workflow, client_id, int(seed), count, state
            )

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

                    total_progress = STATIC_PROGRESS + (1 - STATIC_PROGRESS / 100) * (
                        len(completed_images) * 100 / count + current_progress / count
                    )
                    progress = modules.html.generate_progress_bar(
                        total_progress, resp["text"]
                    )

                    preview = gr.Image(
                        current_preview, visible=current_preview is not None
                    )
                    progress = gr.HTML(progress, visible=True)
                    stop_btn = gr.Button(visible=True)
                    skip_btn = gr.Button(visible=True)
                    generate_btn = gr.Button(visible=False)

                    # Hide the gallery if we don't have a completed image yet
                    if len(completed_images) == 0 and current_preview is not None:
                        output_images = gr.Gallery(visible=False)
                    else:
                        output_images = gr.Gallery(completed_images, visible=True)

                    yield {
                        gallery_comp: output_images,
                        progress_bar_comp: progress,
                        preview_window_comp: preview,
                        stop_btn_comp: stop_btn,
                        skip_btn_comp: skip_btn,
                        generate_btn_comp: generate_btn,
                        state_comp: state,
                        seed_comp: seed,
                    }

                yield {
                    gallery_comp: gr.Gallery(completed_images, visible=True),
                    progress_bar_comp: gr.HTML(visible=False),
                    preview_window_comp: gr.Image(visible=False),
                    stop_btn_comp: gr.Button(visible=False),
                    skip_btn_comp: gr.Button(visible=False),
                    generate_btn_comp: gr.Button(visible=True),
                    state_comp: state,
                    seed_comp: seed,
                }
            except GeneratorExit:
                modules.comfy.clear_queue(comfy_address, state["client_id"])
                modules.comfy.interrupt(comfy_address, state["client_id"])
                ws.close()
                raise

        generate_btn_comp.click(
            generate_fn,
            inputs=[
                prompt_comp,
                count_comp,
                ratio_comp,
                model_comp,
                steps_comp,
                sampler_comp,
                scheduler_comp,
                negative_prompt_comp,
                state_comp,
                server_state_comp,
                seed_comp,
                seed_random_comp,
                stop_btn_comp,
                skip_btn_comp,
                generate_btn_comp,
                cfg_comp,
                vae_comp,
                skip_clip_comp,
                *lora_comps,
            ],
            outputs=[
                gallery_comp,
                progress_bar_comp,
                preview_window_comp,
                stop_btn_comp,
                skip_btn_comp,
                generate_btn_comp,
                state_comp,
                server_state_comp,
                seed_comp,
            ],
            show_progress="hidden",
        )
    server.launch(allowed_paths=ALLOWED_PATHS, server_name=host, server_port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SimplUI")
    parser.add_argument(
        "--listen", default="127.0.0.1", help="set the address to listen on"
    )
    parser.add_argument(
        "--port", type=int, default=7860, help="set the port to listen on"
    )
    parser.add_argument(
        "--comfy-addr", default="127.0.0.1:8188", help="The address of the comfy instance"
    )
    args = parser.parse_args()
    run(args.comfy_addr, args.listen, args.port)
