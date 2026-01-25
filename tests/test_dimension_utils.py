import pytest
from dimension_utils import calculate_dimensions

def test_calculate_dimensions_1to1_1m():
    # 1:1 and 1M should be exactly 1024x1024
    width, height = calculate_dimensions("1:1", 1.0)
    assert width == 1024
    assert height == 1024

def test_calculate_dimensions_16to9_1m():
    # 16:9 and 1M pixels (1,048,576)
    # Height = sqrt(1048576 / (16/9)) = 768
    # Width = 768 * 16/9 = 1365.33 -> round to 64 -> 1344
    width, height = calculate_dimensions("16:9", 1.0)
    assert width == 1344
    assert height == 768
    assert width % 64 == 0
    assert height % 64 == 0

def test_calculate_dimensions_rounding():
    # Test rounding to nearest 64
    # Example: 1:1 at 0.5M
    # Total pixels = 524288
    # Height = sqrt(524288) = 724.07
    # Nearest 64: 704 (64*11) or 768 (64*12)
    # 724-704 = 20, 768-724 = 44. So 704.
    width, height = calculate_dimensions("1:1", 0.5)
    assert width == 704
    assert height == 704

def test_calculate_dimensions_various_ratios():
    ratios = ["4:3", "3:4", "3:2", "2:3", "7:9", "9:7", "1:2", "2:1"]
    for ratio in ratios:
        width, height = calculate_dimensions(ratio, 1.0)
        assert width % 64 == 0
        assert height % 64 == 0
        assert width > 0
        assert height > 0

def test_calculate_dimensions_invalid_ratio():
    # Should default to 1:1 if ratio is invalid
    width, height = calculate_dimensions("invalid", 1.0)
    assert width == 1024
    assert height == 1024
