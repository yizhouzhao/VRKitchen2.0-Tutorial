Timeline & Update
--------------------------------------------------

Get timeline
#########################

.. code-block:: python

    from omni.timeline import get_timeline_interface
    timeline_iface = get_timeline_interface()

Play timeline
#########################

.. code-block:: python

    timeline_iface.play()

Pause timeline
#########################

.. code-block:: python

    timeline_iface.pause()

Stop timeline
#########################

.. code-block:: python

    timeline_iface.stop()

Update timeline
#########################

.. code-block:: python

    timeline_iface.set_auto_update(False) 

    for i in range(nun_frame):
        timeline_iface.forward_one_frame()

Set up time
#########################

.. code-block:: python

    # timeline_iface = get_timeline_interface()
    # timeline_iface.play()
    # timeline_iface.set_auto_update(False)
    timeline_iface.set_current_time(seconds)

Set/Get timeline range
#########################

.. code-block:: python

    stage.SetStartTimeCode(10) 
    # stage.GetStartTimeCode() 
    
    stage.SetEndTimeCode(100)
    # stage.GetEndTimeCode()

Loop/Cancel timeline 
#########################

.. code-block:: python

    timeline.set_looping(True) # False