import omni.ext
import omni
import pxr
import omni.ui as ui
import carb
import importlib
import types


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
                ui.Label("Some Label")
                ui.Button("Click Me", clicked_fn= self.on_click)
                ui.Button("Test simple", clicked_fn= self._on_button_add_xform_keys)
                # ui.Button("Test timeline", clicked_fn= self.set_time_in_frame)
                
                
    
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

        self.characters = sim.create_articulation_view("/World/biped_demo")

        # self.hands = sim.create_rigid_body_view("/World/biped_demo/Body_Mesh")
        # print("hands? ", self.hands.get_transforms())

    
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