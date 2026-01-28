import pytest
import sys
from unittest.mock import patch

# Note: We expect to refactor main.py to include a parse_args function.
# These tests will fail until that refactor is done.


def test_parse_args_none():
    """Test that default values are returned when no arguments are provided."""
    from main import parse_args

    with patch.object(sys, "argv", ["main.py"]):
        args = parse_args()
        assert args.comfy_addr is None
        assert args.listen_addr is None
        assert args.config == "config.json"


def test_parse_args_all():
    """Test that all arguments are correctly parsed."""
    from main import parse_args

    test_args = [
        "main.py",
        "--comfy-addr",
        "10.0.0.1:8188",
        "--listen-addr",
        "127.0.0.1:7861",
        "--config",
        "test_config.json",
    ]
    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.comfy_addr == "10.0.0.1:8188"
        assert args.listen_addr == "127.0.0.1:7861"
        assert args.config == "test_config.json"


def test_address_splitting():
    """Test the logic for splitting address into host and port."""
    from main import split_addr

    host, port = split_addr("127.0.0.1:7860", "0.0.0.0", 7860)
    assert host == "127.0.0.1"
    assert port == 7860

    host, port = split_addr("localhost:8188", "0.0.0.0", 7860)
    assert host == "localhost"
    assert port == 8188

    # Test fallback to defaults if None or malformed
    host, port = split_addr(None, "0.0.0.0", 7860)
    assert host == "0.0.0.0"
    assert port == 7860

    # Test only port
    host, port = split_addr(":9000", "127.0.0.1", 7860)
    assert host == "127.0.0.1"
    assert port == 9000

    # Test only host (this might be tricky, let's assume it requires colon for port)
    host, port = split_addr("myhost", "0.0.0.0", 7860)
    assert host == "myhost"
    assert port == 7860
