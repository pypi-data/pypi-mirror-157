import numpy as np

from pypdp.engine.manager import PDPManager
from pypdp.utils.action_space import default_action_space
from pypdp.utils.generate_problem import get_uniform_problem
from pypdp.utils.observations import manager_observation
from pypdp.utils.rewards import makespan_reward


class PDPenv:

    def __init__(self,
                 m: int,
                 n: int = None,
                 problem: dict = None,
                 observation_func: callable = manager_observation,
                 reward_func: callable = makespan_reward,
                 action_space_func: callable = default_action_space,
                 verbose: bool = False):

        if problem is None:
            self.m = m  # number of vehicles
            self.n = n  # number of requests
            problem = get_uniform_problem(n, m)
        else:
            self.m = problem["num_vehicles"]
            self.n = problem["num_requests"]

        self.observation_func = observation_func
        self.reward_func = reward_func
        self.action_space_func = action_space_func
        self.verbose = verbose

        self.problem = problem
        self.manager = None
        self.event_index = None
        self.reset()

    def reset(self):
        self.manager = PDPManager(self.problem)
        self.event_index = 0
        obs = self.observation_func(self)
        return obs

    def target_agent_idx(self):
        return self.manager.target_vehicle_idx

    def step(self, action=None):
        if action is None:
            action = np.random.choice(self.get_action_space())
        assert action in self.get_action_space()

        task_idx = action
        self.manager.set_next_task(self.manager.target_vehicle_idx, task_idx)

        if self.verbose:
            print("[Event {}] | Vehicle {} is assigned {} ".format(self.event_index,
                                                                   self.manager.target_vehicle_idx,
                                                                   action))

        if len(self.manager.get_idle_vehicle_indices()) == 0:  # perform time simulation
            self.manager.transit()

        done = self.manager.done
        if not done:
            self.manager.set_target_vehicle()

        obs = self.observation_func(self)
        reward = self.reward_func(self)
        self.event_index += 1
        info = {
            'event_index': self.event_index,
            'time': self.manager.time
        }
        return obs, reward, done, info

    def get_action_space(self):
        return self.action_space_func(self)

    @classmethod
    def to_state(cls, state_dict):
        raise NotImplementedError

    @classmethod
    def from_state(cls, state_dict):
        raise NotImplementedError
