# utils function
import omni
from pxr import UsdGeom, Gf, Sdf, UsdPhysics

import numpy as np 

from omni.usd import get_world_transform_matrix, get_local_transform_matrix

def generate_capsule(p1: Gf.Vec3d, p2: Gf.Vec3d, prim_path_str: str):
    mid_point = (p1 + p2) / 2.0

    # generate capsule prim
    stage = omni.usd.get_context().get_stage()

    prim = stage.DefinePrim(prim_path_str, "Capsule")

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

    # set local scale
    prim.GetAttribute("xformOp:scale").Set(Gf.Vec3f([0.1, 0.1, 0.1]))

    # set capsule height and radius , 0.5, 1    
    prim.GetAttribute("height").Set(10 * b_norm - 1)

    

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


def generate_d6_joint(from_prim_str:str, to_prim_str: str, joint_name: str):
    '''
    Generate d6 joint 
    '''
    # generate capsule prim
    stage = omni.usd.get_context().get_stage()

    from_prim = stage.GetPrimAtPath(from_prim_str)
    to_prim = stage.GetPrimAtPath(to_prim_str)
    
    component = UsdPhysics.Joint.Define(stage, joint_name)
    prim = component.GetPrim()
    for limit_name in ["transX", "transY", "transZ"]:
        limit_api = UsdPhysics.LimitAPI.Apply(prim, limit_name)
        limit_api.CreateLowAttr(1.0)
        limit_api.CreateHighAttr(-1.0)
    for limit_name in ["rotX", "rotY", "rotZ"]:
        limit_api = UsdPhysics.LimitAPI.Apply(prim, limit_name)
        limit_api.CreateLowAttr(-45.0)
        limit_api.CreateHighAttr(45.0)

    xfCache = UsdGeom.XformCache()

    to_pose = xfCache.GetLocalToWorldTransform(to_prim)
    from_pose = xfCache.GetLocalToWorldTransform(from_prim)
    rel_pose = to_pose * from_pose.GetInverse()
    pos1 = Gf.Vec3f(rel_pose.ExtractTranslation())
    #rot1 = Gf.Quatf(rel_pose.ExtractRotationQuat())

    component.CreateBody0Rel().SetTargets([to_prim.GetPath()])
    component.CreateBody1Rel().SetTargets([from_prim.GetPath()])
    component.CreateLocalPos1Attr().Set(Gf.Vec3f(0.0))
    component.CreateLocalRot1Attr().Set(Gf.Quatf(1.0))
    component.CreateLocalPos0Attr().Set(-pos1)
    component.CreateLocalRot0Attr().Set(Gf.Quatf(1.0))

    return component


def generate_fixed_joint(from_prim_str:str, to_prim_str: str, joint_name: str):
    stage = omni.usd.get_context().get_stage()

    from_prim = stage.GetPrimAtPath(from_prim_str)

    component = UsdPhysics.FixedJoint.Define(stage, joint_name)
    component.CreateBody1Rel().SetTargets([from_prim.GetPath()])

    if to_prim_str:
        to_prim = stage.GetPrimAtPath(to_prim_str)
        component.CreateBody0Rel().SetTargets([to_prim.GetPath()])

        xfCache = UsdGeom.XformCache()

        to_pose = xfCache.GetLocalToWorldTransform(to_prim)
        from_pose = xfCache.GetLocalToWorldTransform(from_prim)
        rel_pose = to_pose * from_pose.GetInverse()
        pos1 = Gf.Vec3f(rel_pose.ExtractTranslation())
        rot1 = Gf.Quatf(rel_pose.ExtractRotationQuat())

        component.CreateBody0Rel().SetTargets([to_prim.GetPath()])
        component.CreateBody1Rel().SetTargets([from_prim.GetPath()])
        component.CreateLocalPos0Attr().Set(Gf.Vec3f(0.0))
        component.CreateLocalRot0Attr().Set(Gf.Quatf(1.0))
        component.CreateLocalPos1Attr().Set(pos1)
        component.CreateLocalRot1Attr().Set(rot1)

    return component