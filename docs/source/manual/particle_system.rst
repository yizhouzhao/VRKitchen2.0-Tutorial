Particle Systems
--------------------------------------------------

This part includes the APIs for setting up particle systems.

Common imports for particle
##################################

.. code-block:: python

    from pxr import UsdPhysics, PhysxSchema, Sdf, Gf
    from omni.physx.scripts import physicsUtils, particleUtils

Create physics scene
##################################

.. code-block:: python

    self._stage = omni.usd.get_context().get_stage()
    self._default_prim_path = Sdf.Path("/World")

    # create physics scene
    physicsScenePath = self._default_prim_path.AppendChild("physicsScene")
    scene = UsdPhysics.Scene.Define(self._stage, physicsScenePath)
    physxAPI = PhysxSchema.PhysxSceneAPI.Apply(scene.GetPrim())
    physxAPI.CreateSolverTypeAttr("TGS") # TGS or PGS, TGS is more accurate but slower


Create pbd material
##################################

.. code-block:: python

    self._pbd_material_path = self._default_prim_path.AppendChild("PBDMaterial")
    particleUtils.add_pbd_particle_material(self._stage, self._pbd_material_path)
    self._pbd_material_api = PhysxSchema.PhysxPBDMaterialAPI.Get(self._stage, self._pbd_material_path)


Create particle systems
##################################

.. code-block:: python

        self._particle_system_path = self._default_prim_path.AppendChild("particleSystem")
        particleUtils.add_physx_particle_system(
            stage=self._stage,
            particle_system_path=self._particle_system_path, 
            simulation_owner=scene.GetPath(),
        )
        self._particle_system = PhysxSchema.PhysxParticleSystem.Get(self._stage, self._particle_system_path)

        physicsUtils.add_physics_material_to_prim(self._stage, self._particle_system.GetPrim(), self._pbd_material_path)


Create particle points
##################################

.. code-block:: python

    # create 1 particle
    positions_list = []
    velocities_list = []
    widths_list = []

    positions_list.append(Gf.Vec3f(1.0, 1.0, 1.0))
    velocities_list.append(Gf.Vec3f(0.0, 0.0, 0.0))
    widths_list.append(0.5)

    particlePointsPath = Sdf.Path("/World/particles") 
    particleSet = particleUtils.add_physx_particleset_points(
        self._stage,
        particlePointsPath,
        positions_list,
        velocities_list,
        widths_list,
        self._particle_system_path,
        self_collision = True,
        fluid = True,
        particle_group = 0,
        particle_mass = 1.0,
        density = 0.02,
    )
