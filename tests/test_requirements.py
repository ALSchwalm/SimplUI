import os

def test_black_in_requirements():
    """
    Verifies that 'black' is listed in requirements.txt.
    """
    req_path = "requirements.txt"
    assert os.path.exists(req_path)
    with open(req_path, "r") as f:
        content = f.read()
    assert "black" in content.lower()
