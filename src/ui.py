import gradio as gr
import json
import asyncio
from PIL import Image
import io
import copy

def extract_workflow_inputs(workflow, object_info=None):
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
            
            # Check for Enum in object_info
            if node_def:
                # Inputs can be in 'required' or 'optional'
                input_def = node_def.get("input", {}).get("required", {}).get(name)
                if not input_def:
                    input_def = node_def.get("input", {}).get("optional", {}).get(name)
                
                # If input definition is a list, it's an enum
                if isinstance(input_def, list) and len(input_def) > 0 and isinstance(input_def[0], list):
                    input_type = "enum"
                    options = input_def[0]
            
            if input_type != "enum":
                if isinstance(value, bool):
                    input_type = "bool"
                elif isinstance(value, (int, float)):
                    input_type = "number"
            
            input_data = {
                "name": name,
                "type": input_type,
                "value": value
            }
            if options:
                input_data["options"] = options
            
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
        if "." in key:
            node_id, input_name = key.split(".", 1)
            if node_id in merged and "inputs" in merged[node_id]:
                merged[node_id]["inputs"][input_name] = value
    return merged

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
        last_image = None
        last_status = "Starting..."
        async for event in comfy_client.generate_image(workflow_json):
            if event["type"] == "progress":
                last_status = f"Progress: {event['value']}/{event['max']}"
                yield last_image, last_status
            elif event["type"] == "preview":
                try:
                    last_image = Image.open(io.BytesIO(event["data"]))
                    yield last_image, last_status
                except Exception as e:
                    pass
            elif event["type"] == "image":
                image_bytes = event["data"]
                try:
                    last_image = Image.open(io.BytesIO(image_bytes))
                    yield last_image, "Generation complete"
                except Exception as e:
                    yield last_image, f"Error processing image: {e}"
    except Exception as e:
        yield None, f"Error during generation: {e}"

def create_ui(config, comfy_client):
    workflow_names = [w["name"] for w in config.workflows]
    
    async def on_generate(workflow_name, prompt_text, overrides):
        # Initial status and show stop button
        yield None, "Initializing...", gr.update(visible=True)
        
        # Auto-stop previous runs
        try:
            comfy_client.interrupt()
            comfy_client.clear_queue()
            # Small delay to ensure server processes interrupt before new submission
            await asyncio.sleep(0.1)
        except Exception:
            pass

        last_image = None
        last_status = "Processing..."
        async for update in handle_generation(workflow_name, prompt_text, config, comfy_client, overrides):
            last_image, last_status = update
            yield last_image, last_status, gr.update(visible=True)
        
        # Hide stop button when done
        yield last_image, last_status, gr.update(visible=False)

    with gr.Blocks(title="Simpl2 ComfyUI Wrapper") as demo:
        gr.Markdown("# Simpl2 ComfyUI Wrapper")
        
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
            with gr.Column(scale=1):
                workflow_dropdown = gr.Dropdown(
                    choices=workflow_names, 
                    label="Select Workflow",
                    value=workflow_names[0] if workflow_names else None
                )
                
                initial_prompt = ""
                if workflow_names:
                    initial_prompt = update_prompt_on_change(workflow_names[0])
                
                prompt_input = gr.Textbox(
                    label="Prompt", 
                    lines=3, 
                    value=initial_prompt,
                    placeholder="Enter your description here..."
                )
                
                # Bind prompt update
                workflow_dropdown.change(
                    fn=update_prompt_on_change,
                    inputs=[workflow_dropdown],
                    outputs=[prompt_input]
                )
                
                with gr.Row():
                    generate_btn = gr.Button("Generate", variant="primary")
                    stop_btn = gr.Button("Stop", variant="stop", visible=False)
                
                with gr.Accordion("Advanced Controls", open=False):
                    @gr.render(inputs=[workflow_dropdown])
                    def render_dynamic_interface(workflow_name):
                        if not workflow_name:
                            gr.Markdown("Please select a workflow to continue.")
                            return
                        
                        workflow_info = next(w for w in config.workflows if w["name"] == workflow_name)
                        try:
                            with open(workflow_info["path"], "r") as f:
                                workflow_json = json.load(f)
                        except Exception as e:
                            gr.Markdown(f"Error loading workflow: {e}")
                            return

                        extracted = extract_workflow_inputs(workflow_json)
                        
                        for node in extracted:
                            with gr.Group():
                                gr.Markdown(f"#### {node['title']} ({node['node_id']})")
                                for inp in node["inputs"]:
                                    key = f"{node['node_id']}.{inp['name']}"
                                    
                                    if inp["type"] == "number":
                                        comp = gr.Number(label=inp["name"], value=inp["value"], scale=1, interactive=True)
                                    elif inp["type"] == "bool":
                                        comp = gr.Checkbox(label=inp["name"], value=inp["value"], interactive=True)
                                    else:
                                        comp = gr.Textbox(label=inp["name"], value=str(inp["value"]), interactive=True)
                                    
                                    # JavaScript to update the store client-side
                                    js_update = f"(val, store) => {{ store['{key}'] = val; return store; }}"
                                    comp.change(fn=None, js=js_update, inputs=[comp, overrides_store], outputs=[overrides_store])

            with gr.Column(scale=2):
                output_image = gr.Image(label="Generated Image", type="pil")
                status_text = gr.Markdown("Ready")

        gen_event = generate_btn.click(
            fn=on_generate,
            inputs=[workflow_dropdown, prompt_input, overrides_store],
            outputs=[output_image, status_text, stop_btn]
        )
        
        # Clicking Generate again cancels the previous run
        gen_event.cancels = [gen_event]
        
        def stop_generation():
            comfy_client.interrupt()
            return gr.update(value="Interrupted"), gr.update(visible=False)

        stop_btn.click(
            fn=stop_generation,
            inputs=[],
            outputs=[status_text, stop_btn],
            cancels=[gen_event] # Stop button cancels the generation task
        )
        
    return demo