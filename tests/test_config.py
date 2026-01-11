import pytest
import json
import os
from config_manager import ConfigManager

def test_load_config_success(tmp_path):
    config_data = {
        "comfy_url": "http://remote-comfy:8188",
        "workflows": [
            {"name": "Cinematic", "path": "workflows/cinematic.json"}
        ]
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    
    manager = ConfigManager(str(config_file))
    assert manager.comfy_url == "http://remote-comfy:8188"
    assert len(manager.workflows) == 1
    assert manager.workflows[0]["name"] == "Cinematic"

def test_load_config_not_found():
    with pytest.raises(FileNotFoundError):
        ConfigManager("non_existent.json")

def test_load_config_invalid_json(tmp_path):
    config_file = tmp_path / "invalid.json"
    config_file.write_text("invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        ConfigManager(str(config_file))

def test_slider_config_overrides(tmp_path):
    config_data = {
        "comfy_url": "http://localhost",
        "slider_overrides": {
            "steps": {"max": 50},
            "custom_param": {"min": 0, "max": 10, "step": 1}
        }
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    
    manager = ConfigManager(str(config_file))
    
    # Check default (cfg should exist)
    assert "cfg" in manager.sliders
    assert manager.sliders["cfg"]["max"] == 20.0
    
    # Check override (steps max changed)
    assert manager.sliders["steps"]["max"] == 50
    assert manager.sliders["steps"]["min"] == 1 # Default preserved
    
    # Check new
    assert manager.sliders["custom_param"]["max"] == 10
