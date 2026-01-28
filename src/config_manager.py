import json
import copy

DEFAULT_SLIDERS = {
    "steps": {"min": 1, "max": 100, "step": 1},
    "cfg": {"min": 0.0, "max": 20.0, "step": 0.1},
    "denoise": {"min": 0.0, "max": 1.0, "step": 0.01},
}


class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.comfy_url = ""
        self.workflows = []
        self.sliders = copy.deepcopy(DEFAULT_SLIDERS)
        self._load()

    def _load(self):
        with open(self.config_path, "r") as f:
            data = json.load(f)
            self.comfy_url = data.get("comfy_url", "")
            self.workflows = data.get("workflows", [])

            overrides = data.get("slider_overrides", {})
            for key, val in overrides.items():
                if key in self.sliders:
                    self.sliders[key].update(val)
                else:
                    self.sliders[key] = val
