Physics
--------------------------------------------------

This part includes the APIs for setting up physics in the stage , `read more about USDPhysics <https://graphics.pixar.com/usd/release/api/usd_physics_page_front.html>`_


Rigid body & Collision
#########################################################

.. code-block:: python

    from pxr import UsdPhysics

    # check rigidbody api
    prim.HasAPI(UsdPhysics.RigidBodyAPI)
    prim.HasAPI(pxr.UsdPhysics.CollisionAPI)

    # get api
    UsdPhysics.RigidBodyAPI.Get(stage, path)
    UsdPhysics.CollisionAPI.Get(stage, path)

    # apply/add api

    UsdPhysics.RigidBodyAPI.Apply(stage, path)
    UsdPhysics.CollisionAPI.Apply(stage, path)


Set up GPU for physics
#########################################################

.. code-block:: python

    from omni.physx import acquire_physx_interface

    physx = acquire_physx_interface()

    physx.overwrite_gpu_setting(1) # 1 means using GPU


Set mass
#########################################################

.. code-block:: python

    mass = 10
    massAPI = UsdPhysics.MassAPI.Apply(prim)
    massAPI.GetMassAttr().Set(mass)


Set/Get Gravity value
#########################################################

.. code-block:: python
    
    # FIXME: correct gravity api
    # Assume _my_world is of type World
    # self._my_world ._physics_context.get_gravity()
    # meters_per_unit = get_stage_units()
    # self._my_world ._physics_context.set_gravity(value=-9.81 / meters_per_unit)

Set up collision
#########################################################

.. code-block:: python

    from omni.physx.scripts import utils, physicsUtils

    utils.setPhysics(prim=cup_shape_prim, kinematic=False)    
    
    utils.setCollider(prim=cup_shape_prim, approximationShape="convexDecomposition") 
    # other approximationShape: none, triangulate, convexHull, e.t.c.


Set up physical material
#########################################################

.. code-block:: python

    def _setup_physics_material(self, path: Sdf.Path):
        from pxr import UsdGeom, UsdLux, Gf, Vt, UsdPhysics, PhysxSchema, Usd, UsdShade, Sdf
        
        if self._physicsMaterialPath is None:
            self._physicsMaterialPath = self._stage.GetDefaultPrim().GetPath().AppendChild("physicsMaterial")
            UsdShade.Material.Define(self._stage, self._physicsMaterialPath)
            material = UsdPhysics.MaterialAPI.Apply(self._stage.GetPrimAtPath(self._physicsMaterialPath))
            material.CreateStaticFrictionAttr().Set(self._material_static_friction)
            material.CreateDynamicFrictionAttr().Set(self._material_dynamic_friction)
            material.CreateRestitutionAttr().Set(self._material_restitution)

        collisionAPI = UsdPhysics.CollisionAPI.Get(self._stage, path)
        prim = self._stage.GetPrimAtPath(path)
        if not collisionAPI:
            collisionAPI = UsdPhysics.CollisionAPI.Apply(prim)

        # apply material
        physicsUtils.add_physics_material_to_prim(self._stage, prim, self._physicsMaterialPath)

