import gradio as gr
import json
import asyncio
from PIL import Image
import io

async def handle_generation(workflow_name, config, comfy_client):
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

    # 3. Generate Image (Connect -> Submit -> Listen)
    try:
        last_image = None
        async for event in comfy_client.generate_image(workflow_json):
            print(f"DEBUG: Received event: {event['type']}")
            if event["type"] == "progress":
                yield last_image, f"Progress: {event['value']}/{event['max']}"
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
    
    async def on_generate(workflow_name):
        async for update in handle_generation(workflow_name, config, comfy_client):
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
                generate_btn = gr.Button("Generate", variant="primary")
                
            with gr.Column(scale=2):
                output_image = gr.Image(label="Generated Image", type="pil")
                status_text = gr.Markdown("Ready")

        generate_btn.click(
            fn=on_generate,
            inputs=[workflow_dropdown],
            outputs=[output_image, status_text]
        )
        
    return demo
