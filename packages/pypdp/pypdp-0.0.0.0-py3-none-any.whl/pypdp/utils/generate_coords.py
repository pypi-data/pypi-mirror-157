import numpy as np


def get_uniform_coords(n: int) -> np.array:
    """get uniformly distributed points from [0,1] x [0,1]

    Args:
        n (int): number of points

    Returns:
        np.array: coordinates in [n, 2]
    """
    coords = np.random.uniform(0.0, 1.0, size=(n, 2))

    return coords
