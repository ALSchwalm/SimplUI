import json
import pytest
from src.comfy_client import ComfyClient

def test_z_image_prompt_injection():
    # Mock z-image.json structure
    workflow = {
        "58": {
            "inputs": {
                "value": ""
            },
            "class_type": "PrimitiveStringMultiline",
            "_meta": {
                "title": "Prompt"
            }
        }
    }
    
    client = ComfyClient("http://localhost:8188")
    prompt_text = "A beautiful sunset"
    
    success = client.inject_prompt(workflow, prompt_text)
    
    # This is expected to FAIL currently because inject_prompt doesn't handle "value"
    assert success is True, "inject_prompt should return True"
    assert workflow["58"]["inputs"]["value"] == prompt_text, f"Expected {prompt_text}, but got {workflow['58']['inputs'].get('value')}"

def test_standard_prompt_injection():
    # Verify we don't break standard injection
    workflow = {
        "3": {
            "_meta": {"title": "Prompt"},
            "inputs": {"text": "default"}
        }
    }
    
    client = ComfyClient("http://localhost:8188")
    prompt_text = "A beautiful sunset"
    
    success = client.inject_prompt(workflow, prompt_text)
    
    assert success is True
    assert workflow["3"]["inputs"]["text"] == prompt_text

def test_z_image_prompt_hiding():
    from ui import extract_workflow_inputs
    workflow = {
        "58": {
            "inputs": {
                "value": "default"
            },
            "_meta": {
                "title": "Prompt"
            }
        }
    }
    extracted = extract_workflow_inputs(workflow)
    # The Prompt node should be filtered out because it only has the 'value' input which is now hidden
    assert len(extracted) == 0

def test_z_image_prompt_default_value():
    from ui import get_prompt_default_value
    workflow = {
        "58": {
            "inputs": {
                "value": "initial prompt"
            },
            "_meta": {
                "title": "Prompt"
            }
        }
    }
    assert get_prompt_default_value(workflow) == "initial prompt"
