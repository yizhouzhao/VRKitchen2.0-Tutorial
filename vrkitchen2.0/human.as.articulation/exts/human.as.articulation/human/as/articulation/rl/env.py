# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import gym
from gym import spaces
import numpy as np
import math
import carb
import omni

import asyncio

class JetBotEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        skip_frame=1,
        physics_dt=1.0 / 60.0,
        rendering_dt=1.0 / 60.0,
        max_episode_length=1000,
        seed=0,
        headless=True,
    ) -> None:
        # from omni.isaac.kit import SimulationApp

        # self.headless = headless
        # self._simulation_app = SimulationApp({"headless": self.headless, "anti_aliasing": 0})
        self._skip_frame = skip_frame
        self._dt = physics_dt * self._skip_frame
        self._max_episode_length = max_episode_length
        self._steps_after_reset = int(rendering_dt / physics_dt)

        from omni.isaac.core import World
        from omni.isaac.wheeled_robots.robots import WheeledRobot
        from omni.isaac.core.objects import VisualCuboid
        from omni.isaac.core.utils.nucleus import get_assets_root_path
        from omni.isaac.core.utils.stage import create_new_stage_async, update_stage_async

        # async def start_world():
        #     print("start new world")
        World.clear_instance()
        if World.instance() is None:
            print("start new world 2")
            # await create_new_stage_async()
            self._my_world = World(physics_dt=physics_dt, rendering_dt=rendering_dt, stage_units_in_meters=1.0)
        else:
            self._my_world = World.instance()

        self._my_world.scene.add_default_ground_plane()
        # await update_stage_async()

        timeline = omni.timeline.get_timeline_interface()
        timeline.play()

        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
            return

        jetbot_asset_path = assets_root_path + "/Isaac/Robots/Jetbot/jetbot.usd"
        self.jetbot = self._my_world.scene.add(
            WheeledRobot(
                prim_path="/jetbot",
                name="my_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.0, 0.020]),
                orientation=np.array([1.0, 0.0, 0.0, 0.0]),
            )
        )
            
        # await update_stage_async()
        self.goal = self._my_world.scene.add(
            VisualCuboid(
                prim_path="/new_cube_1",
                name="visual_cube",
                position=np.array([0.60, 0.30, 0.025]),
                size=np.array([0.05, 0.05, 0.05]),
                color=np.array([1.0, 0, 0]),
            )
        )
        print("world setup complete")
        
        # asyncio.ensure_future(start_world())       
       
        self.seed(seed)
        self.sd_helper = None
        self.viewport_window = None
        # self._set_camera()
        self.reward_range = (-float("inf"), float("inf"))
        gym.Env.__init__(self)
        self.action_space = spaces.Box(low=-10.0, high=10.0, shape=(2,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=255, shape=(128, 128, 3), dtype=np.uint8)
        return

    def get_dt(self):
        return self._dt

    def step(self, action):
        previous_jetbot_position, _ = self.jetbot.get_world_pose()
        for i in range(self._skip_frame):
            from omni.isaac.core.utils.types import ArticulationAction

            self.jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=action * 10.0))
            self._my_world.step(render=False)
        observations = self.get_observations()
        info = {}
        done = False
        if self._my_world.current_time_step_index - self._steps_after_reset >= self._max_episode_length:
            done = True
        goal_world_position, _ = self.goal.get_world_pose()
        current_jetbot_position, _ = self.jetbot.get_world_pose()
        previous_dist_to_goal = np.linalg.norm(goal_world_position - previous_jetbot_position)
        current_dist_to_goal = np.linalg.norm(goal_world_position - current_jetbot_position)
        reward = previous_dist_to_goal - current_dist_to_goal
        return observations, reward, done, info

    def reset(self):
        self._my_world.reset()
        # randomize goal location in circle around robot
        alpha = 2 * math.pi * np.random.rand()
        r = 1.00 * math.sqrt(np.random.rand()) + 0.20
        self.goal.set_world_pose(np.array([math.sin(alpha) * r, math.cos(alpha) * r, 0.025]))
        observations = self.get_observations()
        return observations

    def get_observations(self):
        self._my_world.render()
        # wait_for_sensor_data is recommended when capturing multiple sensors, in this case we can set it to zero as we only need RGB
        gt = self.sd_helper.get_groundtruth(
            ["rgb"], self.viewport_window, verify_sensor_init=False, wait_for_sensor_data=0
        )
        return gt["rgb"][:, :, :3]

    def render(self, mode="human"):
        return

    def close(self):
        self._simulation_app.close()
        return

    def seed(self, seed=None):
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        np.random.seed(seed)
        return [seed]

    def _set_camera(self):
        import omni.kit
        from pxr import UsdGeom
        from omni.isaac.synthetic_utils import SyntheticDataHelper
        from omni.isaac.core.utils.stage import get_current_stage

        camera_path = "/jetbot/chassis/rgb_camera/jetbot_camera"
        camera = UsdGeom.Camera(get_current_stage().GetPrimAtPath(camera_path))
        camera.GetClippingRangeAttr().Set((0.01, 10000))
        if self.headless:
            viewport_handle = omni.kit.viewport_legacy.get_viewport_interface()
            viewport_handle.get_viewport_window().set_active_camera(str(camera_path))
            viewport_window = viewport_handle.get_viewport_window()
            self.viewport_window = viewport_window
            viewport_window.set_texture_resolution(128, 128)
        else:
            viewport_handle = omni.kit.viewport_legacy.get_viewport_interface().create_instance()
            new_viewport_name = omni.kit.viewport_legacy.get_viewport_interface().get_viewport_window_name(
                viewport_handle
            )
            viewport_window = omni.kit.viewport_legacy.get_viewport_interface().get_viewport_window(viewport_handle)
            viewport_window.set_active_camera(camera_path)
            viewport_window.set_texture_resolution(128, 128)
            viewport_window.set_window_pos(1000, 400)
            viewport_window.set_window_size(420, 420)
            self.viewport_window = viewport_window
        self.sd_helper = SyntheticDataHelper()
        self.sd_helper.initialize(sensor_names=["rgb"], viewport=self.viewport_window)
        self._my_world.render()
        self.sd_helper.get_groundtruth(["rgb"], self.viewport_window)
        return
