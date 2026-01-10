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
        }
    }
    
    extracted = extract_workflow_inputs(workflow)
    
    assert len(extracted) == 2
    
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
    
    sampler_input = next(i for i in ksampler["inputs"] if i["name"] == "sampler_name")
    assert sampler_input["value"] == "euler"
    assert sampler_input["type"] == "str"
    
    # Check CheckpointLoader
    ckpt = next(n for n in extracted if n["title"] == "CheckpointLoader")
    assert ckpt["node_id"] == "2"
    ckpt_input = next(i for i in ckpt["inputs"] if i["name"] == "ckpt_name")
    assert ckpt_input["value"] == "v1-5-pruned-emaonly.ckpt"

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
