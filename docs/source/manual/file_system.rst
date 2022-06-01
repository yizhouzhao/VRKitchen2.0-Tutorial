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
    await omni.kit.app.get_app().next_update_async()

Or the blocking call:

.. code-block:: python

    omni.usd.get_context().new_stage()

Open stage
##########################

.. note::

    The Omniverse uses the scene file with `.usd` format

.. code-block:: python

    usd_path = "<your usd file>.usd"
    success, error = await omni.usd.get_context().open_stage_async(usd_path)
    if not success:
        raise Exception(f"Failed to open usd file: {error}")

Or the blocking call:

.. code-block:: python

    omni.usd.get_context().open_stage(usd_path)


Close stage
##########################

.. code-block:: python

    (result, err) = await omni.usd.get_context().close_stage_async()
    # Assert result == True

Or the blocking call:

.. code-block:: python

    omni.usd.get_context().close_stage()


Reopen stage
##########################

.. code-block:: python

    (result, err) = await omni.usd.get_context().reopen_stage_async()
    # Assert result == True

Or the blocking call:

.. code-block:: python

    omni.usd.get_context().reopen_stage()


Save stage
##########################

.. code-block:: python

    save_file_path = os.path.join(tmpdirname, "<your save path>.usda")
    (result, err, saved_layers) = await omni.usd.get_context().save_as_stage_async(save_file_path)
    # Assert result == True

Or the blocking call:

.. code-block:: python

    omni.usd.get_context().save_as_stage(save_file_path)


Export stage
##########################

.. code-block:: python

    save_file_path = os.path.join(tmpdirname, "<your save path>.usda")
    (result, err) = await omni.usd.get_context().export_as_stage_async(save_file_path)
    # Assert result == True

Or the blocking call:

.. code-block:: python

    omni.usd.get_context().export_as_stage(save_file_path)




