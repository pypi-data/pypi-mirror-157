import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionPatch

from pypdp.engine.manager import PDPManager
from pypdp.engine.pickup import Pickup
from pypdp.engine.status import PickupStatus, VehicleStatus
from pypdp.env import PDPenv


def visualize_env(env_or_manager, ax=None):
    DEPOT_MARKER = 's'
    DEPOT_MAKRKER_SIZE = 75
    DEPOT_MARKER_COLOR = "black"

    PICKUP_MARKER = 'o'
    PICKUP_MARKER_SIZE = 75
    PICKUP_FACE_COLOR = 'white'
    PICKUP_EDGE_COLOR = 'black'

    DELIVERY_MARKER = 's'
    DELIVERY_MARKER_SIZE = 75
    DELIVERY_FACE_COLOR = 'white'
    DELIVERY_EDGE_COLOR = 'black'

    TOUR_MARKER_SIZE = 50
    VEHICLE_MARKER = '^'

    if isinstance(env_or_manager, PDPManager):
        manager = env_or_manager
    elif isinstance(env_or_manager, PDPenv):
        manager = env_or_manager.manager
    else:
        raise RuntimeError("Input is not expected type.")

    if ax is None:
        fig, ax = plt.subplots(1, 1)

    # Visualize the depot
    ax.scatter(manager.depot.loc[0], manager.depot.loc[1],
               marker=DEPOT_MARKER, s=DEPOT_MAKRKER_SIZE, c=DEPOT_MARKER_COLOR,
               zorder=5)

    # Visualize "unvisited" pickups and their corresponding deliveries
    for p in manager.pickups.values():
        if p.status == PickupStatus.ACTIVE:
            p_x, p_y = p.loc[0], p.loc[1]
            d = manager.deliveries[p.delivery_idx]
            d_x, d_y = d.loc[0], d.loc[1]

            ax.scatter(p_x, p_y, marker=PICKUP_MARKER,
                       s=PICKUP_MARKER_SIZE,
                       fc=PICKUP_FACE_COLOR,
                       ec=PICKUP_EDGE_COLOR)
            ax.scatter(d_x, d_y, marker=DELIVERY_MARKER,
                       s=DELIVERY_MARKER_SIZE,
                       fc=DELIVERY_FACE_COLOR,
                       ec=DELIVERY_EDGE_COLOR)
            con = ConnectionPatch((p_x, p_y), (d_x, d_y), "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=15,
                                  ls='--', fc='gray', color='gray')
            ax.add_artist(con)

    for i, v in enumerate(manager.vehicles.values()):
        c = 'C{}'.format(i)

        # visualize partial tour: History
        x, y = np.array(v.tour)[:, 0], np.array(v.tour)[:, 1]
        ax.plot(x, y, c=c)

        for ii, t_id in enumerate(v.tour_idx):
            if 0 < t_id <= manager.n:  # pickup
                ax.scatter(x[ii], y[ii], c=c, marker=PICKUP_MARKER)
            elif t_id > manager.n:  # delivery
                ax.scatter(x[ii], y[ii], c=c, marker=DELIVERY_MARKER)
            else:  # depot
                pass

        # current position
        ax.scatter(v.loc[0], v.loc[1],
                   marker=VEHICLE_MARKER,
                   fc='C{}'.format(i),
                   ec='black',
                   s=TOUR_MARKER_SIZE,
                   zorder=3)

        # Visualize assigned task: Future
        # current task --> vehicle --> next task
        if v.status == VehicleStatus.ASSIGNED:
            pt = v.prev_task
            nt = v.next_task

            # prev task -> current pos
            ax.plot([pt.loc[0], v.loc[0]], [pt.loc[1], v.loc[1]], c=c)

            # next position
            is_nt_pickup = isinstance(nt, Pickup)

            marker = PICKUP_MARKER if is_nt_pickup else DELIVERY_MARKER
            ax.scatter(nt.loc[0], nt.loc[1], ec='C{}'.format(i), fc='white',
                       marker=marker,
                       s=TOUR_MARKER_SIZE)

            if is_nt_pickup:
                d = manager.deliveries[nt.delivery_idx]
                ax.scatter(d.loc[0], d.loc[1], ec='C{}'.format(i), fc='white',
                           marker=DELIVERY_MARKER,
                           s=TOUR_MARKER_SIZE)

            con = ConnectionPatch((v.loc[0], v.loc[1]), (nt.loc[0], nt.loc[1]), "data", "data",
                                  arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=15,
                                  ls='--', color=c)
            ax.add_artist(con)

        if len(v.visitable_delivery_idx) > 0:
            for d_idx in v.visitable_delivery_idx:
                d = manager.deliveries[d_idx]
                ax.scatter(d.loc[0], d.loc[1], ec='C{}'.format(i),
                           marker=DELIVERY_MARKER,
                           fc='white', s=TOUR_MARKER_SIZE)
