import numpy as np

from pypdp.engine.depot import Depot
from pypdp.engine.pickup import Pickup
from pypdp.engine.status import VehicleStatus, PickupStatus, DeliveryStatus


def calc_dist(src, dst):
    return np.sqrt(np.sum((src - dst) ** 2))


class Vehicle:
    def __init__(self,
                 idx: int):
        self.idx = idx
        self.status = VehicleStatus.ACTIVE

        self.loc = None
        self.prev_task = None
        self.prev_task_idx = None

        self.next_task = None
        self.next_task_idx = None
        self.remaining_distance = -1

        # tour information
        self.tour_idx = None
        self.tour = None
        self.tour_length = -1

        # visited pickups
        self.visited_pickup_idx = set()
        self.visitable_delivery_idx = set()  # later to construct action space

    def set_initial_task(self, task):
        self.loc = np.array(task.loc)
        self.prev_task = task
        self.prev_task_idx = task.idx

        self.tour_idx = [task.idx]
        self.tour = [self.loc.tolist()]
        self.tour_length = 0.0

    def travel(self, time: float, manager):
        """
        simulate the vehicle's tour. assuming the unit traveling speed
        """

        assert self.status == VehicleStatus.ASSIGNED or self.status == VehicleStatus.TO_DEPOT
        assert self.remaining_distance >= 0.0

        # traveling
        cur_x, cur_y = self.loc
        next_x, next_y = self.next_task.loc

        dy, dx = (next_y - cur_y), (next_x - cur_x)

        if np.allclose(dx, 0):
            theta = np.pi * 0.5
        elif np.allclose(dy, 0):
            theta = 0.0
        else:
            theta = np.arctan(np.abs(dy / dx))

        self.loc += np.array([np.sign(dx) * time * np.cos(theta),
                              np.sign(dy) * time * np.sin(theta)])

        self.remaining_distance -= time
        self.tour_length += time

        # if reach to the destination city
        if np.allclose(self.loc, self.next_task.loc):
            if isinstance(self.next_task, Depot):  # arrive depot
                self.status = VehicleStatus.COMPLETED
                manager.completed_vehicle_idx.add(self.idx)
                manager.to_depot_vehicle_idx.remove(self.idx)

            elif isinstance(self.next_task, Pickup):  # arrive pickup
                self.status = VehicleStatus.ACTIVE
                self.next_task.status = PickupStatus.COMPLETED
                self.visited_pickup_idx.add(self.next_task.idx)
                self.visitable_delivery_idx.add(self.next_task.delivery_idx)

                manager.deliveries[self.next_task.delivery_idx].status = DeliveryStatus.ACTIVE

                manager.assigned_vehicle_idx.remove(self.idx)
                manager.active_vehicle_idx.add(self.idx)

                manager.assigned_pickup_idx.remove(self.next_task.idx)
                manager.completed_pickup_idx.add(self.next_task.idx)

                manager.inactive_delivery_idx.remove(self.next_task.delivery_idx)
                manager.active_delivery_idx.add(self.next_task.delivery_idx)

            else:  # arrive delivery
                self.status = VehicleStatus.ACTIVE
                self.next_task.status = DeliveryStatus.COMPLETED
                self.visitable_delivery_idx.remove(self.next_task.idx)

                manager.assigned_vehicle_idx.remove(self.idx)
                manager.active_vehicle_idx.add(self.idx)

                manager.assigned_delivery_idx.remove(self.next_task.idx)
                manager.completed_delivery_idx.add(self.next_task.idx)

            self.loc = np.array(self.next_task.loc)
            self.tour_idx.append(self.next_task.idx)
            self.tour.append(self.next_task.loc.tolist())
            self.prev_task_idx = self.next_task.idx
            self.prev_task = self.next_task
            self.next_task = None
            self.remaining_distance = 0.0
