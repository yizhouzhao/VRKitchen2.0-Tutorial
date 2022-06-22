import omni.ext
import omni.ui as ui

import omni
import pxr 
import carb

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[human.as.articulation] MyExtension startup")

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Button("Capsu test", clicked_fn=self.test_capsule)
                ui.Button("Capsu test", clicked_fn=self.test_smpl)

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

        stage = omni.usd.get_context().get_stage()

        import omni.anim.graph.core as ag

        c = ag.get_character("/World/Character2")

        t = carb.Float3(0, 0, 0)
        q = carb.Float4(0, 0, 0, 1)
        # c.get_world_transform(t, q)

        
        c.get_joint_transform("f_avg_R_Hand", t, q)
        print("t, q", t, q)



        # pelvis_prim_path_str = "/World/smpl_f/f_avg_root/f_avg_root/f_avg_Pelvis"
        # pelvis_prim = stage.GetPrimAtPath(pelvis_prim_path_str)

        # mat = get_world_transform_matrix(pelvis_prim)
        # print("mat", mat.ExtractTranslation())


        