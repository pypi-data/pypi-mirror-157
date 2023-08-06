from copy import deepcopy

import numpy as np

from pypdp.engine.delivery import Delivery
from pypdp.engine.depot import Depot
from pypdp.engine.pickup import Pickup
from pypdp.engine.status import VehicleStatus, PickupStatus, DeliveryStatus
from pypdp.engine.vehicle import Vehicle, calc_dist


class PDPManager:

    def __init__(self, problem):
        self.n = problem['num_requests']  # number of requests (the pair of pickup and delivery)
        self.m = problem['num_vehicles']  # number of vehicles

        self.depot = Depot(idx=0, loc=problem['coordinate'][0])
        self.pickups = {i + 1: Pickup(idx=i + 1,
                                      loc=problem['pickup_coordinate'][i]) for i in range(self.n)}

        self.deliveries = {self.n + 1 + i: Delivery(idx=self.n + i + 1,
                                                    loc=problem['delivery_coordinate'][i]) for i in range(self.n)}

        # set the pickup and delivery pairs
        for (pickup_id, pickup), (delivery_id, delivery) in zip(self.pickups.items(), self.deliveries.items()):
            pickup.delivery_idx = delivery_id
            delivery.pickup_idx = pickup_id

        self.vehicles = {2 * self.n + 1 + i: Vehicle(idx=2 * self.n + 1 + i) for i in range(self.m)}
        for v in self.vehicles.values():
            # assuming all vehicles start their tours from the depot.
            v.set_initial_task(self.depot)

        self.active_vehicle_idx = set([2 * self.n + 1 + i for i in range(self.m)])
        self.assigned_vehicle_idx = set()
        self.to_depot_vehicle_idx = set()
        self.completed_vehicle_idx = set()

        self.active_pickup_idx = set([i + 1 for i in range(self.n)])
        self.assigned_pickup_idx = set()
        self.completed_pickup_idx = set()

        self.inactive_delivery_idx = set([self.n + 1 + i for i in range(self.n)])
        self.active_delivery_idx = set()
        self.assigned_delivery_idx = set()
        self.completed_delivery_idx = set()

        self.target_vehicle = None
        self.target_vehicle_idx = None
        self.time = 0
        self.done = False
        self.set_target_vehicle()

    def get_idle_vehicle_indices(self):
        return deepcopy(self.active_vehicle_idx)

    def set_target_vehicle(self):
        idle_vehicle_idx = list(self.get_idle_vehicle_indices())
        target_idx = np.random.choice(idle_vehicle_idx)
        self.vehicles[target_idx].is_target = True
        self.target_vehicle = self.vehicles[target_idx]
        self.target_vehicle_idx = target_idx

    def set_next_task(self, vehicle_idx, task_idx):
        vehicle = self.vehicles[vehicle_idx]
        assert vehicle.status == VehicleStatus.ACTIVE

        if task_idx == 0:  # when the task is the depot.
            vehicle.status = VehicleStatus.TO_DEPOT
            vehicle.next_task = self.depot
            vehicle.next_task_idx = 0

            # adjust "active vehicle idx"
            self.active_vehicle_idx.remove(vehicle_idx)
            self.to_depot_vehicle_idx.add(vehicle_idx)

        else:  # when the task is either pickup or delivery
            vehicle.status = VehicleStatus.ASSIGNED

            if 1 <= task_idx <= self.n:  # pickup
                pickup = self.pickups[task_idx]
                pickup.status = PickupStatus.ASSIGNED
                pickup.assigned_by = vehicle_idx
                task = pickup

                self.active_pickup_idx.remove(task_idx)
                self.assigned_pickup_idx.add(task_idx)

            else:  # delivery
                delivery = self.deliveries[task_idx]
                # assure whether the pickup is actually made by the current vehicle
                assert self.pickups[delivery.pickup_idx].assigned_by == vehicle_idx
                delivery.status = DeliveryStatus.ASSIGNED
                delivery.assigned_by = vehicle_idx
                task = delivery

                self.active_delivery_idx.remove(task_idx)
                self.assigned_delivery_idx.add(task_idx)

            vehicle.next_task = task
            vehicle.next_task_idx = task.idx

            # adjust "active vehicle idx"
            self.active_vehicle_idx.remove(vehicle_idx)
            self.assigned_vehicle_idx.add(vehicle_idx)

        vehicle.remaining_distance = calc_dist(vehicle.loc, vehicle.next_task.loc)

    def transit(self):
        assert len(self.get_idle_vehicle_indices()) == 0
        assert len(self.assigned_vehicle_idx) + len(self.to_depot_vehicle_idx) >= 1

        if len(self.assigned_vehicle_idx) == 0:  # all agents are returning to the depot
            dt = -1e10
            for vehicle_idx in list(self.to_depot_vehicle_idx):
                dt = max(dt, self.vehicles[vehicle_idx].remaining_distance)

            # simulate the "to-depot" vehicles
            for vehicle_idx in list(self.to_depot_vehicle_idx):
                _dt = min(self.vehicles[vehicle_idx].remaining_distance, dt)
                self.vehicles[vehicle_idx].travel(_dt, self)
            self.done = True
            self.time += dt
        else:
            dt = 1e10
            for vehicle_idx in list(self.assigned_vehicle_idx):
                dt = min(dt, self.vehicles[vehicle_idx].remaining_distance)

            # simulate the "assigned" vehicles
            for vehicle_idx in list(self.assigned_vehicle_idx):
                self.vehicles[vehicle_idx].travel(dt, self)

            # simulate the "to-depot" vehicles
            for vehicle_idx in list(self.to_depot_vehicle_idx):
                _dt = min(self.vehicles[vehicle_idx].remaining_distance, dt)
                self.vehicles[vehicle_idx].travel(_dt, self)

            self.time += dt
