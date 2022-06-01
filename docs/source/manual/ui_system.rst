UI
--------------------------------------------------

The UI system allows you to build up your own graphics control. 

Learn more about `Omniverse omni.ui <https://docs.omniverse.nvidia.com/py/kit/source/extensions/omni.ui/docs/index.html>`_

.. note::
    Get started by importing the ``omni.ui``:

    .. code-block:: python

        import omni.ui as ui

Build window
#########################

.. code-block:: python

    self._window = ui.Window("VRKitchen Asset Importer", width=500, height=300)
    with self._window.frame:
        with ui.VStack():
            with ui.HStack(height=30):
                ui.Label("Welcome!", width=200)