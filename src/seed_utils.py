import random

def generate_batch_seeds(base_seed: int, count: int) -> list[int]:
    """
    Generates a deterministic sequence of seeds from a base seed.
    """
    # Initialize a separate Random instance to avoid affecting global state
    # and to ensure reproducibility independent of other random calls.
    rng = random.Random(base_seed)
    
    seeds = []
    for _ in range(count):
        # Generate a 64-bit integer
        seeds.append(rng.randint(0, 18446744073709551615))
        
    return seeds
