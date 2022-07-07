# utilities

from msilib.schema import tables

from matplotlib import table
import omni
from pxr import Gf
import carb
import numpy

import omni.anim.graph.core as ag

from .constants import *

# reflexion matrix
reflex_x_mat = Gf.Matrix4f(-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)

def get_mat_from_joint(joint_name, c):
    pos = carb.Float3(0.0, 0.0, 0.0)
    rot = carb.Float4(0.0, 0.0, 0.0, 0.0)
    c.get_joint_transform(joint_name, pos, rot)

    # print("get_mat_from_joint", joint_name, "pos, rot", pos, rot)

    # get joint world transform matrix
    mat = Gf.Matrix4f(1.0)
    mat.SetRotate(Gf.Quatf(rot[3], rot[0], rot[1], rot[2]))
    mat.SetTranslateOnly(Gf.Vec3f(pos[0], pos[1], pos[2]))

    return mat

def generate_trans_and_rots_for_pose_provider(joint_info = idle_joint2info):
    print("generate_trans_and_rots_for_pose_provider") 

    # flatten list
    joint_info = {key: list(numpy.concatenate(value).flat) for key, value in joint_info.items()}

    # get joint simple name
    joint_name_list =  list(smplx_joint2path.keys())

    

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
     
def set_pose(positions, forwards, upwards, velocities, character_path_str= "/World/smplx"):
        """
        Set idle pose as init for the character
        """
        # get character
        c = ag.get_character(character_path_str)

        # get joint simple name
        joint_name_list =  list(smplx_joint2path.keys())

        # get necessary joint list
        need_joint_list = list(idle_joint2info.keys())

       # get translate and rotation for all joints
        trans = []
        quats = []
        
        joint2mat = {"root": Gf.Matrix4f(1.0)}
        # joint2mat_ori =  {"root": Gf.Matrix4f(1.0)}
        for j in range(smplx_joint_num):
            joint_name = joint_name_list[j]

            if joint_name in need_joint_list:
                i = need_joint_list.index(joint_name)
            
                pos = positions[i]
                z_axis = forwards[i]
                y_axis = upwards[i]
                x_axis = Gf.Cross(y_axis, z_axis)

                # get current transform
                # t0 = carb.Float3(0.0, 0.0, 0.0)
                # r0 = carb.Float4(0.0, 0.0, 0.0, 0.0)
                # c.get_joint_transform(joint_name, t0, r0)

                # mat_ori = get_mat_from_joint(joint_name, c) * reflex_x_mat
                # t0 = mat_ori.ExtractTranslation()

                # mat_ori = get_mat_from_joint(joint_name, c)

                # mat = Gf.Matrix4f(
                #         x_axis[0], x_axis[1], x_axis[2], 0, \
                #         y_axis[0], y_axis[1], y_axis[2], 0, \
                #         z_axis[0], z_axis[1], z_axis[2], 0, \
                #         0.5 * (t0[0] + velocities [i][0] / 30 + pos[0]), \
                #             0.5 * (t0[1] + velocities [i][1] / 30 + pos[1]), 
                #                 0.5 * (t0[2] + velocities [i][2] / 30 + pos[2]), 1,
                #     )

                mat = Gf.Matrix4f(
                        x_axis[0], x_axis[1], x_axis[2], 0, \
                        y_axis[0], y_axis[1], y_axis[2], 0, \
                        z_axis[0], z_axis[1], z_axis[2], 0, \
                        pos[0], pos[1], pos[2], 1
                    )


                joint2mat[joint_name] = mat

                joint_parent = smplx_joint2parent[joint_name]

                mat_relative = reflex_x_mat * mat * joint2mat[joint_parent].GetInverse() * reflex_x_mat 
            
                # print("bone mat_relative ", joint_name, mat_relative.ExtractTranslation())


                t = mat_relative.ExtractTranslation()
                r = mat_relative.ExtractRotationQuat()

                # joint2mat_ori[joint_name] = mat_ori
                # mat_ori_relative = mat_ori * joint2mat[joint_parent].GetInverse() 
                # t0 = mat_ori_relative.ExtractTranslation()
                # t0 = carb.Float3(0.0, 0.0, 0.0)
                # r0 = carb.Float4(0.0, 0.0, 0.0, 0.0)
                # c.get_joint_transform(joint_name, t0, r0)

                # TODO: interpolate
                # t_interpolated = Gf.Lerp(0.5, Gf.Vec3f(t[0], t[1], t[2]), t)
                # print("t t0", t, t0)

                trans.append(carb.Float3(t[0], t[1], t[2]))
                quats.append(carb.Float4(r.imaginary[0], r.imaginary[1], r.imaginary[2], r.real))
            else:
                # root_mat = joint2mat["root"]
                trans.append(carb.Float3(0,0,0)) #
                quats.append(carb.Float4(0, 0, 0, 1))

        # print("new trans quats", len(trans), len(quats), trans, quats)
        return trans, quats


        # trans, quats = generate_trans_and_rots_for_pose_provider(joint2info)
        # for jj, t in enumerate(trans):
        #     self.character.set_variable("poses", trans)
        #     self.character.set_variable("rots", quats)
    
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


    # FIXME: make sure where the root transform stays as identity
    # root_mat = get_mat_from_joint("root")
    # print("root pos rot", root_mat.ExtractTranslation(), root_mat.ExtractRotationQuat())
    joint2mat = {}  # Gf.Matrix4f(1.0) # "root": root_mat
    # loop joints that are necessary
    for joint in joint_info:
        mat = get_mat_from_joint(joint, c)

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






