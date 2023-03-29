Mesh
--------------------------------------------------

This part works with UsdGeom, UsdMesh, e.t.c.

Get mesh from prim
##############################

.. code-block:: python

    mesh = UsdGeom.Mesh(prim)

Get face and point information
##############################

.. code-block:: python

    vertex_points = mesh.GetPointsAttr().Get()
    vertex_counts = mesh.GetFaceVertexCountsAttr().Get()
    vertex_indices = mesh.GetFaceVertexIndicesAttr().Get()