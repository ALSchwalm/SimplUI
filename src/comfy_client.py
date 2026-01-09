import requests

class ComfyClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/system_stats")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def submit_workflow(self, workflow):
        response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow})
        response.raise_for_status()
        return response.json().get("prompt_id")
