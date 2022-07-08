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
            self.RootSeries.Transformations[i] = Gf.Matrix4f(Gf.Matrix4f(root_mat))
        
            if self.StyleSeries.Styles:
                self.StyleSeries.Values[i][0] = 1

            if self.GoalSeries.Actions:
                self.GoalSeries.Values[i][0] = 1  

            self.GoalSeries.Transformations[i] = Gf.Matrix4f(Gf.Matrix4f(root_mat))
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

            for time in range(200):
                self.timeline.forward_one_frame()
                current_frame_code = self.timeline.get_current_time() * self.stage.GetTimeCodesPerSecond()
                print("time: ", self.stage.GetTimeCodesPerSecond(), current_frame_code)

                if time == 0:
                    self.SetIdlePose()
                    self.Setup()
                else:
                    self.Feed()
                    self.model.predict()
                    self.Read()

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
        turn_val = self.controlloer.QueryTurn()
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

        # get move direction
        move4f = Gf.Vec4f(move[0], move[1], move[2], 1.0)

        # get root forward direction
        root_forward4f = Gf.Vec4f(root[2][0], root[2][1], root[2][2], 1.0)


        time_metric = 2.0
        for i in range(len_sample):
            weight = ((i + 1.0) / len_sample) ** 0.5
            bias_pos = 1.0 - (1.0 - weight) ** 0.75
            bias_dir = 1.0 - (1.0 - weight) ** 0.75

            # get turning rotation
            rotation = Gf.Rotation(Gf.Vec3d(0, 1, 0), bias_dir * turn)
            mat_w_rotation = Gf.Matrix4f(rotation, Gf.Vec3f(0))

            # direction_blend_4f = root_forward4f * mat_w_rotation
            # directions_blend[i] = Gf.Vec3f(direction_blend_4f[0], direction_blend_4f[1], direction_blend_4f[2])
            
            move_w_rot_4f = move4f * mat_w_rotation
            move_w_rot = Gf.Vec3f(move_w_rot_4f[0], move_w_rot_4f[1], move_w_rot_4f[2])

            print(turn, "direction blend: ", directions_blend[i], "root_forward4d: ", root_forward4f,  "move_w_rot:", move_w_rot)


            if i == 0:
                v1 = self.GoalSeries.Transformations[i + 1].ExtractTranslation() - self.GoalSeries.Transformations[i].ExtractTranslation()
                v2 = time_metric / (len_sample - 1) * move_w_rot
                positions_blend[i] = root.ExtractTranslation() + Gf.Lerp(bias_pos, v1, v2)
            else:
                v1 = self.GoalSeries.Transformations[i].ExtractTranslation() - self.GoalSeries.Transformations[i - 1].ExtractTranslation()
                v2 = time_metric / (len_sample - 1) * move_w_rot
                positions_blend[i] = positions_blend[i - 1] + Gf.Lerp(bias_pos, v1, v2)

            # print("positions_blend: ", move, positions_blend)

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

        # print("root_mat", root_mat)
        
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
            
            m = reflex_x_mat * mat * root_mat.GetInverse() * reflex_x_mat # relative to root

            rel_pos = m.ExtractTranslation() 
            rel_forward_dir = m.GetRow(2)
            rel_up_dir = m.GetRow(1)
            self.model.x.extend([rel_pos[0], rel_pos[1], rel_pos[2]])
            self.model.x.extend([rel_forward_dir[0], rel_forward_dir[1], rel_forward_dir[2]])
            self.model.x.extend([rel_up_dir[0], rel_up_dir[1], rel_up_dir[2]])
            self.model.x.extend(bone.velocity.copy()) 

            # print("bone velocity: ", bone.velocity)

        # print("Pivot Bone Positions / Velocities :", len(self.model.x))

        # Input Inverse Bone Positions
        for i, joint in enumerate(joint2mat):
            root_series_transform_last = Gf.Matrix4f(self.RootSeries.Transformations[-1])
            rel_pos = (joint2mat[joint] * root_series_transform_last.GetInverse()).ExtractTranslation()
            self.model.x.extend([rel_pos[0], rel_pos[1], rel_pos[2]])

        # print("Pivot Inverse Bone Positions :", len(self.model.x))
        # print("self.model.x", self.model.x)
        # print("self.model.x", self.model.x[-300:])
        # print(stop)

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

            # print("Input Trajectory Positions / Directions / Velocities / Styles: ", sample.index, rel_pos, rel_forward_dir, self.StyleSeries.Values[sample.index])
        
        # print("Pivot Trajectory Positions / Directions / Velocities / Styles :", len(self.model.x))
        # print("self.model.x", self.model.x)
        
        # Input Contacts
        self.model.x.extend(self.ContactSeries.Values[self.TimeSeries.Pivot])

        # print("Pivot Inverse Input Contacts :", len(self.model.x))
        # print("self.model.x", self.model.x)

        # Input Inverse Trajectory Positions 
        for i in range(self.TimeSeries.keycount):
            sample = self.TimeSeries.Samples[i * self.TimeSeries.Resolution]

            m = self.RootSeries.Transformations[sample.index] * (self.GoalSeries.Transformations[self.TimeSeries.Pivot]).GetInverse()
            rel_pos = m.ExtractTranslation()
            rel_forward_dir = m.GetRow(2)
            self.model.x.extend([rel_pos[0], rel_pos[2]])
            self.model.x.extend([rel_forward_dir[0], rel_forward_dir[2]])

        # print("Pivot Inverse Trajectory Positions :", len(self.model.x))
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

        # print("Pivot Goals:", len(self.model.x)) 
        # print("self.model.x", self.model.x)

        # Input Geometry
        for i in range(self.Geometry.GetDimensionality()):
            m = Gf.Matrix4f().SetTranslate(Gf.Vec3f(*self.Geometry.References[i])) * root_mat.GetInverse()
            rel_pos = m.ExtractTranslation()
            self.model.x.extend([rel_pos[0], rel_pos[1], rel_pos[2]])
            self.model.x.extend([self.Geometry.Occupancies[i]])

            # print("Geometry loop:", rel_pos, self.Geometry.Occupancies[i])

        # print("Pivot Geometry:", len(self.model.x)) 
        # print("self.model.x", self.model.x) # {i: val for i, val in enumerate(self.model.x)}


    def Read(self):
        """
        Read prediction from NN
        """
        assert self.timeline and self.timeline.is_playing()
        # Update Past State
        for i in range(self.TimeSeries.Pivot):
            sample = self.TimeSeries.Samples[i]
            mat = Gf.Matrix4f(1.0)
            mat.SetTranslateOnly(self.RootSeries.Transformations[i+1].ExtractTranslation())

            self.RootSeries.Transformations[i] = mat
            # TODO: set up rotation
            
            for j in range(len(self.StyleSeries.Styles)):
                self.StyleSeries.Values[i][j] = self.StyleSeries.Values[i + 1][j]
            
            for j in range(len(self.ContactSeries.Bones)):
                self.ContactSeries.Values[i][j] = self.ContactSeries.Values[i + 1][j]
            
            self.GoalSeries.Transformations[i] = self.GoalSeries.Transformations[i + 1]

            for j in range(len(self.GoalSeries.Actions)):
                self.GoalSeries.Values[i][j] = self.GoalSeries.Values[i + 1][j]

        
        root_mat = Gf.Matrix4f(self.RootSeries.Transformations[self.TimeSeries.Pivot])

        # Read Posture
        positions, forwards, upwards, velocities = [], [], [], []
        for i in range(len(self.actor.Bones)):
            # load position
            pos4f = Gf.Vec4f(self.model.read(), self.model.read(), self.model.read(), 1.0)
            pos4f_r = pos4f # * root_mat
            pos = Gf.Vec3f(pos4f_r[0], pos4f_r[1], pos4f_r[2])  
            positions.append(pos)

            # load forward
            forward3f = Gf.Vec3f(self.model.read(), self.model.read(), self.model.read()).GetNormalized()
            forward4f = Gf.Vec4f(forward3f[0], forward3f[1], forward3f[2], 1.0)
            forward4f_r = forward4f # * root_mat
            forward = Gf.Vec3f(forward4f_r[0], forward4f_r[1], forward4f_r[2])
            forwards.append(forward)

            # load upward
            upward3f = Gf.Vec3f(self.model.read(), self.model.read(), self.model.read()).GetNormalized()
            upward4f = Gf.Vec4f(upward3f[0], upward3f[1], upward3f[2], 1.0)
            upward4f_r = upward4f # * root_mat
            upward = Gf.Vec3f(upward4f_r[0], upward4f_r[1], upward4f_r[2])
            upwards.append(upward)

            # load velocity
            v4f = Gf.Vec4f(self.model.read(), self.model.read(), self.model.read(), 1.0)
            v4f_r = v4f # * root_mat
            v = Gf.Vec3f(v4f_r[0], v4f_r[1], v4f_r[2])
            velocities.append(v)

            # FIXME: lerp position
            # positions.append(Gf.Lerp(0.5, self.actor.Bones[i].))

        # Read Inverse Pose
        for i in range(len(self.actor.Bones)):
            pose_prediction = Gf.Vec4f(self.model.read(), self.model.read(), self.model.read(), 1.0)

        # Read Future Trajectory
        for i in range(self.TimeSeries.keycount):
            sample = self.TimeSeries.Samples[i * self.TimeSeries.Resolution]

            # load position
            pos4f = Gf.Vec4f(self.model.read(), 0, self.model.read(), 1.0)
            pos4f_r = pos4f * root_mat 
            pos = Gf.Vec3f(pos4f_r[0], pos4f_r[1], pos4f_r[2])

            # print(" Read Future Trajectory: ", i, pos4f)

            # load direction
            dir3f = Gf.Vec3f(self.model.read(), 0, self.model.read()).GetNormalized()
            dir4f = Gf.Vec4f(dir3f[0], dir3f[1], dir3f[2], 1.0)
            dir4f_r = dir4f * root_mat
            dir = Gf.Vec3f(dir4f_r[0], dir4f_r[1], dir4f_r[2])

            styles = [max(0, min(self.model.read(), 1)) for _ in range(len(self.StyleSeries.Styles))]

            # M: edit future only
            if i >= self.TimeSeries.Pivot // self.TimeSeries.Resolution:
                mat = Gf.Matrix4f(1.0)
                mat.SetTranslateOnly(pos)

                # TODO: set direction

                self.RootSeries.Transformations[sample.index] = mat
                self.StyleSeries.Values[sample.index] = styles

                if i >= 6:
                    pass
        
        # Read Future Contacts
        contacts = [self.model.read() for _ in range(len(self.ContactSeries.Bones))]


        # Read Inverse Trajectory
        for i in range(self.TimeSeries.keycount):
           
            sample = self.TimeSeries.Samples[i * self.TimeSeries.Resolution]
            goal = self.GoalSeries.Transformations[self.TimeSeries.Pivot]
            goal[3][1] = 0 # keep on floor
            
            # load position
            pos4f = Gf.Vec4f(self.model.read(), 0, self.model.read(), 1.0)
            pos4f_r = pos4f * goal
            pos = Gf.Vec3f(pos4f_r[0], pos4f_r[1], pos4f_r[2])

            # print("new pos", pos4f, pos)
            print("Read Inverse Trajectory i", i, goal.ExtractTranslation())
            # load direction
            dir3f = Gf.Vec3f(self.model.read(), 0, self.model.read()).GetNormalized()
            dir4f = Gf.Vec4f(dir3f[0], dir3f[1], dir3f[2], 1.0)
            dir4f_r = dir4f * goal
            dir = Gf.Vec3f(dir4f_r[0], dir4f_r[1], dir4f_r[2])

            # TODO:

            if i > self.TimeSeries.Pivot // self.TimeSeries.Resolution:
                pivot = self.RootSeries.Transformations[sample.index]
                pivot[3][1] = 0
                reference = self.GoalSeries.Transformations[sample.index]
                reference[3][1] = 0

                pivot_pos = pivot.ExtractTranslation()
                reference_pos = reference.ExtractTranslation()

                # distance2 = (pivot_pos[0] - reference_pos[0])**2 +  (pivot_pos[1] - reference_pos[1])**2 +  (pivot_pos[2] - reference_pos[2])**2
                # weight = ((i - 6)/ 7)**(distance2 * 100)

                mat = Gf.Matrix4f(1.0)
                mat.SetTranslateOnly(pos)
               
                # TODO: set direction
                self.RootSeries.Transformations[sample.index] = mat

                # if (i >= TimeSeries.PivotKey)

        # Read and Correct Goals
        for i in range(self.TimeSeries.keycount):
            sample = self.TimeSeries.Samples[i * self.TimeSeries.Resolution]
            weight = ((sample.index + 1) /  len(self.TimeSeries.Samples))**2
            
            # load position
            pos4f = Gf.Vec4f(self.model.read(), self.model.read(), self.model.read(), 1.0)
            pos4f_r = pos4f * root_mat
            pos = Gf.Vec3f(pos4f_r[0], pos4f_r[1], pos4f_r[2])

            # load direction
            dir3f = Gf.Vec3f(self.model.read(), self.model.read(), self.model.read()).GetNormalized()
            dir4f = Gf.Vec4f(dir3f[0], dir3f[1], dir3f[2], 1.0)
            dir4f_r = dir4f * root_mat
            dir = Gf.Vec3f(dir4f_r[0], dir4f_r[1], dir4f_r[2])
  
            actions = [max(0, min(self.model.read(), 1)) for _ in range(len(self.GoalSeries.Actions))]
            
            # FIXME: interpolate

        
            mat = Gf.Matrix4f(1.0)
            mat.SetTranslateOnly(pos)
            self.GoalSeries.Transformations[sample.index] 

            self.GoalSeries.Values[sample.index] = actions


        # Interpolate Current to Future Trajectory
        for i in range(len(self.TimeSeries.Samples)):
            sample  = self.TimeSeries.Samples[i]
            prevSample = self.TimeSeries.Samples[ i // self.TimeSeries.Resolution * self.TimeSeries.Resolution]
            nextSample = self.TimeSeries.Samples[min((i // self.TimeSeries.Resolution + 1) * self.TimeSeries.Resolution, len(self.TimeSeries.Samples) - 1)]
            
            # print(("nextSample of: ", i, " is ", nextSample.index)) 
            weight = (i % self.TimeSeries.Resolution) / self.TimeSeries.Resolution
            lerp_pos = Gf.Lerp(weight, self.RootSeries.Transformations[nextSample.index].ExtractTranslation(), self.RootSeries.Transformations[prevSample.index].ExtractTranslation())
            # print("Interpolate Current to Future Trajectory lerp_pos", i, lerp_pos)

            mat = Gf.Matrix4f(1.0)
            mat.SetTranslateOnly(lerp_pos)
            # self.RootSeries.Transformations[sample.index] = mat

            # TODO: set rotation

            self.GoalSeries.Transformations[sample.index] = self.GoalSeries.Transformations[nextSample.index] 
            self.StyleSeries.Values[i] = self.StyleSeries.Values[nextSample.index].copy()
            self.GoalSeries.Values[i]= self.GoalSeries.Values[nextSample.index].copy()

        # print("read pivot", self.model.pivot)


        # Assign Posture
        new_root_mat = self.RootSeries.Transformations[self.TimeSeries.Pivot]
        new_pos = new_root_mat.ExtractTranslation()
        new_rot = new_root_mat.ExtractRotationQuat()

        #　print("new_root_mat:", new_root_mat)
        t = carb.Float3(new_pos[0], new_pos[1],new_pos[2])
        q = carb.Float4(new_rot.imaginary[0], new_rot.imaginary[1], new_rot.imaginary[2], new_rot.real)
        self.character.set_world_transform(t, q)

        # print("new_pos new_rot", t, q)

        # print("positions, forwards, upwards, velocities", positions, forwards, upwards, velocities)
        trans, quats = set_pose(positions, forwards, upwards, velocities)
        
        # set pose
        for jj, t in enumerate(trans):
            self.character.set_variable("poses", trans)
            self.character.set_variable("rots", quats)

        # set velocity
        for i in range(len(velocities)):
            v = velocities[i]
            self.actor.Bones[i].velocity = [v[0], v[1], v[2]]


    




            

