import gradio as gr
from src.config_manager import ConfigManager
from src.comfy_client import ComfyClient
from src.ui import create_ui
import os

def main():
    if not os.path.exists("config.json"):
        print("Error: config.json not found.")
        return

    try:
        config = ConfigManager("config.json")
        
        # Verify workflows exist
        for wf in config.workflows:
            if not os.path.exists(wf["path"]):
                print(f"Warning: Workflow file not found at {wf['path']}")

        client = ComfyClient(config.comfy_url)
        
        if not client.check_connection():
            print(f"Warning: Could not connect to ComfyUI at {config.comfy_url}. Check if the server is running.")

        demo = create_ui(config, client)
        
        print(f"Connecting to ComfyUI at: {config.comfy_url}")
        print("Launching Gradio UI at http://localhost:7860")
        
        # Launching with debug=True can help see errors in the console
        demo.launch(server_name="0.0.0.0", server_port=7860, debug=True, css=demo.css)
        
    except Exception as e:
        print(f"Failed to launch UI: {e}")
        exit(1)

if __name__ == "__main__":
    main()
