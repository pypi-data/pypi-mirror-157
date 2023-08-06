from enum import Enum


class DepotStatus(Enum):
    ACTIVE = 0


class PickupStatus(Enum):
    ACTIVE = 1  # Not visited/assigned to a vehicle
    ASSIGNED = 2  # assigned to some vehicle; the assigned vehicle is about to leave the tour/ or on the tour
    COMPLETED = 3  # already visited


class DeliveryStatus(Enum):
    INACTIVE = 4  # corresponding pickup is not made
    ACTIVE = 5  # corresponding pickup is made and ready to be visited
    ASSIGNED = 6  # a vehicle is on transit
    COMPLETED = 7  # delivery is done.


class VehicleStatus(Enum):
    ACTIVE = 8  # ready to be assigned
    ASSIGNED = 9  # in transit
    TO_DEPOT = 10  # in depot transit
    COMPLETED = 11  # already return to the depot
