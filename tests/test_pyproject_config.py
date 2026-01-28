import os
import tomllib


def test_pyproject_toml_config():
    """
    Verifies that pyproject.toml exists and has the correct black configuration.
    """
    path = "pyproject.toml"
    assert os.path.exists(path), "pyproject.toml does not exist"

    with open(path, "rb") as f:
        config = tomllib.load(f)

    assert "tool" in config
    assert "black" in config["tool"]
    assert config["tool"]["black"]["line-length"] == 100
