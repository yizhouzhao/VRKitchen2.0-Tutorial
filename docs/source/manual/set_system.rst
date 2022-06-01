Settings
--------------------------------------------------

The original documentation can be found `here <https://docs.omniverse.nvidia.com/py/kit/docs/api/carb/carb.settings.html?highlight=carb%20settings#module-carb.settings>`_


Get app title
#########################

.. code-block:: python

    import carb
    app_name = carb.settings.get_settings().get("/app/window/title")
    # Isaac Sim, Create, Code, e.t.c.

Get app version
#########################

.. code-block:: python

    import carb
    app_version = str(carb.settings.get_settings().get("/app/version"))
    # 2022.1.1, e.t.c.




