from random import shuffle

import numpy as np

from pypdp.utils.generate_coords import get_uniform_coords


def get_uniform_problem(n: int, m: int) -> dict:
    """_summary_

    Args:
        n (int): _description_
        m (int): _description_

    Returns:
        dict: the coordinates of the depot, pickups, and deliveries
    """

    coords = get_uniform_coords(2 * n + 1)

    # prepare PD pairs (reqeusts)
    indices = list(range(1, 2 * n + 1))
    shuffle(indices)
    pickup_indices = indices[:n]
    delivery_indices = indices[n:]

    problem = dict()
    problem["coordinate"] = coords
    problem["pickup_delivery"] = (np.array([pickup_indices,
                                            delivery_indices]).T).tolist()

    problem["pickup_indices"] = pickup_indices
    problem["pickup_coordinate"] = coords[pickup_indices, :]
    problem["delivery_indices"] = delivery_indices
    problem["delivery_coordinate"] = coords[delivery_indices, :]
    problem["num_vehicles"] = m
    problem["num_requests"] = n
    return problem


if __name__ == "__main__":
    print(get_uniform_problem(2, 5))
