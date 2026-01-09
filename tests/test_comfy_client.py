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
    with patch("uuid.uuid4", return_value="test-client-id"):
        client = ComfyClient("http://localhost:8188")
        workflow = {"3": {"inputs": {"seed": 5}}}
        response_data = {"prompt_id": "12345", "number": 1, "node_errors": {}}
        
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = response_data
            
            prompt_id = client.submit_workflow(workflow)
            
            assert prompt_id == "12345"
            mock_post.assert_called_once_with(
                "http://localhost:8188/prompt",
                json={"prompt": workflow, "client_id": "test-client-id"}
            )

def test_submit_workflow_failure():
    client = ComfyClient("http://localhost:8188")
    workflow = {}
    
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.submit_workflow(workflow)
