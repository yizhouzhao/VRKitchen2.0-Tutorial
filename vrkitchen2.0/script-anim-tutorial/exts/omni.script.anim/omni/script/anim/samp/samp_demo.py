import omni
from pxr import Gf, UsdGeom
import carb

import asyncio
import numpy as np

import omni.anim.graph.core as ag

from .time_series import *
from .cuboid_map import *
from .actor import Actor
from .sampnn import SAMPNN
from .controller import Controller


from ..smplx.constants import *
from ..smplx.utils import *


class SAMP_Demo:
    def __init__(self, smplx_prim_path = "/World/smplx") -> None:
        
        # get utility
        self.prim_path_str = smplx_prim_path
        self.stage = omni.usd.get_context().get_stage()
        self.timeline = omni.timeline.get_timeline_interface()
        self.xfCache = UsdGeom.XformCache()

        # get character
        self.prim = self.stage.GetPrimAtPath(self.prim_path_str)
        self.character = None # init at runtime

        # get network
        self.model = SAMPNN()

        # get actor
        self.actor = Actor()

        # controller
        self.controlloer = Controller()

        # geometry
        self.InteractionSmoothing = 0.9


    def _setup_callbacks(self):
        stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_subscription = stream.create_subscription_to_pop(self._on_timeline_event)

        self._appwindow = omni.appwindow.get_default_app_window()
        self._input = carb.input.acquire_input_interface()
        self._keyboard = self._appwindow.get_keyboard()
        self._sub_keyboard = self._input.subscribe_to_keyboard_events(self._keyboard, self._sub_keyboard_event)

    def _sub_keyboard_event(self, event, *args, **kwargs):
        # if (
        #     event.type == carb.input.KeyboardEventType.KEY_PRESS
        #     or event.type == carb.input.KeyboardEventType.KEY_REPEAT
        #     ):
        #     print("event input", event.input)
        #     # increment
        #     if event.input == carb.input.KeyboardInput.W:
        #         print("Get key board input: W")
        #         self.character =  ag.get_character("/World/smplx")
        #         pos = carb.Float3(0.0, 0.0, 0.0)
        #         rot = carb.Float4(0.0, 0.0, 0.0, 0.0)
        #         self.character.get_world_transform(pos, rot)

        #         print("pos, rot", pos, rot)
                
        #         pos[2] += 0.1
        #         self.character.set_world_transform(pos, rot)
            
        
        self.controlloer.handle_keyboard_event(event)


    def _on_timeline_event(self, e):
        """
        set up timeline event
        """
        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            self.character = ag.get_character("/World/smplx")

        if e.type == int(omni.timeline.TimelineEventType.STOP):
            self._input.unsubscribe_to_keyboard_events(self._keyboard, self._sub_keyboard)
            self._timeline_subscription = None

    def Setup(self):
        # geo
        self.Geometry = CuboidMap([8, 8, 8])

        # series
        self.TimeSeries = TimeSeries(6,6,1.0,1.0,5)
        self.RootSeries = Root(self.TimeSeries)
        self.StyleSeries = Style(self.TimeSeries, ["Idle", "Walk", "Run", "Sit", "Liedown"])
        self.GoalSeries = Goal(self.TimeSeries, ["Idle", "Walk", "Run", "Sit", "Liedown"])
        self.ContactSeries = Contact(self.TimeSeries, [ "right_hip", "right_wrist", "left_wrist", "right_foot", "left_foot"])

        print("samples and data", len(self.TimeSeries.Samples), len(self.TimeSeries.Data))

        root_mat = self.xfCache.GetLocalToWorldTransform(self.prim) # reflect????????????????????
        root_mat = Gf.Matrix4f(root_mat)
        self.Geometry.Pivot = Gf.Matrix4f(root_mat)

        for i in range(len(self.TimeSeries.Samples)):
            self.RootSeries.Transformations[i] = Gf.Matrix4f(root_mat)
        
            if self.StyleSeries.Styles:
                self.StyleSeries.Values[i][0] = 1

            if self.GoalSeries.Actions:
                self.GoalSeries.Values[i][0] = 1  

            self.GoalSeries.Transformations[i] = Gf.Matrix4f(root_mat)
            self.Geometry.References.append(root_mat.ExtractTranslation())
    
        # PosePrediction = new Vector3[Actor.Bones.Length];
        # RootPrediction = new Matrix4x4[7];
        # GoalPrediction = new Matrix4x4[7];



    def Start(self):
        
        async def Updates():
            self.timeline.stop()
            self.timeline.set_current_time(0.0)
            self.timeline.set_auto_update(False)
            self.timeline.set_looping(False)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            self.timeline.play()
            
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            for time in range(30):
                self.timeline.forward_one_frame()
                current_frame_code = self.timeline.get_current_time() * self.stage.GetTimeCodesPerSecond()
                print("time: ", self.stage.GetTimeCodesPerSecond(), current_frame_code)

                if time == 0:
                    self.SetIdlePose()
                    self.Setup()
                else:
                    self.Feed()
                

                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()

        asyncio.ensure_future(Updates())
    

    def SetIdlePose(self):
        """
        Set idle pose as init for the character
        """
        assert self.timeline and self.timeline.is_playing()

        self.character =  ag.get_character("/World/smplx")

        trans, quats = generate_trans_and_rots_for_pose_provider(idle_joint2info)
        for jj, t in enumerate(trans):
            self.character.set_variable("poses", trans)
            self.character.set_variable("rots", quats)

    def Default(self):
        """
        Handle default controllor action
        """
        # TODO: handle ProjectionActive
        if False:
            pass
        else:
            print("ApplyDynamicGoal:  TimeSeries.Pivot", self.TimeSeries.Pivot)

        move_val = self.controlloer.QueryMove()
        turn_val = 0
        print(("move_val, turn_val: ", move_val, turn_val))

        root_mat = Gf.Matrix4f(self.RootSeries.Transformations[self.TimeSeries.Pivot])
        self.ApplyDynamicGoal(root_mat, Gf.Vec3f(*move_val), turn_val)

        self.Geometry.Generate()
        self.Geometry.Sense(root_mat, Gf.Vec3f(0), self.InteractionSmoothing)

    def ApplyDynamicGoal(self, root, move, turn, actions = None):
        """
        Apply user controlled goal
        """
        len_sample = len(self.TimeSeries.Samples) 
        positions_blend = [Gf.Vec3f(0.0)] * len_sample
        directions_blend = [Gf.Vec3f(0.0)]  * len_sample

        time_metric = 2.0
        for i in range(len_sample):
            weight = ((i + 1.0) / len_sample) ** 0.5
            bias_pos = 1.0 - (1.0 - weight) ** 0.75
            bias_dir = 1.0 - (1.0 - weight) ** 0.75
            directions_blend = Gf.Vec3f(-1, 0, 0) # ????????????????
            if i == 0:
                v1 = self.GoalSeries.Transformations[i + 1].ExtractTranslation() - self.GoalSeries.Transformations[i].ExtractTranslation()
                v2 = time_metric / (len_sample - 1) * move
                positions_blend[i] = root.ExtractTranslation() + Gf.Lerp(bias_pos, v1, v2)
            else:
                v1 = self.GoalSeries.Transformations[i].ExtractTranslation() - self.GoalSeries.Transformations[i - 1].ExtractTranslation()
                v2 = time_metric / (len_sample - 1) * move
                positions_blend[i] = positions_blend[i - 1] + Gf.Lerp(bias_pos, v1, v2)

            # print("positions_blend: ", positions_blend)

        for i in range(len_sample):
            pos = Gf.Lerp(self.UserControl, self.GoalSeries.Transformations[i].ExtractTranslation(), positions_blend[i])
            self.GoalSeries.Transformations[i].SetTranslateOnly(pos)

            # rot = Gf.Slerp


    def Feed(self):
        """
        Feed information into Neural network
        """
        assert self.timeline and self.timeline.is_playing()
        root_mat = Gf.Matrix4f(self.RootSeries.Transformations[self.TimeSeries.Pivot])

        print("root_mat", root_mat)
        
        # control
        self.UserControl = self.controlloer.PoolUserControl()
        self.NetworkControl = self.controlloer.PoolNetworkControl()

        self.Default()

        # Feed input to NN
        self.model.reset_input()
        joint2mat = get_trans_and_rots_for_pose_provider()

        # Input Bone Positions / Velocities
        for i, joint in enumerate(joint2mat):
            bone = self.actor.Bones[i]
            assert joint == bone.name, f"joint name: {joint} and bone name {bone.name} don't match"

            mat = joint2mat[joint]
            bone.transform = mat  
            
            m = mat * root_mat.GetInverse() # relative to root

            rel_pos = m.ExtractTranslation() 
            rel_forward_dir = m.GetRow(2)
            rel_up_dir = m.GetRow(1)
            self.model.x.extend([rel_pos[0], rel_pos[1], rel_pos[2]])
            self.model.x.extend([rel_forward_dir[0], rel_forward_dir[1], rel_forward_dir[2]])
            self.model.x.extend([rel_up_dir[0], rel_up_dir[1], rel_up_dir[2]])
            self.model.x.extend(bone.velocity.copy())

        print("Pivot Bone Positions / Velocities :", len(self.model.x))
        # print("self.model.x", self.model.x)

        # Input Inverse Bone Positions
        for i, joint in enumerate(joint2mat):
            root_series_transform_last = Gf.Matrix4f(self.RootSeries.Transformations[-1])
            rel_pos = (joint2mat[joint] * root_series_transform_last.GetInverse()).ExtractTranslation()
            self.model.x.extend([rel_pos[0], rel_pos[1], rel_pos[2]])

        print("Pivot Inverse Bone Positions :", len(self.model.x))
        # print("self.model.x", self.model.x)

        # Input Trajectory Positions / Directions / Velocities / Styles
        for i in range(self.TimeSeries.keycount):
            sample = self.TimeSeries.Samples[i * self.TimeSeries.Resolution]
            root_series_transform = self.RootSeries.Transformations[sample.index]
            m = root_series_transform * root_mat.GetInverse()
            rel_pos = m.ExtractTranslation()
            rel_forward_dir = m.GetRow(2)
            self.model.x.extend([rel_pos[0], rel_pos[2]])
            self.model.x.extend([rel_forward_dir[0], rel_forward_dir[2]])
            self.model.x.extend(self.StyleSeries.Values[sample.index])

            # print("sample: ", sample.index, rel_pos, rel_forward_dir, self.StyleSeries.Values[sample.index])
        
        print("Pivot Trajectory Positions / Directions / Velocities / Styles :", len(self.model.x))
        # print("self.model.x", self.model.x)
        
        # Input Contacts
        self.model.x.extend(self.ContactSeries.Values[self.TimeSeries.Pivot])

        print("Pivot Inverse Input Contacts :", len(self.model.x))
        # print("self.model.x", self.model.x)

        # Input Inverse Trajectory Positions 
        for i in range(self.TimeSeries.keycount):
            sample = self.TimeSeries.Samples[i * self.TimeSeries.Resolution]

            m = self.RootSeries.Transformations[sample.index] * (self.GoalSeries.Transformations[self.TimeSeries.Pivot]).GetInverse()
            rel_pos = m.ExtractTranslation()
            rel_forward_dir = m.GetRow(2)
            self.model.x.extend([rel_pos[0], rel_pos[2]])
            self.model.x.extend([rel_forward_dir[0], rel_forward_dir[2]])

        print("Pivot Inverse Trajectory Positions :", len(self.model.x))
        # print("self.model.x", self.model.x)

        # Input Goals
        for i in range(self.TimeSeries.keycount):
            sample = self.TimeSeries.Samples[i * self.TimeSeries.Resolution]
            m = self.GoalSeries.Transformations[sample.index] * root_mat.GetInverse()
            rel_pos = m.ExtractTranslation()
            rel_forward_dir = m.GetRow(2)
            self.model.x.extend([rel_pos[0], rel_pos[1], rel_pos[2]])
            self.model.x.extend([rel_forward_dir[0], rel_forward_dir[1], rel_forward_dir[2]])
            self.model.x.extend(self.GoalSeries.Values[sample.index])

        print("Pivot Goals:", len(self.model.x)) 
        # print("self.model.x", self.model.x)

        # Input Geometry
        for i in range(self.Geometry.GetDimensionality()):
            m = Gf.Matrix4f().SetTranslate(Gf.Vec3f(*self.Geometry.References[i])) * root_mat.GetInverse()
            rel_pos = m.ExtractTranslation()
            self.model.x.extend([rel_pos[0], rel_pos[1], rel_pos[2]])
            self.model.x.extend([self.Geometry.Occupancies[i]])

            # print("Geometry loop:", rel_pos, self.Geometry.Occupancies[i])

        print("Pivot Geometry:", len(self.model.x)) 
        print("self.model.x", {i: val for i, val in enumerate(self.model.x)})

        



