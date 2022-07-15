import asyncio

import omni.ext
import omni.ui as ui

import omni
import pxr 
import carb

import time
import numpy as np

import os, sys
sys.path.append(os.path.dirname(__file__))

from constants import *
from rl.robot_env import RobotEnv
from rl.utils import *
from rl.trainer import Trainer

# go to directory: vrkitchen2.0/human.as.articulation/exts/human.as.articulation/human/as/articulation
# start notebook from: /home/yizhou/.local/share/ov/pkg/isaac_sim-2022.1.0/jupyter_notebook.sh


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[human.as.articulation] MyExtension startup")

        self._is_stopped = True
        self._tensor_started = False
        self.dt_acc = 1.0

        self._window = ui.Window("human.as.articulation", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Button("Capsu test", clicked_fn=self.test_capsule)
                ui.Button("humanoid test 2", clicked_fn=self.test_smpl)
                ui.Button("Joint test 3", clicked_fn=self.test_joint)
                ui.Button("Joint test runtime 4", clicked_fn=self.test_joint_runtime)
                ui.Button("Test RL", clicked_fn=self.test_rl)
                ui.Button("Test RL 2", clicked_fn=self.test_rl2)
                
                

    def on_shutdown(self):
        print("[human.as.articulation] MyExtension shutdown")

    def test_capsule(self):
        print("test_capsule")
        
        from pxr import UsdGeom, Gf

        stage = omni.usd.get_context().get_stage()

        geom_path = "/World/Capsule"
        # UsdGeom.Capsule.Define(stage, geom_path)

        # capsule_bboxes =  omni.usd.get_context().compute_path_world_bounding_box(geom_path)

        # print("capsule_bboxes", capsule_bboxes)

        from .utils import generate_capsule

        generate_capsule(Gf.Vec3d(0,0,0), Gf.Vec3d(1,1,1), geom_path)

    def test_smpl(self):
        print("test_smpl")
        # from omni.usd import get_world_transform_matrix, get_local_transform_matrix
        from pxr import Gf, Sdf

        from .utils import generate_capsule

        stage = omni.usd.get_context().get_stage()

        stage.DefinePrim("/World/ihuman", "Xform")
        

        # import omni.anim.graph.core as ag

        # c = ag.get_character("/World/Character2")

        # t = carb.Float3(0, 0, 0)
        # q = carb.Float4(0, 0, 0, 1)
        # # c.get_world_transform(t, q)

        
        # c.get_joint_transform("f_avg_R_Hand", t, q)
        # print("t, q", t, q)

        pelvis_prim_path_str = "/World/smpl_f/f_avg_root/f_avg_root/f_avg_Pelvis"
        pelvis_prim = stage.GetPrimAtPath(pelvis_prim_path_str)

        root_joint_path_str = "/World/smpl_f/f_avg_root"
        root_joint_prim = stage.GetPrimAtPath(root_joint_path_str)

        joints = root_joint_prim.GetAttribute("joints").Get()
        bind_transforms = root_joint_prim.GetAttribute("bindTransforms").Get()

        # print("joints", len(joints), joints)
        # print("transforms", len(bind_transforms), bind_transforms)

        joint2trans = {}
        joint2parent = {}
        for joint, trans in zip(joints, bind_transforms):
            joint_name = joint.split("/")[-1]
            
            if joint_name not in joint2trans:
                joint2trans[joint_name] = trans
            if joint_name not in joint2parent:
                if "/" in joint:
                    parent_name = joint.split("/")[-2]
                    joint2parent[joint_name] = parent_name

            translate = trans.ExtractTranslation()

            # cube = stage.DefinePrim(f"/World/cubes/{joint_name}_cube", "Cube")
            # mat = Gf.Matrix4d().SetScale(0.02) * Gf.Matrix4d().SetTranslate(translate) 

            # omni.kit.commands.execute(
            #     "TransformPrimCommand",
            #     path=cube.GetPath().pathString,
            #     new_transform_matrix=mat,
            # )

            # generate capsule
            if joint_name in joint2parent:
                parent_name = joint2parent[joint_name]
                parant_translate = joint2trans[parent_name].ExtractTranslation()

                joint_xform = stage.DefinePrim(f"/World/ihuman/{parent_name}", "Xform")
                mat = Gf.Matrix4d().SetTranslate(parant_translate)

                omni.kit.commands.execute(
                    "TransformPrimCommand",
                    path=joint_xform.GetPath().pathString,
                    new_transform_matrix=mat,
                )


                generate_capsule(translate, parant_translate, f"/World/ihuman/{parent_name}_collision")

                # move 
                move_dict = {Sdf.Path(f"/World/ihuman/{parent_name}_collision"): Sdf.Path(f"/World/ihuman/{parent_name}/collision")}
                omni.kit.commands.execute("MovePrims", paths_to_move=move_dict,  on_move_fn=None)

                # mid_translate = (parant_translate + translate) / 2
                # print(joint_name, "mid\n", mid_translate)

                # set
                omni.physx.scripts.utils.setRigidBody(joint_xform, "", False)


        # print("joint2parent", joint2parent)
        # print("joint2trans", joint2trans)
        
    def test_joint(self):
        print("connect joint test")

        from pxr import Gf, Sdf, UsdPhysics, UsdGeom

        xfCache = UsdGeom.XformCache()

        stage = omni.usd.get_context().get_stage()
        joint_root_path_str = "/World/ihuman/joints"
        stage.DefinePrim(joint_root_path_str, "Xform")

        # pelvis prim
        # pelvis_prim = stage.GetPrimAtPath("/World/ihuman/f_avg_Pelvis")
        # component = UsdPhysics.FixedJoint.Define(stage, f"{joint_root_path_str}/pelvis")
        # component.CreateBody0Rel().SetTargets([])
        # component.CreateBody1Rel().SetTargets([pelvis_prim.GetPath()])
        from .utils import generate_d6_joint, generate_fixed_joint

        # TODO: enable
        component = generate_fixed_joint("/World/ihuman/f_avg_Pelvis", None, f"{joint_root_path_str}/pelvis")
        component.CreateJointEnabledAttr(False)


        generate_d6_joint("/World/ihuman/f_avg_R_Hip", "/World/ihuman/f_avg_Pelvis", f"{joint_root_path_str}/r_hip")
        

    def test_joint_runtime(self):
        print("joint run time test") 
        from pxr import UsdPhysics
        from .utils import generate_fixed_joint

        stage = omni.usd.get_context().get_stage()

        joint_root_path_str = "/World/ihuman/joints"

        c = UsdPhysics.Joint.Get(stage, f"{joint_root_path_str}/r_hip")
        c.CreateJointEnabledAttr(False)
        generate_fixed_joint("/World/ihuman/f_avg_R_Hip", f"/World/ihuman/f_avg_Pelvis", f"{joint_root_path_str}/runtime")
       
        
        
    def test_rl(self):
        print("test RL")

        self.trainer = Trainer(54, 21)


    def test_rl2(self):
        print("test rl20")

        self.timeline = omni.timeline.get_timeline_interface()
        stage = omni.usd.get_context().get_stage()

        # start env
        self.env = RobotEnv()


        self._setup_callbacks()
        self.timeline.set_looping(True)
        self.timeline.play()


# ----------------------------------------------------time----------------------------------------------

    def _setup_callbacks(self):
        stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_sub = stream.create_subscription_to_pop(self._on_timeline_event)
        # subscribe to Physics updates:
        self._physics_update_sub = omni.physx.get_physx_interface().subscribe_physics_step_events(self._on_physics_step)
        events = omni.physx.get_physx_interface().get_simulation_event_stream_v2()
        self._simulation_event_subscription = events.create_subscription_to_pop(self.on_simulation_event)

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.STOP):
            self._is_stopped = True
            self._tensor_started = False

            # !!!
            self._simulation_event_subscription = None
            self._physics_update_sub = None
            self._timeline_sub = None
        
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            self._is_stopped = False
    
    def _on_physics_step(self, dt):
        if not self._can_callback_physics_step():
            return

        # call user implementation
        self.on_physics_step(dt)


    def on_simulation_event(self, e):
        """
        This method is called on simulation events. See omni.physx.bindings._physx.SimulationEvent.
        """
        pass
        # print("on_simulation_event", e)
        
    def _can_callback_physics_step(self) -> bool:
        if self._is_stopped:
            return False

        if self._tensor_started:
            return True


        self._tensor_started = True

        # start env
        self.env.start()

        return True
    
    def on_physics_step(self, dt):
        """
        This method is called on each physics step callback, and the first callback is issued
        after the on_tensor_start method is called if the tensor API is enabled.
        """
        # self.dt_acc -= dt
        # if self.dt_acc > 0:
        #     return 
        
        # print("0.2 second passed")
        # self.dt_acc = 0.2

        # renew observation
        old_obs_buf = self.env.obs_buf.clone()
        # print("old_obs_buf", old_obs_buf.shape)

        action = self.trainer.sample_action(old_obs_buf)
        # print("action", action.shape, action)

        # print("step")
        self.env.step(action)
        self.env.compute_observations()

        new_obs_buf = self.env.obs_buf.clone()
        reward, done = self.env.compute_reward()

        # print("reward", reward.shape, "done", done.shape)
        self.trainer.buf.add_batch(old_obs_buf, action, new_obs_buf, reward, done)
        print("self.trainer.buf", self.trainer.buf.size)

        # train
        if self.trainer.buf.size > 50:
            self.trainer.train_debug()


        # handle bug
        if torch.isnan(old_obs_buf[:,0]).any():
            self.timeline.pause()

            async def stop_and_restart():

                self.timeline.pause()
                await asyncio.sleep(2.0)
                self.timeline.stop()
                await asyncio.sleep(1.0)
                self.test_rl2()

            # asyncio.ensure_future(stop_and_restart())

        # need to reset
        if torch.sum(done) >= 1:
            env_ids = []
            for i in range(len(done)):
                if done[i] > 0:
                    env_ids.append(i)

            # self.env.reset_idx(env_ids)

            for i in env_ids:
                if i in self.env.active_ids:
                    self.env.active_ids.remove(i)
                    self.env.reset_count_down[i] = 10
        
        # update reset
        now_reset_env_ids = []
        for key in list(self.env.reset_count_down.keys()):
            self.env.reset_count_down[key] -= 1
            if self.env.reset_count_down[key] <= 0:
                self.env.active_ids.append(key)
                now_reset_env_ids.append(key)
                del self.env.reset_count_down[key]

        if len(now_reset_env_ids):
            self.env.reset_idx(now_reset_env_ids)

            # self.env.robots.post_reset()


