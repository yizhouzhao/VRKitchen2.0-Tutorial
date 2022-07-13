import numpy as np
import torch
import os

from .utils import ReplayBuffer
from .humanoid_env import HumanoidEnv
from .SAC import SAC

class Trainer():
    def __init__(self, env: HumanoidEnv) -> None:
        # env
        self.env = env
        
        # buffer
        self.buf = ReplayBuffer(env.obs_dim, env.act_dim, args=None, max_size=int(1e6))
        self.env.buf = self.buf

        # policy
        self.policy = SAC(self.env.obs_dim, self.env.act_dim,
                          init_temperature=0.1,
                          alpha_lr=1e-4,
                          actor_lr=1e-4,
                          critic_lr=1e-4,
                          tau=0.005,
                          discount=0.99,
                          critic_target_update_freq=2,
                          args=None)
