import pytest
import requests
from comfy_client import ComfyClient
from unittest.mock import patch, Mock

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
