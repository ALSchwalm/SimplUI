import tomllib
import pathlib


def test_pyproject_requires_python():
    pyproject_path = pathlib.Path("pyproject.toml")
    assert pyproject_path.exists()

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    assert "project" in config
    assert "requires-python" in config["project"]
    assert config["project"]["requires-python"] == ">=3.11"
