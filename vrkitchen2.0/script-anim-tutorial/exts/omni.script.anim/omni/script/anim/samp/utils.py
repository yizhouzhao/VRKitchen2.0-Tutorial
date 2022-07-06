# util
from pxr import Gf

def reflect_mat(mat, axis = "x"):
    reflex_x_mat = Gf.Matrix4f(-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    return  mat * reflex_x_mat

def interpolate_mat(alpha, m1, m2):
    p1 = m1.ExtractTranslation()
    p2 = m2.ExtractTranslation()

    r1 = m1.ExtractRotationQuat()
    r2 = m2.ExtractRotationQuat() 
    
    p = Gf.Lerp(alpha, p1, p2)
    r = Gf.Quatf(Gf.Slerp(alpha, r1, r2))

    mat = Gf.Matrix4f(1.0)
    mat.SetRotate(r)
    mat.SetTranslateOnly(p)

    return mat