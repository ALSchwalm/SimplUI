import subprocess


def test_black_installed():
    """
    Verifies that 'black' is installed and accessible in the environment.
    """
    result = subprocess.run(["black", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "black" in result.stdout.lower()
