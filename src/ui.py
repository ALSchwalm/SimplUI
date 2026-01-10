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
            elif isinstance(value, int):
                input_type = "int"
            elif isinstance(value, float):
                input_type = "float"
            
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
            print(f"DEBUG: Received event: {event['type']}")
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
    
    async def on_generate(workflow_name, prompt_text):
        async for update in handle_generation(workflow_name, prompt_text, config, comfy_client):
            yield update

    with gr.Blocks(title="Simpl2 ComfyUI Wrapper") as demo:
        gr.Markdown("# Simpl2 ComfyUI Wrapper")
        
        with gr.Row():
            with gr.Column(scale=1):
                workflow_dropdown = gr.Dropdown(
                    choices=workflow_names, 
                    label="Select Workflow",
                    value=workflow_names[0] if workflow_names else None
                )
                prompt_input = gr.Textbox(
                    label="Prompt", 
                    lines=3, 
                    placeholder="Enter your description here..."
                )
                generate_btn = gr.Button("Generate", variant="primary")
                
                with gr.Accordion("Advanced Controls", open=False):
                    advanced_params_area = gr.Column()
                    
            with gr.Column(scale=2):
                output_image = gr.Image(label="Generated Image", type="pil")
                status_text = gr.Markdown("Ready")

        generate_btn.click(
            fn=on_generate,
            inputs=[workflow_dropdown, prompt_input],
            outputs=[output_image, status_text]
        )
        
    return demo