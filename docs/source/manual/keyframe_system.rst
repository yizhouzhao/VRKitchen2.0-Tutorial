Key Frame 
---------------------------------------------------------------------------------

This part includes the APIs for setting up keyframe using code

Set up keyframe for a prim attribute
#################################################################################

.. code-block:: python

    (result, err) = omni.kit.commands.execute("SetAnimCurveKeys", 
                paths=["/World/Exhibition2/ur3e_nvidia_140/ur3e/shoulder_link/shoulder_lift_joint.drive:angular:physics:targetPosition"],
                value = float(0),
                time=Usd.TimeCode(0)
                )




