# utils function
import omni
from pxr import UsdGeom, Gf, Sdf

import numpy as np 

from omni.usd import get_world_transform_matrix, get_local_transform_matrix

def generate_capsule(p1: Gf.Vec3d, p2: Gf.Vec3d, prim_path_str: str):
    mid_point = (p1 + p2) / 2.0

    # generate capsule prim
    stage = omni.usd.get_context().get_stage()

    # prim = stage.DefinePrim(prim_path_str, "Capsule")

    a = np.array([0, 0, 1])
    b = np.array(p2 - p1)

    b_norm = np.linalg.norm(b)

    b = b / b_norm

    print("mid_point", mid_point)
    print("b_norm", b_norm, a, b) 

    r = get_rodrigues_rotation_matrix(b, a)

    # mat = Gf.Matrix4d()
    # get_world_transform_matrix(prim)


    mat = Gf.Matrix4d(r[0][0], r[0][1], r[0][2], 0, 
            r[1][0], r[1][1], r[1][2], 0, 
            r[2][0], r[2][1], r[2][2], 0, 
            0, 0, 0, 1)
    
    mat = mat * Gf.Matrix4d().SetScale(b_norm / 2) * Gf.Matrix4d().SetTranslate(mid_point)

    print("mat", mat)

    omni.kit.commands.execute(
        "TransformPrimCommand",
        path=prim_path_str,
        new_transform_matrix=mat,
    )


def get_rodrigues_rotation_matrix(a, b):
    '''
    Get the rotation matrix for rotate a to b
    '''
    # https://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
    v = np.cross(a, b) 
    s = np.linalg.norm(v) 
    c = np.dot(a, b) 
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]) 
    r = np.eye(3) + vx + np.matmul(vx, vx) * (1-c)/(s**2) 
    print("rotation matrix", r)

    return r