Toolkit overview
===============================================================

To facilitate the study of **indoor scene building** methods and their potential
applications for `robotics`, `animation`, and `Embodied AI`, we introduce VRKITCHEN2.0: a toolkit built by NVIDIA OMNIVERSE that provides flexible pipelines for indoor scene building, scene randomizing, and robotic controls. 

Besides, by combining Python coding in the animation software VRKITCHEN2.0 can assist researches in
creating real-time training and control for robotics in the future.

Demo 1: Build customized high-quality indoor scenes
################################################################

Embodied artificial intelligence (EAI) has attracted significant attention, both in advanced deep
learning models and algorithms and the rapid development of simulated platforms. Many open challenges have been proposed to facilitate EAI research. A critical bottleneck in existing simulated platforms is the **limited number of indoor scenes** that support vision-and-language navigation, object interaction, and complex household tasks.

In this tutoral: :ref:`Tutorial Indoor`, we shall present how to import tens of thousands of room layouts from the original `3D-Front dataset` into `Omniverse` to give a photo-realistic effect for EAI tasks.

.. image:: ./img/scene_demo1.*
   :alt: scene_demo1
   :width: 100%

Demo 2: Parsing articulated objects
################################################################

Articulated objects can be defined as objects composed of more than one rigid parts. In our daily life, humans are constantly interacting with a lot of articulated objects such as *door, keyboard, light switch,* and e.t.c. The rigidbody, softbody, articulated object, and liquid compose a large part of our interaction with the world.

In this tutorial: :ref:`Tutorial Articulated Object`, we present how to parse articulated objects in SAPIEN :cite:`xiang2020sapien` (a realistic and physics-rich simulated environment) into `Omniverse`, and present their potential applications for dynmaic controls in the virtual environment.

.. image:: ./img/articulated_body1.png
   :alt: articulated_body1
   :width: 100%

.. bibliography:: ../refs.bib