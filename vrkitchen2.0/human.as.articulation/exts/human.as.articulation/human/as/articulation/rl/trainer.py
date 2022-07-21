from re import L
import numpy as np
import torch
import os

from rl.utils import ReplayBuffer
from rl.SAC import SAC

# Writer will output to ./runs/ directory by default
import torch
from torch.utils.tensorboard import SummaryWriter


class Trainer():
    def __init__(self, obs_dim, act_dim, use_tensorboard = True):
        self.obs_dim = obs_dim
        self.act_dim = act_dim

        self.env = None
        self.total_training_step = 0
        
        # tensorboard
        self.use_tensorboard = use_tensorboard
        self.writer = SummaryWriter() if use_tensorboard else None

        # buffer
        self.buf = ReplayBuffer(obs_dim, act_dim, args=None, max_size=int(1e5))

        # policy
        self.policy = SAC(obs_dim, act_dim,
                          init_temperature=0.1,
                          alpha_lr=1e-3,
                          actor_lr=1e-3,
                          critic_lr=1e-3,
                          tau=0.005,
                          discount=0.99,
                          critic_target_update_freq=2,
                          args=None)

        self.device = self.policy.device
        self.warm_up_steps = 1000
    
    def add_env(self, env):
        self.env = env

    def sample_action(self, current_obs):
         with torch.no_grad():
            state = current_obs.to(self.device)
            # print("state", state.shape)
            mu, pi, _, _ = self.policy.actor(state, compute_log_pi=False)
            return pi.cpu().data
            
    def train(self, batch_size = 16):
        self.total_training_step += 1
        self.policy.train(self.buf, batch_size)

    def write_summary(self):
        self.writer.add_scalar('Loss/reward_mean', torch.mean(self.env.reward_buf), \
            self.total_training_step)
        self.writer.add_scalar('Loss/reward_max', torch.max(self.env.reward_buf), \
            self.total_training_step)
    