from pathlib import Path


def absolute_from_root_relative(path):
    root = Path(__file__).parent.parent
    return root / path
