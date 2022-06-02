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


String UI
#########################

.. code-block:: python

    ui.Label("Scene folder: ", width=20)
    self.scene_asset_path_ui = omni.ui.StringField(height=20, style={ "margin_height": 4 })
    self.scene_asset_path_ui.model.set_value(SCENE_ASSET_PATH)

    # get string
    self.scene_asset_path_ui.model.get_value_as_string()


Integer UI
#########################

.. code-block:: python

    ui.Label("Example id: ", width=20)
    self.example_id_ui = omni.ui.IntField(height=20, style={ "margin_height": 8 })

    # get int
    self.example_id_ui .model.get_value_as_int()