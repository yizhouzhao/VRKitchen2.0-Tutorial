Joint system
--------------------------------------------------

This part includes the APIs for setting up joint systems.

Common imports for joints
##################################

.. code-block:: python

    from pxr import UsdPhysics

Create joints
##################################

.. code-block:: python

    component = UsdPhysics.FixedJoint.Define(stage, joint_path)
    component = UsdPhysics.RevoluteJoint.Define(stage, joint_path)
    component = UsdPhysics.PrismaticJoint.Define(stage, joint_path)
