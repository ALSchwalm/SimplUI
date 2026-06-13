import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# We import the FastAPI app from main.py
try:
    from main import app
except ImportError:
    app = None

def test_api_config():
    assert app is not None, "FastAPI app is not defined in main.py"
    client = TestClient(app)
    
    # Mock config data
    with patch("main.get_config") as mock_get_config:
        mock_config = MagicMock()
        mock_config.comfy_url = "http://127.0.0.1:8188"
        mock_config.workflows = [{"name": "Test Workflow", "path": "workflows/test.json"}]
        mock_get_config.return_value = mock_config
        
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert data["comfy_url"] == "http://127.0.0.1:8188"
        assert len(data["workflows"]) == 1
        assert data["workflows"][0]["name"] == "Test Workflow"

def test_static_assets():
    assert app is not None, "FastAPI app is not defined in main.py"
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 200
    
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    
    response = client.get("/static/app.js")
    assert response.status_code == 200

def test_get_workflow(tmp_path):
    assert app is not None, "FastAPI app is not defined in main.py"
    client = TestClient(app)
    
    # Create a dummy workflow file
    wf_file = tmp_path / "test_wf.json"
    wf_file.write_text('{"nodes": []}')
    
    with patch("main.get_config") as mock_get_config:
        mock_config = MagicMock()
        mock_config.workflows = [{"name": "Test Workflow", "path": str(wf_file)}]
        mock_get_config.return_value = mock_config
        
        response = client.get("/api/workflows/Test Workflow")
        assert response.status_code == 200
        assert response.json() == {"nodes": []}

def test_get_workflow_not_found():
    assert app is not None, "FastAPI app is not defined in main.py"
    client = TestClient(app)
    
    with patch("main.get_config") as mock_get_config:
        mock_config = MagicMock()
        mock_config.workflows = [{"name": "Test Workflow", "path": "workflows/test.json"}]
        mock_get_config.return_value = mock_config
        
        response = client.get("/api/workflows/Nonexistent")
        assert response.status_code == 404

def test_split_addr():
    from main import split_addr
    assert split_addr("127.0.0.1:8000", "0.0.0.0", 7860) == ("127.0.0.1", 8000)
    assert split_addr("127.0.0.1", "0.0.0.0", 7860) == ("127.0.0.1", 7860)
    assert split_addr("", "0.0.0.0", 7860) == ("0.0.0.0", 7860)
    assert split_addr("127.0.0.1:invalid", "0.0.0.0", 7860) == ("127.0.0.1", 7860)
    assert split_addr(":8000", "0.0.0.0", 7860) == ("0.0.0.0", 8000)

@patch("argparse.ArgumentParser.parse_args")
def test_parse_args(mock_parse_args):
    from main import parse_args
    mock_parse_args.return_value = MagicMock(comfy_addr="127.0.0.1:8188", listen_addr="0.0.0.0:7860", config="config.json")
    args = parse_args()
    assert args.comfy_addr == "127.0.0.1:8188"

@patch("main.parse_args")
@patch("main.ConfigManager")
@patch("main.ComfyClient")
@patch("uvicorn.run")
@patch("os.path.exists")
def test_main_success(mock_exists, mock_run, mock_client_cls, mock_config_cls, mock_parse_args):
    from main import main
    mock_parse_args.return_value = MagicMock(comfy_addr="127.0.0.1:8188", listen_addr="0.0.0.0:7860", config="config.json")
    mock_exists.return_value = True
    
    mock_config = MagicMock()
    mock_config.comfy_url = "http://localhost:8188"
    mock_config.workflows = [{"name": "wf", "path": "wf.json"}]
    mock_config_cls.return_value = mock_config
    
    mock_client = MagicMock()
    mock_client.check_connection.return_value = True
    mock_client_cls.return_value = mock_client
    
    main()
    
    mock_config_cls.assert_called_once_with("config.json")
    mock_run.assert_called_once()

@patch("requests.request")
def test_comfy_proxy(mock_request):
    assert app is not None, "FastAPI app is not defined in main.py"
    client = TestClient(app)
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"proxy response"
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_request.return_value = mock_resp
    
    app.state.comfy_url = "http://localhost:8188"
    with patch("main.get_config") as mock_get_config:
        mock_config = MagicMock()
        mock_config.comfy_url = "http://localhost:8188"
        mock_get_config.return_value = mock_config
        
        response = client.get("/comfy-proxy/object_info")
        assert response.status_code == 200
        assert response.content == b"proxy response"
        assert response.headers["Content-Type"] == "application/json"
        
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:8188/object_info"
