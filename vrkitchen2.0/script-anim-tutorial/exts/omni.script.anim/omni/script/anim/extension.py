import omni.ext
import omni
import pxr
import omni.ui as ui
import carb
import importlib
import types

import asyncio


from pxr import AnimationSchema, AnimationSchemaTools

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):

        # property
        self._is_stopped = True
        self._tensor_started = False
        self._tensor_api = None

        print("[omni.script.anim] MyExtension startup")

        self._window = ui.Window("Script Animation Tutorial", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                with ui.HStack():
                    ui.Label("Some Label")
                    ui.Button("Click Me", clicked_fn= self.on_click)
                    ui.Button("Test simple", clicked_fn= self._on_button_add_xform_keys)
                    ui.Button("Test get position in anim", clicked_fn= self.get_transform_in_anim)
                with ui.HStack():
                    ui.Button("Test Animation", clicked_fn= self.test_anim_graph)
                    ui.Button("Convert file", clicked_fn= self.convert_file)
                    ui.Button("Test edit animation curve", clicked_fn= self.test_edit_curve)
                with ui.HStack():
                    ui.Button("Test Pose Provider", clicked_fn= self.test_pose_provider)
                    ui.Button("Test Pose Provider 2", clicked_fn= self.test_pose_provider2)
                    
                
                
                
    
    def on_click(self):
        carb.log_warn("Script Animation Tutorial")

        # setup subscriptions:
        self._setup_callbacks()

        self._enable_tensor_api()


        

        
    
    def on_shutdown(self):
        print("[omni.script.anim] MyExtension shutdown")

    # ---------------------------------------------------------------------------------------

    def _enable_tensor_api(self):
        manager = omni.kit.app.get_app().get_extension_manager()
        self._tensorapi_was_enabled = manager.is_extension_enabled("omni.physx.tensors")
        if not self._tensorapi_was_enabled:
            manager.set_extension_enabled_immediate("omni.physx.tensors", True)

        self._tensor_api = importlib.import_module("omni.physics.tensors")

    def _can_callback_physics_step(self) -> bool:
        if self._is_stopped:
            return False

        if self._tensor_started or self._tensor_api is None:
            return True

        self._tensor_started = True
        self.on_tensor_start(self._tensor_api)
        return True


    def _on_physics_step(self, dt):
        if not self._can_callback_physics_step():
            return

        # call user implementation
        self.on_physics_step(dt)

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.STOP):
            self._is_stopped = True
            self._tensor_started = False

            # !!!
            self._timeline_sub = None
            self._simulation_event_subscription = None
            self._physics_update_sub = None


        if e.type == int(omni.timeline.TimelineEventType.PLAY):
            self._is_stopped = False

        # call user implementation
        self.on_timeline_event(e)
    
    def on_timeline_event(self, e):
        """
        This method is called on timeline events. Note that in async sim, the STOP event is issued before the end
        of the simulation is awaited. Use on_simualtion_event and checking for

          e.type == int(omni.physx.bindings._physx.SimulationEvent.STOPPED)

        instead if you need to do operations that are illegal during simulation (e.g. actor removal).
        """
        pass
    
    def _setup_callbacks(self):
        stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_sub = stream.create_subscription_to_pop(self._on_timeline_event)
        # subscribe to Physics updates:
        self._physics_update_sub = omni.physx.get_physx_interface().subscribe_physics_step_events(self._on_physics_step)
        events = omni.physx.get_physx_interface().get_simulation_event_stream_v2()
        self._simulation_event_subscription = events.create_subscription_to_pop(self.on_simulation_event)

    
    def on_simulation_event(self, e):
        """
        This method is called on simulation events. See omni.physx.bindings._physx.SimulationEvent.
        """
        pass

    # --------------------------------------------------------

    def on_tensor_start(self, tensorApi: types.ModuleType):
        """
        This method is called when
            1. the tensor API is enabled, and
            2. when the simulation data is ready for the user to setup views using the tensor API.
        """
        sim = tensorApi.create_simulation_view("numpy")
        sim.set_subspace_roots("/World/*")

        self.characters = sim.create_articulation_view("/World/envs/*/Cube")

        self.cubes = sim.create_rigid_body_view("/World/envs/*/Cube")

        # self.hands = sim.create_rigid_body_view("/World/biped_demo/Body_Mesh")
        print("cubes? ", self.cubes.get_transforms())

    
    def on_physics_step(self, dt):
        """
        This method is called on each physics step callback, and the first callback is issued
        after the on_tensor_start method is called if the tensor API is enabled.
        """
        pass
        #self.count_down -= 1
        # self.dof_pos = self.frankas.get_dof_positions()
        
        # # print("dof_pos", self.dof_pos)
        # #if self.count_down < 0:
        # self.position_control()

    # --------------------------------------------

    def test_simple(self):
        stage = omni.usd.get_context().get_stage()

        prim = stage.DefinePrim("/World/cube", "Cube")

        prim = stage.GetPrimAtPath("/World/Cube")

        has_anim = prim.HasAPI(AnimationSchema.AnimationDataAPI)
        print("Object has animation? ", has_anim)

        # (result, err) = omni.kit.commands.execute("SetAnimCurveKey", paths=["/World/Cube.size"], value=120.0)
        # _anim_data_prim_path =  omni.usd.get_stage_next_free_path(stage, str(prim.GetPath()) + "/animationData", False)
        # AnimationSchemaTools.AddAnimation(prim, _anim_data_prim_path)


        prim_paths = [prim.GetPath()]


    
    def set_time_in_frame(self, nun_frame: int = 10):
        
        from omni.timeline import get_timeline_interface

        timeline_iface = get_timeline_interface()
        timeline_iface.play()
        timeline_iface.set_auto_update(False)
        for i in range(nun_frame):
            timeline_iface.forward_one_frame()
        
        timeline_iface.pause()

    def _on_button_add_xform_keys(self):
        self._usd_context = omni.usd.get_context()

        stage = self._usd_context.get_stage()
        if not stage:
            message = "Try to add animation keys while the scene stage is invalid."
            carb.log_info(message)
            return
        selection = self._usd_context.get_selection()
        prim_paths = selection.get_selected_prim_paths()
        self._add_xform_keys(prim_paths, stage)

    
    def _add_xform_keys(self, prim_paths, stage):
        
        from pxr import UsdGeom

        if prim_paths == None or len(prim_paths) == 0:
            message = "Please select xformable prims(objects) before adding animation keys."
            carb.log_info(message)
            return
        keyable_xform_attr_names = [
            "xformOp:translate",
            "xformOp:rotateX",
            "xformOp:rotateY",
            "xformOp:rotateZ",
            "xformOp:rotateXYZ",
            "xformOp:rotateXZY",
            "xformOp:rotateYXZ",
            "xformOp:rotateYZX",
            "xformOp:rotateZXY",
            "xformOp:rotateZYX",
            "xformOp:scale",
            "visibility"
        ]
        curve_names = []
        for path in prim_paths:
            if path is not None:
                prim = stage.GetPrimAtPath(path)
                if prim and prim.IsA(UsdGeom.Xformable):
                    for attr_name in keyable_xform_attr_names:
                        attr = prim.GetAttribute(attr_name)
                        if attr:
                            curve_names.append(attr.GetPath().pathString)
        if len(curve_names) > 0:
            omni.kit.commands.execute("SetAnimCurveKey", paths=curve_names)
        else:
            message = "There is no suitable xformable attribute to author keys."
            carb.log_info(message)
            return
    
    def get_transform_in_anim(self):
        self._usd_context = omni.usd.get_context()
        stage = self._usd_context.get_stage()

        # prim_list = stage.TraverseAll()

        # for prim in prim_list:
        #     if "f_avg_L_Foot" in prim.GetPath().pathString:
        #         translate = prim.GetAttribute("xformOp:translate").Get()
        #         print("Got it prim: ", translate)

        # timeline = omni.timeline.get_timeline_interface()
        # timeline.play()
        # time = timeline.get_current_time()
        # omni.kit.app.get_app().update()
        # omni.kit.app.get_app().update()

        character_prim = stage.GetPrimAtPath("/World/Character")
        print("character_prim ?!", character_prim == None)

        import omni.anim.graph.core as ag

        '''
        # c = ag.get_character("/World/Character")

        # t = carb.Float3(0, 0, 0)
        # q = carb.Float4(0, 0, 0, 1)
        # # c.get_world_transform(t, q)
        # c.get_joint_transform("f_avg_L_Foot", t, q)

        # print("t, q", t, q)
        '''
        self._usd_context = omni.usd.get_context()
        # omni.usd.get_context().open_stage_async(path)
        stage = self._usd_context.get_stage()
        
        from omni.anim.graph.ui.scripts.extension import PublicExtension

        graph_manager = PublicExtension.GRAPH_MANAGER
        print("graph manager dict", graph_manager._node_graph_dict)

        from pxr import Sdf
        node_graph = graph_manager.get_node_graph(Sdf.Path("/World/AnimationGraph"))

        print("node_graph: ", node_graph._path_to_node)

        # node_graph._on_create_node("/World/AnimationGraph/Animation")

        anim_clip_node = node_graph._path_to_node.get(Sdf.Path("/World/AnimationGraph/Animation"))
        root_node = node_graph._path_to_node.get(Sdf.Path("/World/AnimationGraph"))

        root_input_port = root_node.ports[0]
        print("root ports", root_input_port.kind, root_input_port.rel)

        output_port = anim_clip_node.output

        print("anim port", output_port)

        node_graph.create_connection(output_port,root_input_port)
        

        # node_graph._create_node_from_prim(stage.GetPrimAtPath("/World/AnimationGraph/Animation"))
        # root_node = node_graph._path_to_node[Sdf.Path("/World/AnimationGraph")]

        # _on_create_node

    def test_anim_graph(self):
        
        from pxr import Sdf, Usd, UsdSkel
        from pxr import AnimGraphSchema, AnimGraphSchemaTools
        import omni.anim.graph.core as ag
        import carb

        self._usd_context = omni.usd.get_context()
        # omni.usd.get_context().open_stage_async(path)
        self.stage = self._usd_context.get_stage()

        character_path = "/World/character"
        anim_path = "/World/character_anim_clip"
        
        character_usd = "E:/researches/VRKitchen2.0-Tutorial/asset/mixamo/peasant_girl_converted.usd"
        anim_usd = "E:/researches/VRKitchen2.0-Tutorial/asset/mixamo/silly_dancing_converted.usd"

        prim = self.stage.GetPrimAtPath(character_path)
        if not prim.IsValid():
            prim = self.stage.DefinePrim(character_path)

        success_bool = prim.GetReferences().AddReference(character_usd)
        assert success_bool

        prim = self.stage.GetPrimAtPath(anim_path)
        if not prim.IsValid():
            prim = self.stage.DefinePrim(anim_path)

        success_bool = prim.GetReferences().AddReference(anim_usd)


        anim_graph_path = "/World/AnimationGraph"
        skeleton_path = "/World/character/Hips0/Skeleton"

        ### anim_graph = AnimGraphSchemaTools.createAnimationGraph(stage, Sdf.Path("/World/AnimationGraph"))
        omni.kit.commands.execute("CreateAnimationGraphCommand", \
            path=Sdf.Path(anim_graph_path), skeleton_path=Sdf.Path(skeleton_path))

        omni.kit.commands.execute("ApplyAnimationGraphAPICommand", \
            paths=[Sdf.Path(character_path + "/Hips0")], animation_graph_path=Sdf.Path(anim_graph_path))

        
        skeleton_prim = self.stage.GetPrimAtPath(skeleton_path)
        skeleton_bindingAPI = UsdSkel.BindingAPI(skeleton_prim)
        skeleton_bindingAPI.GetAnimationSourceRel().SetTargets([])


        # create 
        omni.kit.commands.execute(
                    'CreatePrimCommand',
                    prim_type="AnimationClip",
                    prim_path="/World/AnimationGraph/Animation",
                    select_new_prim=True,
                )
        

        animclip_prim = self.stage.GetPrimAtPath("/World/AnimationGraph/Animation")
        animclip_bindingAPI = UsdSkel.BindingAPI(animclip_prim)

        anim_clip = AnimGraphSchema.AnimationClip(animclip_prim)
        source_rel = anim_clip.GetInputsAnimationSourceRel()

        omni.kit.commands.execute(
            'omni.anim.graph.ui.scripts.command.SetRelationshipTargetsCommand',
            relationship=source_rel,
            targets=[Sdf.Path("/World/character_anim_clip/Hips0/mixamo_com")]
        )
        
    
    def convert_file(self):
        print("convert file test")

        async def convert_file_async():
            from pathlib import Path

            test_data_path = "E:/researches/VRKitchen2.0-Tutorial/asset/mixamo/Silly Dancing.fbx"
            converter_manager = omni.kit.asset_converter.get_instance()
            context = omni.kit.asset_converter.AssetConverterContext()
            context.keep_all_materials = True
            context.merge_all_meshes = True
            output_path = "E:/researches/VRKitchen2.0-Tutorial/asset/mixamo/silly_dancing_converted.usd"
            task = converter_manager.create_converter_task(test_data_path, output_path, None, context)
      
            success = await task.wait_until_finished()
            assert success, "convert not successful"
            assert Path(output_path).is_file()

        
        asyncio.ensure_future(convert_file_async())

    def test_edit_curve(self):
        print("edit curve test")

        from pxr import AnimGraphSchema, AnimGraphSchemaTools, UsdSkel
        from pxr import Gf, Sdf, Usd
        
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath("/World/AnimationGraph/Animation")

        print("prim type", prim.GetTypeName())

        # relation = prim.GetRelationship("animationData:binding")
        #print("relation", relation)


        anim_clip = AnimGraphSchema.AnimationClip(prim)

        # has_anim = AnimationSchemaTools.HasAnimation(prim)
        # print("has_anim", has_anim)
        # return 
        src_rel = anim_clip.GetInputsAnimationSourceRel()
        src_targets = src_rel.GetTargets()
        if src_targets:
            src_skel_prim = stage.GetPrimAtPath(src_targets[0])
            print("src_skel_prim", src_skel_prim.GetPath())

            # has_anim = AnimationSchemaTools.HasAnimation(src_skel_prim)
            # print("has_anim", has_anim)
            # return 


            src_skel_anim = UsdSkel.Animation(src_skel_prim)

            # print(src_skel_anim.GetSchemaAttributeNames())

            rot_attr = src_skel_anim.GetRotationsAttr()
            # print("GetJointsAttr ()", src_skel_anim.GetJointsAttr().Get())
            # print("CetRotationsAttr ()", rot_attr.HasValue())
            # print("GetTranslationsAttr ()", src_skel_anim.GetTranslationsAttr().Get())
            
            n_time_samples = rot_attr.GetNumTimeSamples()
            # print("n_time_samples", n_time_samples) 

            timeline = omni.timeline.get_timeline_interface()
            # current_frame_code = timeline.get_current_time() * stage.GetTimeCodesPerSecond()
            
            # quats = src_skel_anim.GetRotationsAttr().Get(current_frame_code)
            # print(":rot_attr", current_frame_code, len(quats), quats)

            # current_frame_code = 1.0
            # quats = src_skel_anim.GetRotationsAttr().Get(current_frame_code)
            # print(":rot_attr", current_frame_code, len(quats), quats)

            # current_frame_code = -1.0
            # quats = src_skel_anim.GetRotationsAttr().Get(current_frame_code)
            # print(":rot_attr", current_frame_code, len(quats), quats)

            # trans = src_skel_anim.GetTranslationsAttr()
            # success = trans.Clear()
            # success = success and src_skel_anim.GetRotationsAttr().Clear()
            # print("clear success", success)

            animation = src_skel_anim

            timecode = Usd.TimeCode(0.0 * stage.GetTimeCodesPerSecond())
            trans = animation.GetTranslationsAttr().Get(timecode)
            rots = animation.GetRotationsAttr().Get(timecode)
            scales = animation.GetScalesAttr().Get(timecode)
            joints = animation.GetJointsAttr().Get()

            animation_new_path = "/World/AnimationGraph/newAnimation"
            animation_new = UsdSkel.Animation.Define(stage, animation_new_path)
            animation_new_prim = animation_new.GetPrim()

            print("joints", len(joints), joints)
            print("trans", len(trans), trans)
            trans[0] = trans[0] + Gf.Vec3f(0,100,0)
            print("trans", trans)
            
            print("scales", scales)

            with Sdf.ChangeBlock():
                animation_new.GetJointsAttr().Set(joints)
                animation_new.GetTranslationsAttr().Set(trans)
                # animation_new.GetTranslationsAttr().Clear()
                animation_new.GetRotationsAttr().Set(rots)
                # animation_new.GetRotationsAttr().Clear()
                animation_new.GetScalesAttr().Set(scales)
            
            # skeleton_bindingAPI.GetAnimationSourceRel().SetTargets([animation_new_path])

            return


            attrs = [src_skel_prim.GetAttribute(attr_name) for attr_name in src_skel_anim.GetSchemaAttributeNames()]

            rt = src_skel_prim.GetAttribute("rotations.timeSamples")

            print("rt", rt)

            # for attr in attrs:
            #     print("attr", attr)

            for c, attr in enumerate(attrs):
                
                u = []
                # elements = attr.Get(u)
                print(c, attr, type(attr),  attr.HasValue(), attr.HasAuthoredValue())
                # if attr.HasValue():
                #     elements = list(attr.Get())
                #     print("elements", elements)

                # time_samples = attr.GetTimeSamples()
                # if len(time_samples) > 0:
                #     print(f"attr with {len(time_samples)} time samples", attr)
                #     print("time_samples", type(time_samples), time_samples)
                
                # print("GetTimeSamplesInInterval()", attr.GetTimeSamplesInInterval())

    def test_pose_provider(self):
        import omni.anim.graph.core as ag

        from pxr import UsdSkel, UsdGeom, Gf, Sdf

        print("test pose provider")

        timeline = omni.timeline.get_timeline_interface()
        stage = omni.usd.get_context().get_stage()

        # stage.SetStartTimeCode(10)
        # stage.SetEndTimeCode(100)
        # return 

        async def test_PoseProvider_pose_provider():
            timeline.stop()
            timeline.set_current_time(0.0)
            timeline.set_auto_update(False)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            stage.SetEndTimeCode(100)
            timeline.set_looping(True)

            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            timeline.play()
            
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            #character = ag.get_character("/World/Character")
            character = ag.get_character("/World/smpl_f")

            #animprim = stage.GetPrimAtPath("/World/stand_idle_loop_skelanim")
            animprim = stage.GetPrimAtPath("/World/chicken2/f_avg_root/Animation")
            anim = UsdSkel.Animation(animprim)
            joints = anim.GetJointsAttr().Get()

            for i in range(1):
                print(f"time {i}")
                previous_frame_code = timeline.get_current_time() * stage.GetTimeCodesPerSecond()
                timeline.forward_one_frame()
                current_frame_code = timeline.get_current_time() * stage.GetTimeCodesPerSecond()

                # delta_trans_carb = carb.Float3(10, 0, 0)
                # delta_quat_carb = carb.Float4(0, 0, 0, 0)
                # character.set_transform_delta("PoseProvider", delta_trans_carb, delta_quat_carb)

                
                trans = anim.GetTranslationsAttr().Get(current_frame_code)
                quats = anim.GetRotationsAttr().Get(current_frame_code)

                trans = [carb.Float3(e[0],e[1],e[2]) for e in trans]
                quats = [carb.Float4(e.imaginary[0], e.imaginary[1], e.imaginary[2], e.real) for e in quats ]

                print("current_frame_code: ", current_frame_code)
                print("len trans", len(trans), trans)
                print("len joints", len(joints))
                # debug
                for jj, t in enumerate(trans):
                    cube_name = joints[jj].split("/")[-1]
                    cube = stage.DefinePrim(f"/World/Cube/{cube_name}", "Xform")
                    cube_mat = Gf.Matrix4d().SetRotate(Gf.Quatd(quats[jj][3], quats[jj][0], quats[jj][1], quats[jj][2])) * \
                         Gf.Matrix4d().SetTranslate(Gf.Vec3d(t[0], t[1], t[2]))
                    
                    print(jj, "cube_mat: ", cube_name, cube_mat)
                    # UsdGeom.Xformable(cube).AddTransformOp().Set(cube_mat)

                    omni.kit.commands.execute(
                        "TransformPrimCommand",
                        path=cube.GetPath().pathString,
                        new_transform_matrix=cube_mat,
                    )

                    # attr_matrix = cube.CreateAttribute("xformOp:transform", Sdf.ValueTypeNames.Matrix4d, False)
                    # attr_matrix.Set(cube_mat)

                    # cube.GetAttribute("xformOp:scale").Set(Gf.Vec3f([0.1, 0.1, 0.1]))

                
                print("trans", trans)
                print("quats", quats)
                character.set_variable("poses", trans)
                character.set_variable("rots", quats)

                target_pos = character.get_variable("poses")
                print("target_pos", target_pos)

                # scales = anim.GetScalesAttr().Get(current_frame_code)
                # translist = [carb.Float3(i[0], i[1], i[2]) for i in trans ]
                tran_root = carb.Float3(0.001 * i, 0.0, 0.0)
                # quatslist = [carb.Float4(i.imaginary[0], i.imaginary[1], i.imaginary[2], i.real) for i in quats ]
                #quatslist[0] = carb.Float4(0.0, 0.0, 0.0, 1.0)
                #scaleslist = [carb.Float3(i)  for i in scales ]
                character.set_variable("tran_root", tran_root)


                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()

            timeline.set_looping(False)
            timeline.set_auto_update(True)
            timeline.pause()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        asyncio.ensure_future(test_PoseProvider_pose_provider())

    
    def test_pose_provider2(self):
        print("test_pose_provider2")
        from .smplx.utils import generate_trans_and_rots_for_pose_provider
        import omni.anim.graph.core as ag
        from pxr import UsdSkel, UsdGeom, Gf, Sdf

        print("test pose provider")

        timeline = omni.timeline.get_timeline_interface()
        stage = omni.usd.get_context().get_stage()

        # stage.SetStartTimeCode(10)
        # stage.SetEndTimeCode(100)
        # return 

        async def test_PoseProvider_pose_provider():
            timeline.stop()
            timeline.set_current_time(0.0)
            timeline.set_auto_update(False)
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            stage.SetEndTimeCode(100)
            timeline.set_looping(True)

            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            timeline.play()
            
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

            #character = ag.get_character("/World/Character")
            character = ag.get_character("/World/smplx")


            for i in range(1):
                print(f"time {i}")
                previous_frame_code = timeline.get_current_time() * stage.GetTimeCodesPerSecond()
                timeline.forward_one_frame()
                current_frame_code = timeline.get_current_time() * stage.GetTimeCodesPerSecond()

                # delta_trans_carb = carb.Float3(10, 0, 0)
                # delta_quat_carb = carb.Float4(0, 0, 0, 0)
                # character.set_transform_delta("PoseProvider", delta_trans_carb, delta_quat_carb)

                trans, quats = generate_trans_and_rots_for_pose_provider()

                # trans = [carb.Float3(e[0],e[1],e[2]) for e in trans]
                # quats = [carb.Float4(e.imaginary[0], e.imaginary[1], e.imaginary[2], e.real) for e in quats ]

                # debug
                from .smplx.constants import smplx_joint2path
                joints = list(smplx_joint2path.values())
                for jj, t in enumerate(trans):
                    cube_name = joints[jj] #.split("/")[-1]
                    cube = stage.DefinePrim(f"/World/Cube/{cube_name}", "Xform")
                    cube_mat = Gf.Matrix4d().SetRotate(Gf.Quatd(quats[jj][3], quats[jj][0], quats[jj][1], quats[jj][2])) * \
                         Gf.Matrix4d().SetTranslate(Gf.Vec3d(t[0], t[1], t[2]))
                    
                    print(jj, "cube_mat: ", cube_name, cube_mat)
                    # UsdGeom.Xformable(cube).AddTransformOp().Set(cube_mat)

                    omni.kit.commands.execute(
                        "TransformPrimCommand",
                        path=cube.GetPath().pathString,
                        new_transform_matrix=cube_mat,
                    )

                character.set_variable("poses", trans)
                character.set_variable("rots", quats)

                target_pos = character.get_variable("poses")
                print("target_pos", target_pos)

                # scales = anim.GetScalesAttr().Get(current_frame_code)
                # translist = [carb.Float3(i[0], i[1], i[2]) for i in trans ]
                tran_root = carb.Float3(0.001 * i, 0.0, 0.0)
                # quatslist = [carb.Float4(i.imaginary[0], i.imaginary[1], i.imaginary[2], i.real) for i in quats ]
                #quatslist[0] = carb.Float4(0.0, 0.0, 0.0, 1.0)
                #scaleslist = [carb.Float3(i)  for i in scales ]
                character.set_variable("tran_root", tran_root)


                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()

            timeline.set_looping(False)
            timeline.set_auto_update(True)
            timeline.pause()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()

        asyncio.ensure_future(test_PoseProvider_pose_provider())
