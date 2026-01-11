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
    
    # Check KSampler
    ksampler = next(n for n in extracted if n["title"] == "KSampler")
    assert ksampler["node_id"] == "1"
    assert len(ksampler["inputs"]) == 3
    
    steps_input = next(i for i in ksampler["inputs"] if i["name"] == "steps")
    assert steps_input["value"] == 20
    assert steps_input["type"] == "number"
    
    cfg_input = next(i for i in ksampler["inputs"] if i["name"] == "cfg")
    assert cfg_input["value"] == 8.0
    assert cfg_input["type"] == "number"
    
    # Check CheckpointLoader
    ckpt = next(n for n in extracted if n["title"] == "CheckpointLoader")
    assert ckpt["node_id"] == "2"
    ckpt_input = next(i for i in ckpt["inputs"] if i["name"] == "ckpt_name")
    assert ckpt_input["value"] == "v1-5-pruned-emaonly.ckpt"

def test_extract_workflow_inputs_seed_randomization():
    from ui import extract_workflow_inputs
    
    workflow = {
        "1": {
            "_meta": {"title": "KSampler"},
            "inputs": {
                "seed": 0, # Should default to random
                "steps": 20
            }
        },
        "2": {
            "_meta": {"title": "AnotherSampler"},
            "inputs": {
                "seed": 12345, # Should NOT default to random
                "noise_seed": 0 # Should detect "seed" in name
            }
        }
    }
    
    extracted = extract_workflow_inputs(workflow)
    
    # Check Node 1
    node1 = next(n for n in extracted if n["node_id"] == "1")
    seed_input = next(i for i in node1["inputs"] if i["name"] == "seed")
    assert seed_input["type"] == "seed" # New type
    assert seed_input["randomize"] is True
    
    steps_input = next(i for i in node1["inputs"] if i["name"] == "steps")
    assert steps_input["type"] == "number"
    
    # Check Node 2
    node2 = next(n for n in extracted if n["node_id"] == "2")
    seed2_input = next(i for i in node2["inputs"] if i["name"] == "seed")
    assert seed2_input["type"] == "seed"
    assert seed2_input["randomize"] is False
    
    noise_seed_input = next(i for i in node2["inputs"] if i["name"] == "noise_seed")
    assert noise_seed_input["type"] == "seed"
    assert noise_seed_input["randomize"] is True


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

def test_extract_workflow_inputs_sliders():
    from ui import extract_workflow_inputs
    
    workflow = {
        "1": {
            "_meta": {"title": "KSampler"},
            "class_type": "KSampler",
            "inputs": {
                "steps": 20,
                "cfg": 8.0,
                "other": 50
            }
        }
    }
    
    # Mock slider config
    slider_config = {
        "steps": {"min": 1, "max": 100, "step": 1},
        "cfg": {"min": 0.0, "max": 20.0, "step": 0.1}
    }
    
    extracted = extract_workflow_inputs(workflow, slider_config=slider_config)
    
    node = extracted[0]
    
    # steps should be slider
    steps = next(i for i in node["inputs"] if i["name"] == "steps")
    assert steps["type"] == "slider"
    assert steps["min"] == 1
    assert steps["max"] == 100
    
    # cfg should be slider
    cfg = next(i for i in node["inputs"] if i["name"] == "cfg")
    assert cfg["type"] == "slider"
    assert cfg["step"] == 0.1
    
    # other should be number
    other = next(i for i in node["inputs"] if i["name"] == "other")
    assert other["type"] == "number"