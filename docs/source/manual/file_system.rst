File system
--------------------------------------------------

We introduce how to provide a coding solution to the Omniverse file system. The modules listed below are originally derived from ``USDContext`` module. The original documentation can be found `here <https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.usd/docs/index.html?highlight=new_stage#omni.usd.UsdContext.new_stage>`_.

Get started by importing the ``omni`` package:

.. code-block::

    import omni

New Stage
#########################

.. code-block::

    await omni.usd.get_context().new_stage_async()