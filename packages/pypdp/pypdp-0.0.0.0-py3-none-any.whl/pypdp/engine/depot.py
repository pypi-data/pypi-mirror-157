import numpy as np

from pypdp.engine.status import DepotStatus


class Depot:
    def __init__(self,
                 idx: int,
                 loc: list):
        self.status = DepotStatus.ACTIVE
        self.idx = idx
        self.loc = np.array(loc)

    def state_dict(self):
        state_dict = {
            'idx': self.idx,
            'loc': np.array(self.loc)
        }
        return state_dict

    @classmethod
    def from_state_dict(cls, state_dict):
        depot = cls(idx=state_dict['idx'],
                    loc=state_dict['loc'])
        return depot
