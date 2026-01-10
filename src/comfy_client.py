import requests
import json
import uuid
import websockets

class ComfyClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/system_stats")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def submit_workflow(self, workflow, client_id):
        response = requests.post(
            f"{self.base_url}/prompt", 
            json={"prompt": workflow, "client_id": client_id}
        )
        response.raise_for_status()
        return response.json().get("prompt_id")

    async def generate_image(self, workflow):
        client_id = str(uuid.uuid4())
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        async with websockets.connect(f"{ws_url}/ws?clientId={client_id}", max_size=10 * 1024 * 1024) as websocket:
            
            # Submit workflow AFTER connecting
            try:
                prompt_id = self.submit_workflow(workflow, client_id)
            except Exception as e:
                raise e

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
                                    if image.get("type") in ["output", "temp"]:
                                        filename = image["filename"]
                                        subfolder = image["subfolder"]
                                        # Note: Blocking call in async loop
                                        image_data = self._get_image(filename, subfolder, image["type"])
                                        yield {"type": "image", "data": image_data}
                            break # End loop after receiving images for this prompt
                elif isinstance(message, bytes):
                    # Binary message is a preview
                    yield {"type": "preview", "data": message[8:]}

    def _get_image(self, filename, subfolder, folder_type):
        response = requests.get(
            f"{self.base_url}/view", 
            params={"filename": filename, "subfolder": subfolder, "type": folder_type}
        )
        return response.content

    def find_node_by_title(self, workflow, title):
        title = title.lower()
        for node_id, node_data in workflow.items():
            meta = node_data.get("_meta", {})
            node_title = meta.get("title", "")
            if node_title.lower() == title:
                return node_id
        return None

    def inject_prompt(self, workflow, prompt_text):
        node_id = self.find_node_by_title(workflow, "Prompt")
        if node_id:
            # We assume the input field is named 'text' or 'string'.
            # We prioritize 'text' as it's common for CLIPTextEncode.
            # A more robust solution would inspect the node type definition, but that requires an API call.
            inputs = workflow[node_id].get("inputs", {})
            if "text" in inputs:
                inputs["text"] = prompt_text
                return True
            elif "string" in inputs:
                inputs["string"] = prompt_text
                return True
            # Fallback: if 'text' isn't there, maybe create it? 
            # Or assume 'text' is the target if inputs is empty?
            # Let's set 'text' if neither exists, assuming standard CLIPTextEncode behavior.
            inputs["text"] = prompt_text
            return True
        return False

    def interrupt(self):
        try:
            requests.post(f"{self.base_url}/interrupt")
        except Exception:
            pass

    def clear_queue(self):
        try:
            requests.post(f"{self.base_url}/queue", json={"clear": True})
        except Exception:
            pass
