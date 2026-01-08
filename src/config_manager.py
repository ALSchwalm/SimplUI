import json

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.comfy_url = ""
        self.workflows = []
        self._load()

    def _load(self):
        with open(self.config_path, "r") as f:
            data = json.load(f)
            self.comfy_url = data.get("comfy_url", "")
            self.workflows = data.get("workflows", [])
