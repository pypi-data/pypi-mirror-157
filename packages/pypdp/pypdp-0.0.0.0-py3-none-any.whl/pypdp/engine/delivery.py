import numpy as np

from pypdp.engine.status import DeliveryStatus


class Delivery:

    def __init__(self,
                 idx: int,
                 loc: np.array):
        self.idx = idx
        self.loc = np.array(loc)
        self.status = DeliveryStatus.INACTIVE
        self.assigned_by = None
        self.pickup_idx = None

    def __repr__(self):
        msg = "Delivery {} | Coord: {} | Status: {}".format(self.idx, self.loc, self.status)
        return msg

    def state_dict(self):
        state_dict = {
            'status': self.status,
            'idx': self.idx,
            'loc': np.array(self.loc),
            'assigned_by': self.assigned_by,
            'pickup_idx': self.pickup_idx
        }
        return state_dict

    @classmethod
    def from_state_dict(cls, state_dict):
        pickup = cls(state_dict['idx'],
                     state_dict['loc'])
        pickup.status = state_dict['status']
        pickup.assigned_by = state_dict['assigned_by']
        pickup.pickup_idx = state_dict['pickup_idx']
        return pickup
