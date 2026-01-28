import gradio as gr
from src.config_manager import ConfigManager
from src.comfy_client import ComfyClient
from src.ui import create_ui
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Simpl2 ComfyUI Wrapper")
    parser.add_argument("--comfy-addr", type=str, help="ComfyUI server address (e.g. 127.0.0.1:8188)")
    parser.add_argument("--listen-addr", type=str, help="Local listen address (e.g. 0.0.0.0:7860)")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config.json")
    return parser.parse_args()


def split_addr(addr_str, default_host, default_port):
    if not addr_str:
        return default_host, default_port
    
    if ":" in addr_str:
        host, port = addr_str.rsplit(":", 1)
        if not host:
            host = default_host
        try:
            return host, int(port)
        except ValueError:
            return host, default_port
    else:
        return addr_str, default_port


def main():
    args = parse_args()
    
    if not os.path.exists(args.config):
        print(f"Error: {args.config} not found.")
        return

    try:
        config = ConfigManager(args.config)
        
        # Precedence: CLI > Config
        comfy_url = config.comfy_url
        if args.comfy_addr:
            # Assume http if not specified
            addr = args.comfy_addr
            if not addr.startswith("http"):
                addr = f"http://{addr}"
            comfy_url = addr

        # Verify workflows exist
        for wf in config.workflows:
            if not os.path.exists(wf["path"]):
                print(f"Warning: Workflow file not found at {wf['path']}")

        client = ComfyClient(comfy_url)

        if not client.check_connection():
            print(
                f"Warning: Could not connect to ComfyUI at {comfy_url}. Check if the server is running."
            )

        demo = create_ui(config, client)

        # Listen address splitting
        listen_host, listen_port = split_addr(args.listen_addr, "0.0.0.0", 7860)

        print(f"Connecting to ComfyUI at: {comfy_url}")
        print(f"Launching Gradio UI at http://{listen_host}:{listen_port}")

        # Launching with debug=True can help see errors in the console
        demo.launch(server_name=listen_host, server_port=listen_port, debug=True, css=demo.css)

    except Exception as e:
        print(f"Failed to launch UI: {e}")
        exit(1)


if __name__ == "__main__":
    main()
