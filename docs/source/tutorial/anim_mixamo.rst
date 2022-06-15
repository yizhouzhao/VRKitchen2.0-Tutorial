Animation Tutorial 1: Bring Mixamo Animation to Omniverse
====================================================================

In this part, we are going to show how to bring characters and animation clips from `Adobe Mixamo <https://www.mixamo.com/#/>`_ into ``Omniverse Create``

0. Requirements
#######################################

.. warning::

    Please refer to the licenses (:ref:`Licenses`) if necessary.

* `Adobe Mixamo <https://www.mixamo.com/#/>`_
* `Autodesk Maya 2023 <https://www.autodesk.com/products/maya/overview>`_ (We the Maya version >= 2022) to import ``mayaUSD`` module.
* `Nvidia Omniverse <https://www.nvidia.com/en-us/omniverse/>`_



1. Download character & Animation from MIXAMO
#######################################################################

Visit `Adobe Mixamo <https://www.mixamo.com/#/>`_, then save the character (e.g. peasant_girl.fbx) and the animation clip (e.g. Silly Dancing.fbx)

.. figure:: ./img/mixamo.png
   :alt: log image
   :width: 50%

.. note::

    The ``animation clip`` can be saved with skeletal animation only (without skin).


2. Import FBX into maya

.. code-block:: python

    import maya.cmds as cmds
    cmds.file("E:/researches/VRKitchen2.0-Tutorial/asset/mixamo/peasant_girl.fbx", i=True, type='Fbx')