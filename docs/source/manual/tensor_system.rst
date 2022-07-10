Tensor system
--------------------------------------------------

Package name ``omni.physics.tensors`` or ``omni.physx.tensors``

Pure tensor view
====================================

Create tensor view:

.. code-block:: python

    sim = omni.physics.tensors.create_simulation_view("numpy")
    sim.set_subspace_roots("/World/envs/*")
    self.robots = sim.create_articulation_view("/World/envs/*/jetbot")

Obtain tensor value:

.. code-block:: python
    
    # get position
    self.robots.get_dof_positions()

Set tensor value:

.. code-block:: python
    
    # set joint position
    self.robots.set_dof_positions(self.robot_original_position, self.robot_indices)
    self.robots.set_dof_position_targets(self.robot_original_position, self.robot_indices)
    
    # set root position
    self.robots.set_root_transforms(pos, self.robot_indices)

Robot 
=====================================

Set up robots

.. code-block:: python

    self.robots = RobotView("/World/envs/*/jetbot")
    self.robot_indices = np.arange(self.robots.count, dtype=np.int32)
    self.robots.initialize()

Get robot information

.. code-block:: python

    # self._backend_utils = np_utils  # import omni.isaac.core.utils.numpy as np_utils
    self.robot_original_position = self._backend_utils.clone_tensor(self.robots._physics_view.get_dof_positions())
    self.xform_original_transform = self.robots.get_world_poses()

Apply action / Set position

.. code-block:: python

    action = np.random.uniform(-1, 1, (len(self.robot_indices), 2)) * 20
    self.robots.set_joint_velocity_targets(action, self.robot_indices)
    pos = [[0.5 * i, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0] for i in range(len(self.robot_indices))]
    self.robots._physics_view.set_root_transforms(pos, self.robot_indices)