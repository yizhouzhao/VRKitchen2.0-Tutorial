# utilities

import omni
from pxr import Gf
import carb
import numpy

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
     
