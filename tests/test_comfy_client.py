import pytest
import requests
import json
from comfy_client import ComfyClient
from unittest.mock import patch, Mock, AsyncMock

def test_check_connection_success():
    client = ComfyClient("http://localhost:8188")
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        assert client.check_connection() is True

def test_check_connection_failure():
    client = ComfyClient("http://localhost:8188")
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 500
        assert client.check_connection() is False

def test_check_connection_exception():
    client = ComfyClient("http://localhost:8188")
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException()
        assert client.check_connection() is False

def test_submit_workflow_success():
    client = ComfyClient("http://localhost:8188")
    workflow = {"3": {"inputs": {"seed": 5}}}
    response_data = {"prompt_id": "12345", "number": 1, "node_errors": {}}
    client_id = "test-client-id"
    
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = response_data
        
        prompt_id = client.submit_workflow(workflow, client_id)
        
        assert prompt_id == "12345"
        mock_post.assert_called_once_with(
            "http://localhost:8188/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=10
        )

def test_submit_workflow_failure():
    client = ComfyClient("http://localhost:8188")
    workflow = {}
    client_id = "test-client-id"
    
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.submit_workflow(workflow, client_id)

def test_find_node_by_title():
    client = ComfyClient("http://localhost:8188")
    workflow = {
        "1": {"_meta": {"title": "Prompt"}, "inputs": {"text": "default"}},
        "2": {"_meta": {"title": "KSampler"}, "inputs": {}},
        "3": {"inputs": {}} # No meta
    }
    
    # Exact match
    node_id = client.find_node_by_title(workflow, "Prompt")
    assert node_id == "1"
    
    # Case insensitive
    node_id = client.find_node_by_title(workflow, "prompt")
    assert node_id == "1"
    
    # Not found
    node_id = client.find_node_by_title(workflow, "NonExistent")
    assert node_id is None

def test_inject_prompt():
    client = ComfyClient("http://localhost:8188")
    workflow = {
        "1": {"_meta": {"title": "Prompt"}, "inputs": {"text": "default"}},
        "2": {"_meta": {"title": "KSampler"}, "inputs": {}},
        "3": {"inputs": {"text": "should not change"}}
    }
    
    # Successful injection
    success = client.inject_prompt(workflow, "New Prompt Value")
    assert success is True
    assert workflow["1"]["inputs"]["text"] == "New Prompt Value"
    assert workflow["3"]["inputs"]["text"] == "should not change"
    
    # Injection failure (no node)
    workflow_no_prompt = {"2": {"_meta": {"title": "KSampler"}, "inputs": {}}}
    success = client.inject_prompt(workflow_no_prompt, "New Prompt Value")
    assert success is False

def test_interrupt_success():

    client = ComfyClient("http://localhost:8188")

    with patch("requests.post") as mock_post:

        mock_post.return_value.status_code = 200

        client.interrupt()

        mock_post.assert_called_once_with("http://localhost:8188/interrupt", timeout=5)



def test_clear_queue_success():

    client = ComfyClient("http://localhost:8188")

    with patch("requests.post") as mock_post:

        mock_post.return_value.status_code = 200

        client.clear_queue()

        mock_post.assert_called_once_with(

            "http://localhost:8188/queue",

            json={"clear": True},

            timeout=5

        )
