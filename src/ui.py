import gradio as gr
import json
import asyncio
from PIL import Image
import io
import copy

def extract_workflow_inputs(workflow):
    extracted = []
    for node_id, node_data in workflow.items():
        title = node_data.get("_meta", {}).get("title", f"Node {node_id}")
        inputs = []
        for name, value in node_data.get("inputs", {}).items():
            if isinstance(value, list):
                continue  # Skip links
            
            input_type = "str"
            if isinstance(value, bool):
                input_type = "bool"
            elif isinstance(value, (int, float)):
                input_type = "number"
            
            inputs.append({
                "name": name,
                "type": input_type,
                "value": value
            })
        
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

async def handle_generation(workflow_name, prompt_text, config, comfy_client, overrides=None):
    print(f"DEBUG: Starting generation for {workflow_name}")
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
        print(f"DEBUG: Applying overrides: {overrides}")
        workflow_json = merge_workflow_overrides(workflow_json, overrides)

    # 3. Inject Prompt if provided
    if prompt_text:
        print(f"DEBUG: Injecting prompt: {prompt_text}")
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
                    print(f"DEBUG: Error decoding preview: {e}")
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
    
    with gr.Blocks(title="Simpl2 ComfyUI Wrapper") as demo:
        gr.Markdown("# Simpl2 ComfyUI Wrapper")
        
        # We assume output components are static
        with gr.Row():
            with gr.Column(scale=1):
                workflow_dropdown = gr.Dropdown(
                    choices=workflow_names, 
                    label="Select Workflow",
                    value=workflow_names[0] if workflow_names else None
                )
                
                # Container for dynamic inputs and generate button
                dynamic_area = gr.Column()
                
            with gr.Column(scale=2):
                output_image = gr.Image(label="Generated Image", type="pil")
                status_text = gr.Markdown("Ready")

        @gr.render(inputs=[workflow_dropdown], triggers=[workflow_dropdown.change])
        def render_dynamic_interface(workflow_name):
            if not workflow_name:
                return
            
            workflow_info = next(w for w in config.workflows if w["name"] == workflow_name)
            try:
                with open(workflow_info["path"], "r") as f:
                    workflow_json = json.load(f)
            except Exception as e:
                gr.Markdown(f"Error loading workflow: {e}")
                return

            extracted = extract_workflow_inputs(workflow_json)
            
            # Place prompt input here so it's part of the form
            with gr.Column(): # Ensure vertical layout
                prompt_input = gr.Textbox(
                    label="Prompt", 
                    lines=3, 
                    placeholder="Enter your description here..."
                )
                
                dynamic_components = []
                dynamic_keys = []
                
                with gr.Accordion("Advanced Controls", open=False):
                    for node in extracted:
                        with gr.Group():
                            gr.Markdown(f"#### {node['title']} ({node['node_id']})")
                            for inp in node["inputs"]:
                                key = f"{node['node_id']}.{inp['name']}"
                                dynamic_keys.append(key)
                                
                                if inp["type"] == "number":
                                    comp = gr.Number(label=inp["name"], value=inp["value"], scale=1, interactive=True)
                                elif inp["type"] == "bool":
                                    comp = gr.Checkbox(label=inp["name"], value=inp["value"], interactive=True)
                                else:
                                    comp = gr.Textbox(label=inp["name"], value=str(inp["value"]), interactive=True)
                                dynamic_components.append(comp)

                generate_btn = gr.Button("Generate", variant="primary")

                async def dynamic_on_generate(prompt, *args):
                    overrides = {}
                    for i, val in enumerate(args):
                        key = dynamic_keys[i]
                        overrides[key] = val
                    
                    async for update in handle_generation(workflow_name, prompt, config, comfy_client, overrides):
                        yield update

                generate_btn.click(
                    fn=dynamic_on_generate,
                    inputs=[prompt_input, *dynamic_components],
                    outputs=[output_image, status_text]
                )

    return demo
