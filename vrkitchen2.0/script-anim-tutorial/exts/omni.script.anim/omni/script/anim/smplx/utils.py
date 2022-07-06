# utilities

import omni
from pxr import Gf
import carb
import numpy

import omni.anim.graph.core as ag

from .constants import *

def generate_trans_and_rots_for_pose_provider(joint_info = idle_joint2info):
    print("generate_trans_and_rots_for_pose_provider") 

    # flatten list
    joint_info = {key: list(numpy.concatenate(value).flat) for key, value in joint_info.items()}

    # get joint simple name
    joint_name_list =  list(smplx_joint2path.keys())

    # reflexion matrix
    reflex_x_mat = Gf.Matrix4f(-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)

    # get translate and rotation for all joints
    trans = []
    quads = []
    for i in range(smplx_joint_num):
        joint_name = joint_name_list[i]

        # # reflexion
        # if "left" in joint_name:
        #     refer_name = joint_name.replace("left", "right")
        # elif "right" in joint_name:
        #     refer_name = joint_name.replace("right", "left")        
        # else:
        refer_name = joint_name

        if refer_name in joint_info:
            mat = reflex_x_mat * Gf.Matrix4f(*joint_info[refer_name]).GetTranspose() * reflex_x_mat
            t = mat.ExtractTranslation()
            r = mat.ExtractRotationQuat()

            trans.append(carb.Float3(t[0],t[1],t[2]))
            quads.append(carb.Float4(r.imaginary[0], r.imaginary[1], r.imaginary[2], r.real))
        else:
            trans.append(carb.Float3(0,0,0)) #
            quads.append(carb.Float4(0, 0, 0, 1))

    print("trans, quads", len(trans), len(quads), trans, quads)
    return trans, quads
     
def get_trans_and_rots_for_pose_provider(
        joint_info = idle_joint2info, 
        character_path_str= "/World/smplx",
        ):
    """
    Get joint transform information for joints in joint_info:
    ::params:
        joint_info: joint names
        character_path_str: character prim path
        # relative_to_root: if true, compute the transform relative to skeleton root
    """
    # get character
    c = ag.get_character(character_path_str)

    def get_mat_from_joint(joint_name):
        pos = carb.Float3(0.0, 0.0, 0.0)
        rot = carb.Float4(0.0, 0.0, 0.0, 0.0)
        c.get_joint_transform(joint_name, pos, rot)

        # print("get_mat_from_joint", joint_name, "pos, rot", pos, rot)
 
        # get joint world transform matrix
        mat = Gf.Matrix4f(1.0)
        mat.SetRotate(Gf.Quatf(rot[3], rot[0], rot[1], rot[2]))
        mat.SetTranslateOnly(Gf.Vec3f(pos[0], pos[1], pos[2]))

        return mat

    # FIXME: make sure where the root transform stays as identity
    # root_mat = get_mat_from_joint("root")
    # print("root pos rot", root_mat.ExtractTranslation(), root_mat.ExtractRotationQuat())
    joint2mat = {}  # Gf.Matrix4f(1.0) # "root": root_mat
    # loop joints that are necessary
    for joint in joint_info:
        mat = get_mat_from_joint(joint)

        # if relative_to_root:
        #     # parent_joint = smplx_joint2parent[joint]
        #     # print("joint2mat: ", joint2mat)
        #     mat_r = mat * root_mat.GetInverse()
        #     joint2mat[joint] = mat_r
        # else: 

        # parent_joint = smplx_joint2parent[joint]
        # mat_r = mat * joint2mat[parent_joint] 
        joint2mat[joint] = mat

        # m = joint2mat[joint]
        # print(joint, m.ExtractTranslation(), m.GetRow(2),  m.GetRow(1))
    
    # print("joint2mat", joint2mat) 
    # del joint2mat["root"]
    return joint2mat






