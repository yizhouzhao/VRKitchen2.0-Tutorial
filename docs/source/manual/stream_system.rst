Stream 
--------------------------------------------------

This part includes the APIs for setting up physics in the event,

`read more about event streams <https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/event_streams.html?highlight=get_update_event_stream>`_

App update
#########################################################

.. code-block:: python

    self._update_sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
                self._on_update, name="omni.physx demo update"
            )

    def _on_update(self, e):
        # dt = e.payload["dt"]

Physics update
#########################################################

.. code-block:: python
    self._physics_update_sub = omni.physx.get_physx_interface().subscribe_physics_step_events(self._on_physics_step)
    
    def _on_physics_step(self, dt):
        # pass


Timeline event
#########################################################

.. code-block:: python

    stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
    self._timeline_sub = stream.create_subscription_to_pop(self._on_timeline_event)

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.STOP):
            # pass

        
Stage event
#########################################################

.. code-block:: python
    stage_event_stream = self._usd_context.get_stage_event_stream()
            self._stage_event_sub = stage_event_stream.create_subscription_to_pop(self._on_stage_event)


    def _on_stage_event(self, event):
        if event.type is int(omni.usd.StageEventType.CLOSING):
            # pass

