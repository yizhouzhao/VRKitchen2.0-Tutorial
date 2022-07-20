import gym
from gym import spaces
import numpy as np
import torch
import carb
import omni
from PIL import Image

from omni.isaac.core.robots.robot_view import RobotView
from omni.isaac.core import World, SimulationContext
from omni.isaac.synthetic_utils import SyntheticDataHelper

from constants import humanoid_motor_effort
from rl.torch_utils import *
from rl.torch_jit_utils import *


class RobotEnv(gym.Env):
    def __init__(self, 
            prim_paths_expr = "/World/envs/*/humanoid/torso",
            motor_efforts = humanoid_motor_effort,
            backend = "torch",
            device = torch.device("cpu")
        ):
        super().__init__()

        self.prim_paths_expr = prim_paths_expr
        self.backend = backend
        self.device = device
        self.motor_efforts =motor_efforts

        # stats
        # self.observation_space = spaces.Box(np.ones(self.num_obs) * -np.Inf, np.ones(self.num_obs) * np.Inf, dtype=np.float32)
        # self.action_space = spaces.Box(np.ones(self.num_actions) * -1., np.ones(self.num_actions) * 1., dtype=np.float32)

        # reward
        self.heading_weight = 0.5
        self.up_weight = 0.1
        self.termination_height = 0.8

        # render
        self._sd_helper = SyntheticDataHelper()
        self._viewport_window = omni.kit.viewport_legacy.get_default_viewport_window()
        self._sd_helper.initialize(sensor_names=["rgb"], viewport=self._viewport_window)
    
    def render_img(self):
        gt = self._sd_helper.get_groundtruth(
            [
                "rgb",
            ],
            self._viewport_window,
            verify_sensor_init=False,
        )

        return gt["rgb"]

    def allocate_buffers(self):
        """Allocate the observation, states, etc. buffers.

        These are what is used to set observations and states in the environment classes which
        inherit from this one, and are read in `step` and other related functions.

        """
        # allocate buffers
        # self.obs_buf = torch.zeros(
        #     (self.num_envs, self.num_obs), device=self.device, dtype=torch.float)
        # self.states_buf = torch.zeros(
        #     (self.num_envs, self.num_states), device=self.device, dtype=torch.float)
        self.reward_buf = torch.zeros(
            self.num_envs, device=self.device, dtype=torch.float)
        self.reset_buf = torch.zeros(
            self.num_envs, device=self.device, dtype=torch.long)
        self.progress_buf = torch.zeros(
            self.num_envs, device=self.device, dtype=torch.long)


    def start(self):
        # simulation context
        self.simlation_context = SimulationContext(backend=self.backend, device=self.device)
        print("simlation context", SimulationContext.instance().backend, SimulationContext.instance().device)

        # articulation
        self.robots =  RobotView(self.prim_paths_expr) # sim.create_articulation_view("/World/envs/*/humanoid/torso") # 
        self.robot_indices = self.robots._backend_utils.convert(np.arange(self.robots.count, dtype=np.int32), self.device)
        self.num_envs = len(self.robot_indices)

        print("num_envs", self.num_envs)
        
        self.active_ids = [i for i in range(self.num_envs)]
        self.reset_count_down = {}

        # initialize
        self.robots.initialize()
        self.robot_states = self.robots.get_world_poses()
        self.dof_pos = self.robots.get_joint_positions()

        self.initial_dof_pos = self.dof_pos.clone() # TODO: check numpy?
        self.dof_vel = self.robots.get_joint_velocities()
        self.initial_dof_vel = self.dof_vel.clone()

        # self.dof_force = self.robots._physics_view.get_force_sensor_forces()

        # joint motor effort 
        self.motor_efforts = self.robots._backend_utils.convert(self.motor_efforts, self.device)
        self.robots.set_max_efforts(self.motor_efforts.expand(self.num_envs, -1))
        self.robots._physics_view.set_dof_max_velocities(100 * torch.ones((self.num_envs, 21)), self.robot_indices)
        
        self.robots.set_solver_position_iteration_counts(32 * torch.ones(self.num_envs))
        self.robots.set_solver_velocity_iteration_counts(32 * torch.ones(self.num_envs))
        
        # get joint limit
        self.joint_lower_limit = self.robots.get_dof_limits()[0,:,0]
        self.joint_upper_limit = self.robots.get_dof_limits()[0,:,1]
        
        # constants
        self.dt = 1 / 30
        self.potentials = to_torch([-1000./self.dt], device=self.device).repeat(self.num_envs)
        self.prev_potentials = self.potentials.clone()
        self.angular_velocity_scale = 0.1
        self.dof_vel_scale = 0.1
        self.contact_force_scale = 0.01

        # buffers
        self.allocate_buffers()
        # self.compute_observations()

        # shape
        self.action_shape = self.robots._default_joints_state.positions.shape
        print("default joint state", self.robots._default_joints_state.positions, self.robots._default_joints_state.velocities, \
            self.robots._default_joints_state.efforts)
     
    def compute_observations(self):
        torso_position, torso_rotation  = self.robots.get_world_poses()

        # WXYZ -> XYZW
        index = torch.LongTensor([1, 2, 3, 0])
        torso_rotation = torch.index_select(torso_rotation, 1, index)

        root_velocity = self.robots.get_velocities()
        velocity = root_velocity[:, 0:3]
        ang_velocity = root_velocity[:, 3:]

        # print("torso_position", torso_position, "torso_rotation", torso_rotation, \
        #     #"velocity", velocity.shape, "ang_velocity", ang_velocity.shape,
        #     )

        torso_quat = quat_mul(torso_rotation, self.inv_start_rot)
        up_vec = get_basis_vector(torso_quat, self.basis_vec1).view(-1, 3)
        heading_vec = get_basis_vector(torso_quat, self.basis_vec0).view(-1, 3)
        up_proj = up_vec[:, self.up_axis_idx]
        heading_proj = heading_vec[:, 0]
        

        # FIXME: up index change
        vel_loc, angvel_loc, roll, pitch, yaw, angle_to_target = compute_rot(
            torso_quat, velocity, ang_velocity, self.targets, torso_position)

        # print("torso_quat", torso_quat, "up_vec", up_vec, "heading_vec", heading_vec)
        #  "vel_loc", vel_loc, "angvel_loc", angvel_loc, "roll, pitch, yaw", roll, pitch, yaw, \
        #     "up_proj", up_proj, "heading_proj", heading_proj)

        roll = normalize_angle(roll).unsqueeze(-1)
        yaw = normalize_angle(yaw).unsqueeze(-1)
        pitch = normalize_angle(pitch).unsqueeze(-1)
        
        angle_to_target = normalize_angle(angle_to_target).unsqueeze(-1)

        # joint positions and velocities
        dof_pos = self.robots.get_joint_positions()
        dof_vel = self.robots.get_joint_velocities()

        
        # print("dof_pos", dof_pos.shape, "dof_vel", dof_vel.shape)


        # obs_buf shapes: 1, 3, 3, 1, 1, 1, 
        # 1, 1, num_dofs (21), num_dofs (21), 
        # num_acts (21)
        obs = torch.cat((torso_position[:, 1].view(-1, 1), vel_loc, angvel_loc * self.angular_velocity_scale,
                    yaw, pitch, roll, up_proj.unsqueeze(-1), heading_proj.unsqueeze(-1), \
                    dof_pos, dof_vel * self.dof_vel_scale, \
                    # self.actions, \
                    ), dim = 1)
        
        # record useful observations
        self.obs_buf = obs
        self.up_proj = up_proj
        self.heading_proj = heading_proj

    def compute_reward(self):

        # reward from the direction headed
        heading_weight_tensor = torch.ones_like(self.heading_proj) * self.heading_weight
        heading_reward = torch.where(self.heading_proj > 0.8, heading_weight_tensor, self.heading_weight * self.heading_proj / 0.8)

        # reward for being upright
        up_reward = torch.zeros_like(heading_reward)
        up_reward = torch.where(self.up_proj > 0.93, up_reward + self.up_weight, up_reward)

        # TODO: reward design
        total_reward = up_reward + heading_reward 

        # print("heading_proj", self.heading_proj, heading_reward)
        # print("up_proj", self.up_proj, up_reward)

        self.reward_buf += total_reward

        # reset agents
        reset = torch.where(self.obs_buf[:, 0] < self.termination_height, torch.ones_like(self.reset_buf), self.reset_buf)
        reset = torch.where(self.progress_buf >= 1000 - 1, torch.ones_like(self.reset_buf), reset)
        reset = torch.where(self.progress_buf >= 1000 - 1, torch.ones_like(self.reset_buf), reset)
        
        # if torch.isnan(self.obs_buf[:, 0]).any():
        #     reset = torch.ones_like(self.reset_buf)

        # print("reset?", self.obs_buf[:, 0], reset)
        return total_reward, reset
    
    def compute_active_ids(self):
        for key in list(self.reset_count_down.keys()):
            self.reset_count_down[key] -= 1
            if self.reset_count_down[key] <= 0:
                self.active_ids.append(key)
                del self.reset_count_down[key]

    def step(self, actions):
        """
        Step in RL
        """
        # update progress
        self.progress_buf += 1
        # self.randomize_buf += 1

        # self.compute_active_ids()
        # take action
        if actions is None: # random policy
            # if self.backend == "numpy":
            #     self.actions = 1.0 * np.random.uniform(-1, 1, (len(self.active_ids), len(humanoid_motor_effort)))
            # else: # torch
            self.actions = 2 * torch.rand(self.num_envs, len(self.motor_efforts)) - 1
            self.actions = self.actions.to(self.device)
        else:
            self.actions = actions

        # print("actions", self.actions.shape, self.actions)
        self.actions = self.actions * self.motor_efforts 
        
        # print("active_ids", self.active_ids) 
        # print("action", self.actions)
        if len(self.active_ids) > 0:
            self.robots.set_joint_efforts(efforts = self.actions[self.active_ids, ...], indices = self.active_ids)
        # if len(self.reset_count_down) > 0:
        #     self.robots.set_joint_efforts(efforts = torch.zeros((len(self.reset_count_down), 21)), indices = list(self.reset_count_down.keys()))



    def reset_idx(self, env_ids):
        """
        Reset envs by indexes
        """
        # indices = self.robot_indices[env_ids,...].tolist()
        # print("indices", indices, self.robots._default_state.positions.shape, self.robots._default_state.positions[env_ids,...].shape)
        # return
        # print("init_joint_states", self.initial_dof_pos, self.initial_dof_vel)
        # self.robots.set_joint_positions(torch.zeros_like(self.initial_dof_pos), self.robot_indices[env_ids,...])
        # self.robots.set_joint_position_targets(self.initial_dof_pos[env_ids,...], self.robot_indices[env_ids,...])
        # self.robots.set_joint_velocities(torch.zeros_like(self.initial_dof_vel), indices = self.robot_indices[env_ids,...])
        # self.robots.set_joint_efforts(efforts = torch.zeros_like(self.initial_dof_vel), indices = self.robot_indices)

        self.robots.set_world_poses(self.robots._default_state.positions[env_ids,...], self.robots._default_state.orientations[env_ids,...], indices=env_ids)
        self.robots.set_joint_positions(self.robots._default_joints_state.positions[env_ids,...], indices=env_ids)
        self.robots.set_joint_position_targets(self.robots._default_joints_state.positions[env_ids,...], indices=env_ids)
        
        
        self.robots.set_joint_velocities(self.robots._default_joints_state.velocities[env_ids,...], indices=env_ids)
        self.robots.set_joint_velocity_targets(self.robots._default_joints_state.velocities[env_ids,...], indices=env_ids)
        
        self.robots.set_joint_efforts(self.robots._default_joints_state.efforts[env_ids,...], indices=env_ids)
        self.robots.set_gains(kps=self.robots._default_kps[env_ids,...], kds=self.robots._default_kds[env_ids,...], indices=env_ids)
        
        # temp_damping = self.robots._physics_view.get_dof_dampings()
        # print("temp_damping", temp_damping)
        # self.robots._physics_view.set_dof_dampings(10 * temp_damping[env_ids,...], self.robot_indices[env_ids,...])
        
        # self.robots.set_world_poses(self.robot_states[0][env_ids,...], self.robot_states[1][env_ids,...], self.robot_indices[env_ids,...]) 
        self.progress_buf[env_ids] = 0
        self.reset_buf[env_ids] = 0
        self.reward_buf[env_ids] = 0


    def reset(self):
        """
        reset all
        """
        envs_ids = [i for i in range(self.robot_indices)]
        self.reset_idx(envs_ids)

