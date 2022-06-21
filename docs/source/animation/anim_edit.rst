.. _ANIM_EDIT_API:

Animation Editing
======================================

.. note::

    Common import: 

    .. code-block:: python

        from pxr import AnimGraphSchema, AnimGraphSchemaTools, UsdSkel
        from pxr import Gf, Sdf, Usd

Read more about `USD SKEL ANIMATION <https://graphics.pixar.com/usd/dev/api/class_usd_skel_animation.html#a83e60aafcd3454c8cd1b5bb86a585296>`_.

Get animation clip from prim
###########################################

.. code-block:: python

    anim_clip = AnimGraphSchema.AnimationClip(prim)
    has_anim = AnimationSchemaTools.HasAnimation(prim)

Get animation source
###########################################

.. code-block:: python

    src_rel = anim_clip.GetInputsAnimationSourceRel()
    if src_targets:
        src_skel_prim = stage.GetPrimAtPath(src_targets[0])


Get skeletal animation 
###########################################

.. code-block:: python

    src_skel_anim = UsdSkel.Animation(src_skel_prim)


Get translation from animation at time
###########################################

.. code-block:: python

    timecode = Usd.TimeCode(0.0 * stage.GetTimeCodesPerSecond())
    trans = animation.GetTranslationsAttr().Get(timecode)
    rots = animation.GetRotationsAttr().Get(timecode)
    scales = animation.GetScalesAttr().Get(timecode)
    joints = animation.GetJointsAttr().Get()


New animation
#####################################

.. code-block:: python

    animation_new_path = "/World/AnimationGraph/newAnimation"
    animation_new = UsdSkel.Animation.Define(stage, animation_new_path)
    # animation_new_prim = animation_new.GetPrim()

Set up animation data
#####################################

.. code-block:: python

     with Sdf.ChangeBlock():
        animation_new.GetJointsAttr().Set(joints)
        animation_new.GetTranslationsAttr().Set(trans)
        animation_new.GetRotationsAttr().Set(rots)
        animation_new.GetScalesAttr().Set(scales)

        # animation_new.GetRotationsAttr().Clear()

Bind animation target
#####################################

.. code-block:: python      
        
    skeleton_prim = self.stage.GetPrimAtPath(skeleton_path)
    skeleton_bindingAPI = UsdSkel.BindingAPI(skeleton_prim)
    skeleton_bindingAPI.GetAnimationSourceRel().SetTargets([animation_new_path])

