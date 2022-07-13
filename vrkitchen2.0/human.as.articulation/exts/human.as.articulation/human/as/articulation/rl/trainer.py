import numpy as np
import torch
import os

from .utils import ReplayBuffer
from .humanoid_env import HumanoidEnv
from .SAC import SAC

class Trainer():
    def __init__(self, obs_dim, act_dim) -> None:
        self.obs_dim = obs_dim
        self.act_dim = act_dim
        
        # buffer
        self.buf = ReplayBuffer(obs_dim, act_dim, args=None, max_size=int(1e6))

        # policy
        self.policy = SAC(obs_dim, act_dim,
                          init_temperature=0.1,
                          alpha_lr=1e-4,
                          actor_lr=1e-4,
                          critic_lr=1e-4,
                          tau=0.005,
                          discount=0.99,
                          critic_target_update_freq=2,
                          args=None)

        self.device = self.policy.device
        self.warm_up_steps = 100

    def sample_action(self, current_obs):
         with torch.no_grad():
            state = current_obs.to(self.device)
            # print("state", state.shape)
            mu, pi, _, _ = self.policy.actor(state, compute_log_pi=False)
            return pi.cpu().data
            
    
    def train_debug(self):
        self.policy.train(self.buf, 16)