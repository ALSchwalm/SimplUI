import gradio as gr

def create_ui(config, comfy_client):
    workflow_names = [w["name"] for w in config.workflows]
    
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
                output_image = gr.Image(label="Generated Image")
                status_text = gr.Markdown("Ready")

        # Callbacks will be implemented in the next task
        
    return demo
