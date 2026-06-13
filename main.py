import os
import argparse
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from src.config_manager import ConfigManager
from src.comfy_client import ComfyClient

app = FastAPI(title="SimplUI Backend")


def get_config():
    return getattr(app.state, "config", None)


@app.get("/api/config")
def api_config():
    config = get_config()
    if not config:
        return {
            "comfy_url": getattr(app.state, "comfy_url", "http://localhost:8188"),
            "workflows": [],
            "sliders": {},
        }
    return {
        "comfy_url": getattr(app.state, "comfy_url", config.comfy_url),
        "workflows": config.workflows,
        "sliders": config.sliders,
    }


@app.get("/api/workflows/{name}")
def get_workflow(name: str):
    config = get_config()
    if not config:
        raise HTTPException(status_code=500, detail="Config not loaded")

    workflow_info = next((w for w in config.workflows if w["name"] == name), None)
    if not workflow_info:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        with open(workflow_info["path"], "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading workflow: {e}")


from fastapi import Request
from fastapi.responses import Response
import requests


@app.api_route("/comfy-proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def comfy_proxy(path: str, request: Request):
    config = get_config()
    comfy_url = getattr(
        app.state, "comfy_url", config.comfy_url if config else "http://localhost:8188"
    )
    target_url = f"{comfy_url}/{path}"

    body = await request.body()

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length"]
            },
            params=dict(request.query_params),
            data=body,
            timeout=10.0,
        )

        exclude_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        headers = {k: v for k, v in resp.headers.items() if k.lower() not in exclude_headers}

        return Response(content=resp.content, status_code=resp.status_code, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Proxy error: {e}")


# Ensure static directory exists
os.makedirs("static", exist_ok=True)
if not os.path.exists("static/index.html"):
    with open("static/index.html", "w") as f:
        f.write("<!DOCTYPE html><html><body>SimplUI Backend</body></html>")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_index():
    return FileResponse("static/index.html")


def parse_args():
    parser = argparse.ArgumentParser(description="SimplUI")
    parser.add_argument(
        "--comfy-addr", type=str, help="ComfyUI server address (e.g. 127.0.0.1:8188)"
    )
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

        # Initialize app state
        app.state.config = config
        app.state.comfy_url = comfy_url

        # Listen address splitting
        listen_host, listen_port = split_addr(args.listen_addr, "0.0.0.0", 7860)

        print(f"Connecting to ComfyUI at: {comfy_url}")
        print(f"Launching FastAPI Server at http://{listen_host}:{listen_port}")

        uvicorn.run(app, host=listen_host, port=listen_port)

    except Exception as e:
        print(f"Failed to launch UI: {e}")
        exit(1)


if __name__ == "__main__":
    main()
