Log
--------------------------------------------------

Omniverse provides a easy-to-use log system. Users can either find logs from 

* Command prompt
* Omniverse console window
* Log file

.. figure:: ./img/log.png
   :alt: log image
   :width: 50%

To print a log:

.. code-block:: python

    import carb

    carb.log_error("")
    carb.log_warn("")

    carb.log_info("")
    # which equals
    print("")



