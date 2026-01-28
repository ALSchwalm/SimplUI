import subprocess


def test_codebase_formatted():
    """
    Verifies that the codebase is formatted according to black.
    """
    # --check returns 1 if files would be reformatted
    result = subprocess.run(["black", "--check", "."], capture_output=True, text=True)
    assert result.returncode == 0, f"Codebase is not formatted: {result.stderr or result.stdout}"
