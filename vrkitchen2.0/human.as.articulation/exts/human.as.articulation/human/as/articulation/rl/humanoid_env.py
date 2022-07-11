import gym
from gym import spaces
import numpy as np
import math
import carb
import omni

from omni.isaac.core.robots.robot_view import RobotView

from ..constants import humanoid_motor_effort


class HumanoidEnv(gym.Env):
    def __init__(self, prim_paths_expr = "/World/envs/*/humanoid/torso") -> None:
        super().__init__()

        # articulation
        self.robots =  RobotView("/World/envs/*/humanoid/torso") # sim.create_articulation_view("/World/envs/*/humanoid/torso") # 
        self.robot_indices = np.arange(self.robots.count, dtype=np.int32)
        
        # initialize
        self.robots.initialize()
        self.robot_original_joint_position = self.robots.get_joint_positions()
        self.robot_original_transform = self.robots.get_world_poses()

        # constants
        self.num_envs = len(self.robot_indices)

    
    def step(self, actions = None):
        """
        Step in RL
        """
        actions = 1.0 * np.random.uniform(-1, 1, (len(self.robot_indices), len(humanoid_motor_effort)))
        self.motor_efforts = np.array(humanoid_motor_effort, dtype = np.float)[None,...]

        actions = actions * self.motor_efforts 
        self.robots.set_joint_efforts(efforts = actions, indices = self.robot_indices)


    def reset_idx(self, env_ids):
        """
        Reset envs by indexes
        """
        self.robots.set_joint_positions(self.robot_original_joint_position[env_ids,...], self.robot_indices[env_ids,...])
        self.robots.set_joint_position_targets(self.robot_original_joint_position[env_ids,...], self.robot_indices[env_ids,...])
        
        self.robots.set_world_poses(self.robot_original_transform[0][env_ids,...], self.robot_original_transform[1][env_ids,...], self.robot_indices[env_ids,...]) 
        
