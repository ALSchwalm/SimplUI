import os
import argparse
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from src.config_manager import ConfigManager
from src.comfy_client import ComfyClient

app = FastAPI(title="SimplUI Backend")


@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


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


from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import websockets


@app.websocket("/comfy-ws")
async def comfy_ws(websocket: WebSocket):
    await websocket.accept()

    config = get_config()
    comfy_url = getattr(
        app.state, "comfy_url", config.comfy_url if config else "http://localhost:8188"
    )
    ws_target_base = comfy_url.replace("http://", "ws://").replace("https://", "wss://")

    client_id = websocket.query_params.get("clientId")
    ws_target_url = f"{ws_target_base}/ws"
    if client_id:
        ws_target_url += f"?clientId={client_id}"

    print(f"WS Proxy: Connecting to ComfyUI at {ws_target_url}")
    try:
        async with websockets.connect(ws_target_url, max_size=100 * 1024 * 1024) as comfy_ws_conn:
            print("WS Proxy: Connected to ComfyUI successfully")

            async def forward_to_comfy():
                try:
                    while True:
                        data = await websocket.receive()
                        if data.get("type") == "websocket.disconnect":
                            print("WS Proxy: Client disconnected (forward_to_comfy)")
                            break
                        if "text" in data:
                            await comfy_ws_conn.send(data["text"])
                        elif "bytes" in data:
                            await comfy_ws_conn.send(data["bytes"])
                except Exception as e:
                    print(f"WS Proxy: Exception in forward_to_comfy: {e}")

            async def forward_to_client():
                try:
                    while True:
                        msg = await comfy_ws_conn.recv()
                        if isinstance(msg, bytes):
                            await websocket.send_bytes(msg)
                        else:
                            await websocket.send_text(msg)
                except Exception as e:
                    print(f"WS Proxy: Exception in forward_to_client: {e}")

            task1 = asyncio.create_task(forward_to_comfy())
            task2 = asyncio.create_task(forward_to_client())
            await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)
            print("WS Proxy: Forwarding task finished, cleaning up")
            task1.cancel()
            task2.cancel()

    except WebSocketDisconnect:
        print("WS Proxy: WebSocketDisconnect in outer handler")
    except Exception as e:
        print(f"WS Proxy: Exception in outer handler connecting/running: {e}")


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
