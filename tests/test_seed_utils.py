import pytest
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from seed_utils import generate_batch_seeds


def test_generate_batch_seeds_determinism():
    base_seed = 12345
    count = 5
    seeds1 = generate_batch_seeds(base_seed, count)
    seeds2 = generate_batch_seeds(base_seed, count)
    assert seeds1 == seeds2
    assert len(seeds1) == count


def test_generate_batch_seeds_variance():
    base_seed1 = 12345
    base_seed2 = 67890
    seeds1 = generate_batch_seeds(base_seed1, 5)
    seeds2 = generate_batch_seeds(base_seed2, 5)
    assert seeds1 != seeds2


def test_generate_batch_seeds_range():
    base_seed = 100
    seeds = generate_batch_seeds(base_seed, 20)
    for seed in seeds:
        assert 0 <= seed <= 18446744073709551615
