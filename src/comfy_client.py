import requests
import json
import uuid
import websockets

class ComfyClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())

    def check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/system_stats")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def submit_workflow(self, workflow):
        response = requests.post(
            f"{self.base_url}/prompt", 
            json={"prompt": workflow, "client_id": self.client_id}
        )
        response.raise_for_status()
        return response.json().get("prompt_id")

    async def listen_for_images(self, prompt_id):
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        async with websockets.connect(f"{ws_url}/ws?clientId={self.client_id}") as websocket:
            while True:
                message = await websocket.recv()
                if isinstance(message, str):
                    message = json.loads(message)
                    if message["type"] == "progress":
                        data = message["data"]
                        if data["prompt_id"] == prompt_id:
                            yield {
                                "type": "progress", 
                                "value": data["value"], 
                                "max": data["max"]
                            }
                    elif message["type"] == "executed":
                        data = message["data"]
                        if data["prompt_id"] == prompt_id:
                            outputs = data["output"]
                            for key in outputs:
                                for image in outputs[key]:
                                    if image["type"] == "output":
                                        filename = image["filename"]
                                        subfolder = image["subfolder"]
                                        # Note: Blocking call in async loop
                                        image_data = self._get_image(filename, subfolder, image["type"])
                                        yield {"type": "image", "data": image_data}
                            break # End loop after receiving images for this prompt

    def _get_image(self, filename, subfolder, folder_type):
        response = requests.get(
            f"{self.base_url}/view", 
            params={"filename": filename, "subfolder": subfolder, "type": folder_type}
        )
        return response.content