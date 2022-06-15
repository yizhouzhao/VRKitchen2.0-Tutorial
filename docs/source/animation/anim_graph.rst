Animation Graph
======================================

.. note::

    Common import: 

    .. code-block:: python

        from pxr import Sdf, Usd
        from pxr import AnimGraphSchema, AnimGraphSchemaTools
        import omni.anim.graph.core as ag
        import carb

Add animation graph
############################

.. code-block:: python

    anim_graph = AnimGraphSchemaTools.createAnimationGraph(stage, Sdf.Path("/World/AnimationGraph"))
  
    # or
    omni.kit.commands.execute("CreateAnimationGraphCommand", path=Sdf.Path("/World/AnimationGraph"), skeleton_path=Sdf.Path.emptyPath)

.. note::
    we may set/clear original skeletal animation at root joint by

    .. code-block:: python

        skeleton_prim = stage.GetPrimAtPath("/World/character/f_avg_root")
        skeleton_bindingAPI = UsdSkel.BindingAPI(skeleton_prim)

        # set
        skeleton_bindingAPI.GetAnimationSourceRel().SetTargets(["/World/character/f_avg_root/Animation"])

        # clear
        skeleton_bindingAPI.GetAnimationSourceRel().SetTargets([])
    

Set Skeleton
###################################################

.. code-block:: python

    rel = anim_graph.GetSkelSkeletonRel()
    rel.SetTargets([_skeleton_path])

    # or
    omni.kit.commands.execute("CreateAnimationGraphCommand", path=Sdf.Path("/World/AnimationGraph"), skeleton_path=_skeleton_path)



Apply animation graph api
############################

.. code-block:: python

    AnimGraphSchemaTools.applyAnimationGraphAPI(stage, path, self._animation_graph_path)
  
    # or
    omni.kit.commands.execute("ApplyAnimationGraphAPICommand", paths=self._apply_prim_paths, animation_graph_path=selected_prim.GetPath())


Remove animation graph api
############################

.. code-block:: python

    if stage.GetPrimAtPath(path).HasAPI(AnimGraphSchema.AnimationGraphAPI):
        AnimGraphSchemaTools.removeAnimationGraphAPI(stage, path)
  
    # or
    omni.kit.commands.execute("RemoveAnimationGraphAPICommand", paths=selected_paths)



Get character
############################

.. code-block:: python

    character = ag.get_character("/World/character")

Get character position (run time)
#####################################################

.. code-block:: python

        t = carb.Float3(0, 0, 0)
        q = carb.Float4(0, 0, 0, 1)
        character.get_world_transform(t, q)


Get joint position (run time)
#####################################################
        
.. code-block:: python
        
        t = carb.Float3(0, 0, 0)
        q = carb.Float4(0, 0, 0, 1)
        character.get_joint_transform("f_avg_L_Foot", t, q)