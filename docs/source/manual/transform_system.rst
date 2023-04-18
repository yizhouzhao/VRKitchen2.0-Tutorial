Transform
--------------------------------------------------

This part teaches how to get/set the ``translate``, ``orientation``, and ``scale`` of an object.


.. note::
    
    You may get ``stage`` and object ``prim`` first, 
    
    .. code-block:: python

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath("/World/game/franka")

Get translate/orient/scale (from attribute)
#########################################################

.. code-block:: python

    translate = prim.GetAttribute("xformOp:translate").Get()
    orient = prim.GetAttribute("xformOp:orient").Get()
    scale = prim.GetAttribute("xformOp:scale").Get()


Get translate/orient/scale (from transform matrix)
####################################################

.. code-block:: python

    from omni.usd import get_world_transform_matrix, get_local_transform_matrix

    # or new verion
    # from omni.usd.utils import get_world_transform_matrix, get_local_transform_matrix
  
    mat = get_world_transform_matrix(prim) 
    
    # or 
    # mat = UsdGeom.Xformable(usd_prim).ComputeLocalToWorldTransform(time)

    # or local
    mat = get_local_transform_matrix(prim) 
    
    translate = mat.ExtractTranslation()
    quad = eval(str(mat.ExtractRotation().GetQuat()))
    scale = mat.ExtractScale()


Set translate/orient/scale (from attribute)
####################################################

.. code-block:: python

    prim.GetAttribute("xformOp:translate").Set(pxr.Gf.Vec3f(0,0,0))
    prim.GetAttribute("xformOp:orient").Set(pxr.Gf.Quatd(1, 0, 0, 0))
    prim.GetAttribute("xformOp:scale").Set(pxr.Gf.Vec3f(1, 2, 1))

.. note::
    
    You may add ``Attribute`` first if the prim doesn't contain the translate attribute, `read more about USDAttribute <https://graphics.pixar.com/usd/release/api/class_usd_attribute.html>`_

    .. code-block:: python

        prim.AddTranslateOp().Set(pxr.Gf.Vec3f(0,0,0))
        prim.AddOrientOp().Set()
        prim.AddScaleOp().Set(pxr.Gf.Vec3f(1.0, 1.0, 1.0))


Set translate/orient/scale (from transform matrix)
####################################################

.. code-block:: python

    translate = [0, 0, 0]
    scale = [1, 1, 1]
    rotation = pxr.Gf.Quatd(1, 0, 0, 0)
    xform = pxr.Gf.Matrix4d().SetScale(scale) * pxr.Gf.Matrix4d().SetRotate(rotation) * pxr.Gf.Matrix4d().SetTranslate(translate)
            
    omni.kit.commands.execute(
        "TransformPrimCommand",
        path=prim.GetPath(),
        new_transform_matrix=xform,
    )



