import pytest
from ui import extract_workflow_inputs

def test_extract_workflow_inputs():
    workflow = {
        "1": {
            "_meta": {"title": "KSampler"},
            "inputs": {
                "steps": 20,
                "cfg": 8.0,
                "sampler_name": "euler",
                "model": ["4", 0] # Link to another node, should be ignored
            }
        },
        "2": {
            "_meta": {"title": "CheckpointLoader"},
            "inputs": {
                "ckpt_name": "v1-5-pruned-emaonly.ckpt"
            }
        },
        "3": {
            "_meta": {"title": "Prompt"},
            "inputs": {
                "text": "This should be filtered",
                "other_param": 123
            }
        }
    }
    
    extracted = extract_workflow_inputs(workflow)
    
    # KSampler and CheckpointLoader should be there
    assert len(extracted) == 3
    
    # Check Prompt node
    prompt_node = next(n for n in extracted if n["title"] == "Prompt")
    assert prompt_node["node_id"] == "3"
    
    # 'text' input should be missing
    input_names = [i["name"] for i in prompt_node["inputs"]]
    assert "text" not in input_names
    assert "other_param" in input_names

def test_extract_workflow_inputs_with_metadata():
    from ui import extract_workflow_inputs
    
    workflow = {
        "1": {
            "_meta": {"title": "KSampler"},
            "class_type": "KSampler",
            "inputs": {
                "sampler_name": "euler"
            }
        }
    }
    
    # Mock Object Info
    object_info = {
        "KSampler": {
            "input": {
                "required": {
                    "sampler_name": [["euler", "ddim", "heun"]]
                }
            }
        }
    }
    
    extracted = extract_workflow_inputs(workflow, object_info)
    
    node = extracted[0]
    sampler_input = node["inputs"][0]
    
    assert sampler_input["name"] == "sampler_name"
    assert sampler_input["type"] == "enum"
    assert sampler_input["options"] == ["euler", "ddim", "heun"]
    assert sampler_input["value"] == "euler"

def test_merge_workflow_overrides():
    from ui import merge_workflow_overrides
    
    workflow = {
        "1": {"inputs": {"steps": 20, "cfg": 8.0}},
        "2": {"inputs": {"text": "default"}}
    }
    
    overrides = {
        "1.steps": 30,
        "1.cfg": 7.5,
        "2.text": "new prompt"
    }
    
    merged = merge_workflow_overrides(workflow, overrides)
    
    assert merged["1"]["inputs"]["steps"] == 30
    assert merged["1"]["inputs"]["cfg"] == 7.5
    assert merged["2"]["inputs"]["text"] == "new prompt"
    
    # Original should be untouched (optional, but good practice)
    assert workflow["1"]["inputs"]["steps"] == 20

def test_get_prompt_default_value():
    from ui import get_prompt_default_value
    
    # Workflow with a Prompt node
    workflow_with_prompt = {
        "1": {"_meta": {"title": "Prompt"}, "inputs": {"text": "A photo of a cat"}}
    }
    assert get_prompt_default_value(workflow_with_prompt) == "A photo of a cat"
    
    # Workflow with a Prompt node (case insensitive)
    workflow_case = {
        "1": {"_meta": {"title": "PROMPT"}, "inputs": {"string": "A photo of a dog"}}
    }
    assert get_prompt_default_value(workflow_case) == "A photo of a dog"
    
    # Workflow without Prompt node
    workflow_no_prompt = {
        "1": {"_meta": {"title": "KSampler"}, "inputs": {}}
    }
    assert get_prompt_default_value(workflow_no_prompt) == ""
