import gradio as gr
import json
import asyncio
from PIL import Image
import io
import copy
import random
try:
    from .seed_utils import generate_batch_seeds
except ImportError:
    from seed_utils import generate_batch_seeds

def extract_workflow_inputs(workflow, object_info=None, slider_config=None):
    extracted = []
    for node_id, node_data in workflow.items():
        title = node_data.get("_meta", {}).get("title", f"Node {node_id}")
        class_type = node_data.get("class_type", "")
        inputs = []
        is_prompt_node = title.lower() == "prompt"

        # Get node definition from object_info
        node_def = None
        if object_info and class_type in object_info:
            node_def = object_info[class_type]

        for name, value in node_data.get("inputs", {}).items():
            if isinstance(value, list):
                continue  # Skip links

            # Filter out the primary prompt input from advanced controls
            if is_prompt_node and name in ["text", "string"]:
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
                             slider_params.setdefault("step", meta_params.get("step")) # step might be missing

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

            input_data = {
                "name": name,
                "type": input_type,
                "value": value
            }
            if input_type == "seed":
                input_data["randomize"] = (value == 0 or value == "0")

            if options:
                input_data["options"] = options

            if input_type == "slider":
                input_data.update(slider_params)

            inputs.append(input_data)

        if inputs:
            extracted.append({
                "node_id": node_id,
                "title": title,
                "inputs": inputs
            })
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
            base_key = key[:-10] # remove .randomize
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
        yield None, f"Error loading workflow: {e}"
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
                # Yield completed images + latest preview if available
                current_images = list(completed_images)
                if latest_preview:
                    current_images.append(latest_preview)
                yield current_images, last_status
            elif event["type"] == "preview":
                try:
                    preview_image = Image.open(io.BytesIO(event["data"]))
                    latest_preview = preview_image
                    # Show preview as the next potential image
                    yield completed_images + [preview_image], last_status
                except Exception as e:
                    pass
            elif event["type"] == "image":
                image_bytes = event["data"]
                try:
                    final_image = Image.open(io.BytesIO(image_bytes))
                    completed_images.append(final_image)
                    latest_preview = None # Clear preview as it is replaced by final image
                    yield list(completed_images), "Generation complete"
                except Exception as e:
                    yield list(completed_images), f"Error processing image: {e}"
    except Exception as e:
        yield [], f"Error during generation: {e}"

async def process_generation(workflow_name, prompt_text, overrides, batch_count, config, comfy_client, object_info):
    # Initial status: Ensure Generate is visible/interactive, Show Stop
    yield None, "Initializing...", gr.update(visible=True, interactive=True), gr.update(visible=True), overrides

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
    # If overrides is None/Empty, initialize it
    if overrides is None:
        overrides = {}
        
    extracted = extract_workflow_inputs(workflow_json, object_info, config.sliders)
    for node in extracted:
        for inp in node["inputs"]:
            if inp["type"] == "seed":
                key = f"{node['node_id']}.{inp['name']}"
                random_key = f"{key}.randomize"
                
                # Determine randomization state
                is_random = False
                if random_key in overrides:
                    is_random = overrides[random_key]
                else:
                    # If not in overrides, use default from extraction (True if value is 0)
                    is_random = inp.get("randomize", False)
                
                # If random, ensure we generate a base seed if not already randomized by apply_random_seeds later
                # Wait, apply_random_seeds only processes keys in overrides.
                # So we must add it to overrides here if it's not present.
                if is_random and key not in overrides:
                     # Generate a new random base seed
                     new_seed = random.randint(0, 18446744073709551615)
                     overrides[key] = str(new_seed)
                     overrides[random_key] = True # Ensure randomize is set in overrides too

    # Apply random seeds (handles overrides that are already present)
    if overrides:
        overrides = apply_random_seeds(overrides)
        # Update store with new seeds
        yield None, "Randomizing seeds...", gr.update(visible=True, interactive=True), gr.update(visible=True), overrides

    # Calculate Batch Seeds
    # extracted is already calculated above
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
    last_image = None
    
    try:
        for i in range(batch_count):
             iter_overrides = overrides.copy() if overrides else {}
             
             current_seeds = {}
             for key, batch in seed_batches.items():
                 seed_val = batch[i]
                 iter_overrides[key] = str(seed_val) # Store as string for overrides compatibility
                 current_seeds[key] = seed_val
                 
             seed_info_str = ", ".join([f"{k.split('.')[1].capitalize()}: {v}" for k,v in current_seeds.items()])
             seed_suffix = f" (Batch {i+1}/{batch_count} - {seed_info_str})"
             
             run_images = []
             async for update in handle_generation(workflow_name, prompt_text, config, comfy_client, iter_overrides):
                 run_images, status = update
                 last_status = status
                 last_image = previous_images + run_images
                 yield last_image, last_status + seed_suffix, gr.update(visible=True, interactive=True), gr.update(visible=True), overrides
                 
             # Only extend with finished images (handle_generation yields finished list last)
             previous_images.extend(run_images)
             
        finished_naturally = True
    finally:
         if finished_naturally:
              yield last_image, last_status + seed_suffix if 'seed_suffix' in locals() else "", gr.update(visible=True, interactive=True), gr.update(visible=False), overrides

def create_ui(config, comfy_client):
    workflow_names = [w["name"] for w in config.workflows]

    # Fetch node definitions from ComfyUI
    object_info = comfy_client.get_object_info()

    async def on_generate(workflow_name, prompt_text, overrides, batch_count=1):
        async for update in process_generation(workflow_name, prompt_text, overrides, batch_count, config, comfy_client, object_info):
            yield update

    css = """
    #gallery {
        min-height: 70vh;
    }
    #gallery .grid-container {
        height: 70vh !important;
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
    """
    with gr.Blocks(title="Simpl2 ComfyUI Wrapper", css=css) as demo:
        with gr.Column(elem_id="app_container"):
            # Client-side store for overrides.
            # This JSON component holds the state in the browser.
            overrides_store = gr.JSON(value={}, visible=False)

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
                        show_label=True,
                        elem_id="gallery",
                        object_fit="contain",
                        height="70vh"
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
                                elem_id="prompt-box"
                            )

                        with gr.Column(scale=1, min_width=100, elem_classes=["vertical-buttons"]):
                            generate_btn = gr.Button("Generate", variant="primary", elem_id="gen-btn")
                            stop_btn = gr.Button("Stop", variant="stop", visible=False, elem_id="stop-btn")

                    # Advanced Controls Toggle
                    advanced_toggle = gr.Checkbox(label="Advanced Controls", value=False,
                                                  container=False, elem_id="advanced-checkbox")

                with gr.Column(scale=1, visible=False, min_width=0) as sidebar_col:
                    workflow_dropdown = gr.Dropdown(
                        choices=workflow_names,
                        label="Select Workflow",
                        value=workflow_names[0] if workflow_names else None,
                        filterable=False
                    )

                    # Batch Count Slider
                    batch_count_slider = gr.Slider(
                        label="Batch Count",
                        minimum=1,
                        maximum=20,
                        step=1,
                        value=2,
                        interactive=True,
                        elem_id="batch-count-slider"
                    )

                    batch_count_slider.change(
                        fn=None,
                        js="(val, store) => { const newStore = {...store}; newStore['_meta.batch_count'] = val; return newStore; }",
                        inputs=[batch_count_slider, overrides_store],
                        outputs=[overrides_store]
                    )

                    # Bind prompt update
                    workflow_dropdown.change(
                        fn=update_prompt_on_change,
                        inputs=[workflow_dropdown],
                        outputs=[prompt_input]
                    )

                    with gr.Tabs():
                        with gr.Tab("Node Controls"):
                            @gr.render(inputs=[workflow_dropdown, overrides_store, advanced_toggle])
                            def render_dynamic_interface(workflow_name, overrides, show_advanced):
                                if not show_advanced or not workflow_name:
                                    return

                                workflow_info = next(w for w in config.workflows if w["name"] == workflow_name)
                                try:
                                    with open(workflow_info["path"], "r") as f:
                                        workflow_json = json.load(f)
                                except Exception as e:
                                    gr.Markdown(f"Error loading workflow: {e}")
                                    return

                                extracted = extract_workflow_inputs(workflow_json, object_info, config.sliders)

                                for node in extracted:
                                    with gr.Group():
                                        gr.Markdown(f"#### {node['title']} ({node['node_id']})")
                                        for inp in node["inputs"]:
                                            key = f"{node['node_id']}.{inp['name']}"

                                            # Use value from overrides if available, else default
                                            current_val = overrides.get(key, inp["value"]) if overrides else inp["value"]

                                            if inp["type"] == "enum":
                                                comp = gr.Dropdown(
                                                    choices=inp["options"],
                                                    label=inp["name"],
                                                    value=current_val,
                                                    interactive=True,
                                                    filterable=False
                                                )
                                                comp.change(fn=None, js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}", inputs=[comp, overrides_store], outputs=[overrides_store])
                                            elif inp["type"] == "seed":
                                                with gr.Row():
                                                    # Use Textbox to preserve 64-bit integer precision
                                                    comp = gr.Textbox(label=inp["name"], value=str(current_val), scale=1, interactive=True)
                                                    # Check randomization state from overrides
                                                    random_key = f"{key}.randomize"
                                                    random_default = inp.get("randomize", False)
                                                    random_val = overrides.get(random_key, random_default) if overrides else random_default

                                                    random_box = gr.Checkbox(label="Randomize", value=random_val, scale=1, interactive=True)

                                                # Bind number input (as text)
                                                comp.change(fn=None, js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}", inputs=[comp, overrides_store], outputs=[overrides_store])

                                                # Bind randomize checkbox
                                                random_box.change(fn=None, js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{random_key}'] = val; return newStore; }}", inputs=[random_box, overrides_store], outputs=[overrides_store])
                                            elif inp["type"] == "slider":
                                                comp = gr.Slider(
                                                    label=inp["name"],
                                                    value=current_val,
                                                    minimum=inp["min"],
                                                    maximum=inp["max"],
                                                    step=inp.get("step", 1),
                                                    interactive=True
                                                )
                                                comp.change(fn=None, js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}", inputs=[comp, overrides_store], outputs=[overrides_store])
                                            elif inp["type"] == "number":
                                                comp = gr.Number(label=inp["name"], value=current_val, scale=1, interactive=True)
                                                comp.change(fn=None, js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}", inputs=[comp, overrides_store], outputs=[overrides_store])
                                            elif inp["type"] == "bool":
                                                comp = gr.Checkbox(label=inp["name"], value=current_val, interactive=True)
                                                comp.change(fn=None, js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}", inputs=[comp, overrides_store], outputs=[overrides_store])
                                            else:
                                                comp = gr.Textbox(label=inp["name"], value=str(current_val), interactive=True)
                                                comp.change(fn=None, js=f"(val, store) => {{ const newStore = {{...store}}; newStore['{key}'] = val; return newStore; }}", inputs=[comp, overrides_store], outputs=[overrides_store])

                # Bind sidebar visibility
                advanced_toggle.change(
                    fn=lambda x: gr.update(visible=x),
                    inputs=[advanced_toggle],
                    outputs=[sidebar_col]
                )

                gen_event = generate_btn.click(
                    fn=on_generate,
                    inputs=[workflow_dropdown, prompt_input, overrides_store, batch_count_slider],
                    outputs=[output_gallery, status_text, generate_btn, stop_btn, overrides_store]
                )

                # Clicking Generate again cancels the previous run
                gen_event.cancels = [gen_event]

                def stop_generation():
                    comfy_client.interrupt()
                    # Return status, show Generate, hide Stop
                    return gr.update(value="Interrupted"), gr.update(visible=True, interactive=True), gr.update(visible=False)

                stop_btn.click(
                    fn=stop_generation,
                    inputs=[],
                    outputs=[status_text, generate_btn, stop_btn],
                    cancels=[gen_event] # Stop button cancels the generation task
                )

    demo.css = css
    return demo