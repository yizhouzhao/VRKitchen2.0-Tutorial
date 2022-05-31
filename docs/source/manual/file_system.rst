File system
--------------------------------------------------

We introduce how to provide a coding solution to the Omniverse file system. The modules listed below are originally derived from ``USDContext`` module. The original documentation can be found `here <https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.usd/docs/index.html?highlight=new_stage#omni.usd.UsdContext.new_stage>`_.

Get started by importing the ``omni`` package:

.. code-block:: python

    import omni

.. note::

    If you would like to call with `corountine`, please ``import asyncio`` and run it with
    
    .. code-block:: python

        import asyncio
        asyncio.ensure_future(<your async function>)

New Stage
#########################

.. code-block:: python

    await omni.usd.get_context().new_stage_async()