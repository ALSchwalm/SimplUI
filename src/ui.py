import gradio as gr
import json
import asyncio
from PIL import Image
import io
import copy
import random

try:
    from .seed_utils import generate_batch_seeds
    from .dimension_utils import (
        find_matching_preset,
        find_nearest_preset,
        calculate_dimensions,
    )
except ImportError:
    from seed_utils import generate_batch_seeds
    from dimension_utils import (
        find_matching_preset,
        find_nearest_preset,
        calculate_dimensions,
    )


def extract_workflow_inputs(workflow, object_info=None, slider_config=None):
    extracted = []
    for node_id, node_data in workflow.items():
        title = node_data.get("_meta", {}).get("title", f"Node {node_id}")
        class_type = node_data.get("class_type", "")
        inputs = []
        is_prompt_node = title.lower() == "prompt"

        node_inputs = node_data.get("inputs", {})
        has_width = "width" in node_inputs
        has_height = "height" in node_inputs

        # Get node definition from object_info
        node_def = None
        if object_info and class_type in object_info:
            node_def = object_info[class_type]

        if has_width and has_height:
            # Special 'dimensions' type
            inputs.append(
                {
                    "name": "Dimensions",
                    "type": "dimensions",
                    "width_name": "width",
                    "height_name": "height",
                    "width_value": node_inputs["width"],
                    "height_value": node_inputs["height"],
                }
            )

        for name, value in node_inputs.items():
            if isinstance(value, list):
                continue  # Skip links

            # Filter out the primary prompt input from advanced controls
            if is_prompt_node and name in ["text", "string"]:
                continue

            # Filter out width/height if we grouped them
            if has_width and has_height and name in ["width", "height"]:
                continue

            input_type = "str"
            options = None
            slider_params = {}

            # Check for Enum/Number in object_info
            if node_def:
                # Inputs can be in 'required' or 'optional'
                input_def = node_def.get("input", {}).get("required", {}).get(name)
                if not input_def:
                    input_def = node_def.get("input", {}).get("optional", {}).get(name)

                # If input definition is a list
                if isinstance(input_def, list) and len(input_def) > 0:
                    # Enum
                    if isinstance(input_def[0], list):
                        input_type = "enum"
                        options = input_def[0]
                    # Number definition from object_info
                    elif len(input_def) > 1 and isinstance(input_def[1], dict):
                        # Format: ["INT", {"default": 20, "min": 1, "max": 10000}]
                        meta_params = input_def[1]
                        if "min" in meta_params and "max" in meta_params:
                            slider_params["min"] = meta_params["min"]
                            slider_params["max"] = meta_params["max"]
                            slider_params.setdefault(
                                "step", meta_params.get("step")
                            )  # step might be missing

            if input_type != "enum":
                if isinstance(value, bool):
                    input_type = "bool"
                elif isinstance(value, (int, float)):
                    if "seed" in name.lower():
                        input_type = "seed"
                    else:
                        input_type = "number"

                        # Check config override/default first
                        if slider_config and name in slider_config:
                            input_type = "slider"
                            slider_params.update(slider_config[name])
                        elif "min" in slider_params and "max" in slider_params:
                            input_type = "slider"

            input_data = {"name": name, "type": input_type, "value": value}
            if input_type == "seed":
                input_data["randomize"] = value == 0 or value == "0"

            if options:
                input_data["options"] = options

            if input_type == "slider":
                input_data.update(slider_params)

            inputs.append(input_data)

        if inputs:
            extracted.append({"node_id": node_id, "title": title, "inputs": inputs})
    return extracted


def merge_workflow_overrides(workflow, overrides):
    merged = copy.deepcopy(workflow)
    if not overrides:
        return merged
    for key, value in overrides.items():
        if "." in key and not key.endswith(".randomize"):
            node_id, input_name = key.split(".", 1)
            if node_id in merged and "inputs" in merged[node_id]:
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                merged[node_id]["inputs"][input_name] = value
    return merged


def apply_random_seeds(overrides):
    updated = copy.deepcopy(overrides)
    for key, value in overrides.items():
        if key.endswith(".randomize") and value is True:
            base_key = key[:-10]  # remove .randomize
            new_seed = random.randint(0, 18446744073709551615)
            updated[base_key] = str(new_seed)
    return updated


def get_prompt_default_value(workflow):
    for node_data in workflow.values():
        title = node_data.get("_meta", {}).get("title", "")
        if title.lower() == "prompt":
            inputs = node_data.get("inputs", {})
            if "text" in inputs:
                return str(inputs["text"])
            if "string" in inputs:
                return str(inputs["string"])
    return ""


async def handle_generation(workflow_name, prompt_text, config, comfy_client, overrides=None):
    # 1. Find workflow path
    workflow_info = next(w for w in config.workflows if w["name"] == workflow_name)

    # 2. Load workflow JSON
    try:
        with open(workflow_info["path"], "r") as f:
            workflow_json = json.load(f)
    except Exception as e:
        yield [], None, f"Error loading workflow: {e}"
        return

    # 2.5 Apply Overrides
    if overrides:
        workflow_json = merge_workflow_overrides(workflow_json, overrides)

    # 3. Inject Prompt if provided
    if prompt_text:
        comfy_client.inject_prompt(workflow_json, prompt_text)

    # 4. Generate Image (Connect -> Submit -> Listen)
    try:
        completed_images = []
        latest_preview = None
        last_status = "Starting..."
        async for event in comfy_client.generate_image(workflow_json):
            if event["type"] == "progress":
                last_status = f"Progress: {event['value']}/{event['max']}"
                # Yield completed images, latest preview, and status
                yield list(completed_images), latest_preview, last_status
            elif event["type"] == "preview":
                try:
                    preview_image = Image.open(io.BytesIO(event["data"]))
                    latest_preview = preview_image
                    yield list(completed_images), latest_preview, last_status
                except Exception as e:
                    pass
            elif event["type"] == "image":
                image_bytes = event["data"]
                try:
                    final_image = Image.open(io.BytesIO(image_bytes))
                    completed_images.append(final_image)
                    latest_preview = None  # Clear preview as it is replaced by final image
                    yield list(completed_images), latest_preview, "Generation complete"
                except Exception as e:
                    yield list(completed_images), latest_preview, f"Error processing image: {e}"
    except Exception as e:
        yield [], None, f"Error during generation: {e}"


async def process_generation(
    workflow_name,
    prompt_text,
    overrides,
    batch_count,
    config,
    comfy_client,
    object_info,
    history_state,
    skip_event=None,
):
    # Initial status: Hide Generate, Show Stop, Show Skip
    yield None, "Initializing...", gr.update(visible=False), gr.update(visible=True), gr.update(
        visible=True
    ), gr.update(), history_state[:], []

    # Auto-stop previous runs
    try:
        comfy_client.interrupt()
        comfy_client.clear_queue()
        # Small delay to ensure server processes interrupt before new submission
        await asyncio.sleep(0.1)
    except Exception:
        pass

    # Load Workflow JSON
    workflow_info = next(w for w in config.workflows if w["name"] == workflow_name)
    with open(workflow_info["path"], "r") as f:
        workflow_json = json.load(f)

    # Augment overrides with default random seeds
    if overrides is None:
        overrides = {}

    extracted = extract_workflow_inputs(workflow_json, object_info, config.sliders)
    for node in extracted:
        for inp in node["inputs"]:
            if inp["type"] == "seed":
                key = f"{node['node_id']}.{inp['name']}"
                random_key = f"{key}.randomize"

                is_random = False
                if random_key in overrides:
                    is_random = overrides[random_key]
                else:
                    # If not in overrides, use default from extraction (True if value is 0)
                    is_random = inp.get("randomize", False)

                if is_random and key not in overrides:
                    new_seed = random.randint(0, 18446744073709551615)
                    overrides[key] = str(new_seed)
                    overrides[random_key] = True

    # Apply random seeds
    if overrides:
        new_overrides = apply_random_seeds(overrides)
        if new_overrides != overrides:
            overrides = new_overrides
            # Update store with new seeds - Keep button state
            yield None, "Randomizing seeds...", gr.update(visible=False), gr.update(
                visible=True
            ), gr.update(visible=True), overrides, history_state[:], []
        else:
            # Still need to hide generate/show stop
            yield None, "Starting generation...", gr.update(visible=False), gr.update(
                visible=True
            ), gr.update(visible=True), gr.update(), history_state[:], []

    # Calculate Batch Seeds
    seed_batches = {}
    for node in extracted:
        for inp in node["inputs"]:
            if inp["type"] == "seed":
                key = f"{node['node_id']}.{inp['name']}"
                if overrides and key in overrides:
                    base = int(overrides[key])
                else:
                    base = int(inp["value"])
                seed_batches[key] = generate_batch_seeds(base, batch_count)

    previous_images = []
    finished_naturally = False
    last_status = "Processing..."
    last_safe_images = []

    try:
        for i in range(batch_count):
            # Clear skip event for this iteration
            if skip_event:
                skip_event.clear()

            iter_overrides = overrides.copy() if overrides else {}

            current_seeds = {}
            for key, batch in seed_batches.items():
                seed_val = batch[i]
                iter_overrides[key] = str(seed_val)  # Store as string for overrides compatibility
                current_seeds[key] = seed_val

            seed_suffix = f" (Batch {i+1}/{batch_count})"

            current_completed = []

            # Manual async iteration to support skip/cancellation
            iterator = handle_generation(
                workflow_name, prompt_text, config, comfy_client, iter_overrides
            ).__aiter__()

            while True:
                # Check skip signal
                if skip_event and skip_event.is_set():
                    break

                try:
                    # Create tasks for next update and skip signal
                    next_task = asyncio.create_task(iterator.__anext__())
                    tasks = [next_task]
                    if skip_event:
                        skip_task = asyncio.create_task(skip_event.wait())
                        tasks.append(skip_task)

                    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                    # Check if skip was triggered
                    if skip_event and skip_event.is_set():
                        next_task.cancel()  # Cancel pending generation task
                        # Yield safe state (remove preview)
                        safe_images = previous_images + current_completed
                        yield safe_images, "Skipping...", gr.update(visible=False), gr.update(
                            visible=True
                        ), gr.update(visible=True), gr.update(), history_state[:], safe_images
                        break  # Break inner loop

                    # If we are here, next_task completed successfully
                    try:
                        update = next_task.result()
                        run_completed, run_preview, status = update
                        last_status = status
                        current_completed = run_completed

                        # Construct display list: previous + current_completed + [preview]
                        safe_images = previous_images + current_completed
                        last_safe_images = safe_images

                        display_images = list(safe_images)
                        if run_preview:
                            display_images.append(run_preview)

                        # Add seeds to status if available
                        seed_info = ""
                        # Seed info removed from status display per requirements
                        # if current_seeds:
                        #    seed_info = f" Seed: {list(current_seeds.values())[0]}"

                        yield display_images, last_status + seed_info + seed_suffix, gr.update(
                            visible=False
                        ), gr.update(visible=True), gr.update(
                            visible=True
                        ), gr.update(), history_state[
                            :
                        ], safe_images

                    except StopAsyncIteration:
                        # Generator finished normally
                        # If we finished naturally, current_completed contains the FINAL images for this run.
                        # Update history state
                        history_state.extend(current_completed)
                        break
                    except Exception as e:
                        yield last_safe_images, f"Error: {e}", gr.update(
                            visible=True, interactive=True
                        ), gr.update(visible=False), gr.update(
                            visible=False
                        ), gr.update(), history_state[
                            :
                        ], last_safe_images
                        return  # Stop all on error

                    # Cancel skip task if it's still pending
                    if skip_event:
                        skip_task.cancel()

                except Exception:
                    break

            if not (skip_event and skip_event.is_set()):
                previous_images.extend(current_completed)
            else:
                # If skipped, ensure we keep whatever was completed
                previous_images.extend(current_completed)
                # Update safe images state one last time for this batch to ensure sync
                last_safe_images = previous_images

        finished_naturally = True
    except asyncio.CancelledError:
        # Yield safe state on cancel to ensure preview is removed
        yield last_safe_images, "Interrupted", gr.update(visible=True, interactive=True), gr.update(
            visible=False
        ), gr.update(visible=False), gr.update(), history_state[:], last_safe_images
        raise
    finally:
        if finished_naturally:
            # Add seeds to status if available
            seed_info = ""
            # Seed info removed from status display per requirements
            # if "current_seeds" in locals() and current_seeds:
            #    seed_info = f" Seed: {list(current_seeds.values())[0]}"

            yield previous_images, last_status + seed_info + (
                seed_suffix if "seed_suffix" in locals() else ""
            ), gr.update(visible=True, interactive=True), gr.update(visible=False), gr.update(
                visible=False
            ), gr.update(), history_state[
                :
            ], previous_images


def create_ui(config, comfy_client):
    workflow_names = [w["name"] for w in config.workflows]
    object_info = comfy_client.get_object_info()

    # Event for skip signaling
    skip_event = asyncio.Event()

    async def on_generate(workflow_name, prompt_text, overrides, batch_count, history):
        # Clear skip event at start of run
        skip_event.clear()
        async for update in process_generation(
            workflow_name,
            prompt_text,
            overrides,
            batch_count,
            config,
            comfy_client,
            object_info,
            history,
            skip_event,
        ):
            yield update

    css = """
    #gallery {
        min-height: 70vh;
    }
    #gallery .grid-container {
        height: 70vh !important;
    }
    @media screen and (max-width: 600px) {
        #gallery .grid-container, #history-gallery .grid-container {
            grid-template-columns: repeat(1, minmax(0, 1fr)) !important;
        }
    }
    #gallery .gallery-item {
        max-width: 80vw !important;
    }
    #app_container {
        max-width: 1280px !important;
        margin: 0 auto !important;
    }
    #advanced-checkbox {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    #overrides-store {
        display: none !important;
    }
    .node-title {
        padding-left: 8px;
    }
    """
    shortcut_js = """
    document.addEventListener('keydown', (e) => {
        const target = e.target;
        if (target.tagName !== 'TEXTAREA' || !target.closest('#prompt-box')) return;

        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const genBtn = document.getElementById('gen-btn');
            const stopBtn = document.getElementById('stop-btn');
            if (stopBtn && stopBtn.offsetParent !== null) {
                stopBtn.click();
            } else if (genBtn) {
                genBtn.click();
            }
        }
    });
    """
    with gr.Blocks(title="SimplUI", css=css, js=shortcut_js) as demo:
        with gr.Column(elem_id="app_container"):
            overrides_store = gr.JSON(value={}, visible=True, elem_id="overrides-store")
            history_state = gr.State(value=[])
            safe_gallery_state = gr.State(value=[])

            def update_prompt_on_change(workflow_name):
                if not workflow_name:
                    return ""
                try:
                    workflow_info = next(w for w in config.workflows if w["name"] == workflow_name)
                    with open(workflow_info["path"], "r") as f:
                        workflow_json = json.load(f)
                    return get_prompt_default_value(workflow_json)
                except Exception as e:
                    print(f"Error updating prompt: {e}")
                    return ""

            with gr.Row():
                with gr.Column(scale=3) as main_col:
                    output_gallery = gr.Gallery(
                        label="Generated Images",
                        show_label=False,
                        elem_id="gallery",
                        object_fit="contain",
                        height="70vh",
                    )
                    status_text = gr.Markdown("Ready")

                    with gr.Row(equal_height=True):
                        with gr.Column(scale=4):
                            initial_prompt = ""
                            if workflow_names:
                                initial_prompt = update_prompt_on_change(workflow_names[0])

                            prompt_input = gr.Textbox(
                                label="Prompt",
                                lines=2,
                                value=initial_prompt,
                                placeholder="Enter your description here...",
                                elem_id="prompt-box",
                            )

                        with gr.Column(scale=1, min_width=100, elem_classes=["vertical-buttons"]):
                            generate_btn = gr.Button(
                                "Generate", variant="primary", elem_id="gen-btn"
                            )
                            stop_btn = gr.Button(
                                "Stop",
                                variant="stop",
                                visible=False,
                                elem_id="stop-btn",
                            )
                            skip_btn = gr.Button(
                                "Skip",
                                variant="secondary",
                                visible=False,
                                elem_id="skip-btn",
                            )

                    advanced_toggle = gr.Checkbox(
                        label="Advanced Controls",
                        value=False,
                        container=False,
                        elem_id="advanced-checkbox",
                    )

                with gr.Column(scale=1, visible=False, min_width=0) as sidebar_col:
                    workflow_dropdown = gr.Dropdown(
                        choices=workflow_names,
                        label="Select Workflow",
                        value=workflow_names[0] if workflow_names else None,
                        filterable=False,
                    )

                    batch_count_slider = gr.Slider(
                        label="Batch Count",
                        minimum=1,
                        maximum=20,
                        step=1,
                        value=2,
                        interactive=True,
                        elem_id="batch-count-slider",
                    )

                    batch_count_slider.release(
                        fn=None,
                        js="(val, store) => { const newStore = {...store}; newStore['_meta.batch_count'] = val; return newStore; }",
                        inputs=[batch_count_slider, overrides_store],
                        outputs=[overrides_store],
                    )

                    workflow_dropdown.change(
                        fn=update_prompt_on_change,
                        inputs=[workflow_dropdown],
                        outputs=[prompt_input],
                    )

                    with gr.Tabs():
                        with gr.Tab("Node Controls"):

                            @gr.render(
                                inputs=[
                                    workflow_dropdown,
                                    overrides_store,
                                    advanced_toggle,
                                ]
                            )
                            def render_dynamic_interface(workflow_name, overrides, show_advanced):
                                if not show_advanced or not workflow_name:
                                    return

                                if overrides is None:
                                    overrides = {}

                                workflow_info = next(
                                    (w for w in config.workflows if w["name"] == workflow_name),
                                    None,
                                )
                                if not workflow_info:
                                    return

                                try:
                                    with open(workflow_info["path"], "r") as f:
                                        workflow_json = json.load(f)
                                except Exception as e:
                                    gr.Markdown(f"Error loading workflow: {e}")
                                    return

                                extracted = extract_workflow_inputs(
                                    workflow_json, object_info, config.sliders
                                )

                                for node in extracted:
                                    with gr.Group():
                                        gr.Markdown(
                                            f"#### {node['title']}",
                                            elem_classes=["node-title"],
                                        )
                                        for inp in node["inputs"]:
                                            key = f"{node['node_id']}.{inp['name']}"

                                            if inp["type"] == "dimensions":
                                                # Identify keys
                                                w_key = f"{node['node_id']}.width"
                                                h_key = f"{node['node_id']}.height"
                                                mode_key = f"{key}.mode"
                                                ar_key = f"{key}.aspect_ratio"
                                                pc_key = f"{key}.pixel_count"

                                                # Get current state
                                                cur_w = overrides.get(w_key, inp["width_value"])
                                                cur_h = overrides.get(h_key, inp["height_value"])
                                                cur_mode = overrides.get(mode_key)

                                                # Intelligent Default
                                                if cur_mode is None:
                                                    match = find_matching_preset(cur_w, cur_h)
                                                    if match:
                                                        cur_mode = "simplified"
                                                        if ar_key not in overrides:
                                                            overrides[ar_key] = match[0]
                                                        if pc_key not in overrides:
                                                            overrides[pc_key] = match[1]
                                                    else:
                                                        cur_mode = "exact"

                                                is_simplified = cur_mode == "simplified"

                                                with gr.Group():
                                                    # Simplified View
                                                    with gr.Row(
                                                        visible=is_simplified
                                                    ) as simplified_row:
                                                        # Sorted from tallest (lowest W/H) to widest (highest W/H)
                                                        ar_options = [
                                                            "1:2",
                                                            "9:16",
                                                            "2:3",
                                                            "3:4",
                                                            "7:9",
                                                            "1:1",
                                                            "9:7",
                                                            "4:3",
                                                            "3:2",
                                                            "16:9",
                                                            "2:1",
                                                        ]
                                                        ar_val = overrides.get(ar_key, "1:1")
                                                        ar_comp = gr.Dropdown(
                                                            choices=ar_options,
                                                            label="Aspect Ratio",
                                                            value=ar_val,
                                                            scale=1,
                                                            min_width=80,
                                                            interactive=True,
                                                            filterable=False,
                                                        )

                                                        pc_options = [
                                                            "0.25M",
                                                            "0.5M",
                                                            "1M",
                                                            "1.5M",
                                                            "2M",
                                                        ]
                                                        pc_val = overrides.get(pc_key, "1M")
                                                        pc_comp = gr.Dropdown(
                                                            choices=pc_options,
                                                            label="Pixel Count",
                                                            value=pc_val,
                                                            scale=1,
                                                            min_width=80,
                                                            interactive=True,
                                                            filterable=False,
                                                        )

                                                    # Exact View
                                                    with gr.Row(
                                                        visible=not is_simplified
                                                    ) as exact_row:
                                                        w_comp = gr.Number(
                                                            label="Width",
                                                            value=cur_w,
                                                            interactive=True,
                                                        )
                                                        h_comp = gr.Number(
                                                            label="Height",
                                                            value=cur_h,
                                                            interactive=True,
                                                        )

                                                    # Toggle Button
                                                    toggle_btn = gr.Button(
                                                        (
                                                            "Show Exact Dimensions"
                                                            if is_simplified
                                                            else "Show Aspect Ratio"
                                                        ),
                                                        size="sm",
                                                    )

                                                # Logic for Simplified (Dropdowns)
                                                js_calc = f"""
                                                (val, store) => {{
                                                    const newStore = {{...store}};
                                                    if (!newStore['{ar_key}']) newStore['{ar_key}'] = '1:1';
                                                    if (!newStore['{pc_key}']) newStore['{pc_key}'] = '1M';

                                                    const ar = '{ar_key}'.endsWith('.aspect_ratio') && val.includes(':') ? val : newStore['{ar_key}'];
                                                    const pc_str = '{pc_key}'.endsWith('.pixel_count') && val.includes('M') ? val : newStore['{pc_key}'];

                                                    if (val.includes(':')) newStore['{ar_key}'] = val;
                                                    else newStore['{pc_key}'] = val;

                                                    const pc = parseFloat(pc_str) * 1024 * 1024;
                                                    const parts = ar.split(':');
                                                    const ratio = parseFloat(parts[0]) / parseFloat(parts[1]);

                                                    const h = Math.sqrt(pc / ratio);
                                                    const w = h * ratio;
                                                    const round64 = (v) => Math.max(64, Math.round(v / 64) * 64);

                                                    newStore['{w_key}'] = round64(w);
                                                    newStore['{h_key}'] = round64(h);
                                                    return newStore;
                                                }}
                                                """
                                                ar_comp.change(
                                                    fn=None,
                                                    js=js_calc,
                                                    inputs=[ar_comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                pc_comp.change(
                                                    fn=None,
                                                    js=js_calc,
                                                    inputs=[pc_comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )

                                                # Logic for Exact (Numbers)
                                                w_comp.blur(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{w_key}'] = val; return newStore; }}",
                                                    inputs=[w_comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                w_comp.submit(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{w_key}'] = val; return newStore; }}",
                                                    inputs=[w_comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                h_comp.blur(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{h_key}'] = val; return newStore; }}",
                                                    inputs=[h_comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                h_comp.submit(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{h_key}'] = val; return newStore; }}",
                                                    inputs=[h_comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )

                                                # Logic for Toggle
                                                def on_toggle(store):
                                                    if store is None:
                                                        return {}
                                                    new_store = copy.deepcopy(store)
                                                    mode = new_store.get(mode_key, cur_mode)

                                                    if mode == "simplified":
                                                        new_store[mode_key] = "exact"
                                                    else:
                                                        new_store[mode_key] = "simplified"
                                                        w = new_store.get(w_key, cur_w)
                                                        h = new_store.get(h_key, cur_h)
                                                        match = find_nearest_preset(w, h)
                                                        ar, pc = match
                                                        new_store[ar_key] = ar
                                                        new_store[pc_key] = pc
                                                        new_w, new_h = calculate_dimensions(
                                                            ar,
                                                            float(pc.replace("M", "")),
                                                        )
                                                        new_store[w_key] = new_w
                                                        new_store[h_key] = new_h
                                                    return new_store

                                                toggle_btn.click(
                                                    on_toggle,
                                                    inputs=[overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                continue

                                            # Use value from overrides if available, else default
                                            current_val = (
                                                overrides.get(key, inp["value"])
                                                if overrides
                                                else inp["value"]
                                            )

                                            if inp["type"] == "enum":
                                                comp = gr.Dropdown(
                                                    choices=inp["options"],
                                                    label=inp["name"],
                                                    value=current_val,
                                                    interactive=True,
                                                    filterable=False,
                                                )
                                                comp.change(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                            elif inp["type"] == "seed":
                                                with gr.Row():
                                                    random_key = f"{key}.randomize"
                                                    random_default = inp.get("randomize", False)
                                                    random_val = (
                                                        overrides.get(random_key, random_default)
                                                        if overrides
                                                        else random_default
                                                    )

                                                    comp = gr.Textbox(
                                                        label=inp["name"],
                                                        value=str(current_val),
                                                        scale=1,
                                                        interactive=True,
                                                        visible=not random_val,
                                                    )

                                                    random_box = gr.Checkbox(
                                                        label="Randomize",
                                                        value=random_val,
                                                        scale=1,
                                                        interactive=True,
                                                    )

                                                comp.blur(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                comp.submit(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )

                                                random_box.change(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{random_key}'] = val; return newStore; }}",
                                                    inputs=[
                                                        random_box,
                                                        overrides_store,
                                                    ],
                                                    outputs=[overrides_store],
                                                )
                                            elif inp["type"] == "slider":
                                                comp = gr.Slider(
                                                    label=inp["name"],
                                                    value=current_val,
                                                    minimum=inp["min"],
                                                    maximum=inp["max"],
                                                    step=inp.get("step", 1),
                                                    interactive=True,
                                                )
                                                comp.release(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                            elif inp["type"] == "number":
                                                comp = gr.Number(
                                                    label=inp["name"],
                                                    value=current_val,
                                                    scale=1,
                                                    interactive=True,
                                                )
                                                comp.blur(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                comp.submit(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                            elif inp["type"] == "bool":
                                                comp = gr.Checkbox(
                                                    label=inp["name"],
                                                    value=current_val,
                                                    interactive=True,
                                                )
                                                comp.change(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                            else:
                                                comp = gr.Textbox(
                                                    label=inp["name"],
                                                    value=str(current_val),
                                                    interactive=True,
                                                )
                                                comp.blur(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )
                                                comp.submit(
                                                    fn=None,
                                                    js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}",
                                                    inputs=[comp, overrides_store],
                                                    outputs=[overrides_store],
                                                )

                        with gr.Tab("History"):
                            history_gallery = gr.Gallery(
                                label="Session History",
                                show_label=False,
                                object_fit="contain",
                                height="70vh",
                                elem_id="history-gallery",
                                interactive=False,
                            )

                advanced_toggle.change(
                    fn=lambda x: gr.update(visible=x),
                    inputs=[advanced_toggle],
                    outputs=[sidebar_col],
                )

                gen_event = generate_btn.click(
                    fn=on_generate,
                    inputs=[
                        workflow_dropdown,
                        prompt_input,
                        overrides_store,
                        batch_count_slider,
                        history_state,
                    ],
                    outputs=[
                        output_gallery,
                        status_text,
                        generate_btn,
                        stop_btn,
                        skip_btn,
                        overrides_store,
                        history_gallery,
                        safe_gallery_state,
                    ],
                )

                gen_event.cancels = [gen_event]

                def stop_generation(safe_images):
                    try:
                        comfy_client.interrupt()
                    except Exception:
                        pass
                    return (
                        safe_images,
                        gr.update(value="Interrupted"),
                        gr.update(visible=True, interactive=True),
                        gr.update(visible=False),
                        gr.update(visible=False),
                    )

                stop_btn.click(
                    fn=stop_generation,
                    inputs=[safe_gallery_state],
                    outputs=[output_gallery, status_text, generate_btn, stop_btn, skip_btn],
                    cancels=[gen_event],
                )

                def on_skip():
                    skip_event.set()
                    comfy_client.interrupt()

                skip_btn.click(
                    fn=on_skip,
                    inputs=[],
                    outputs=[],
                )

    demo.css = css
    demo.js = shortcut_js
    return demo
