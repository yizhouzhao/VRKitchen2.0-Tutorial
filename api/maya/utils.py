from maya.cmds import *

def clear_keys():
    """Clear all keyframes for selection.
    
    :param a: The first arg.
    :param b: The second arg.
    
    :returns: Something.
    """

    objs = ls(selection=True)

    for obj in objs:
        print(obj)
        cutKey(obj, clear=True)



# file -force -options ";exportUVs=1;exportSkels=auto;exportSkin=auto;exportBlendShapes=0;exportDisplayColor=1;exportColorSets=1;defaultMeshScheme=catmullClark;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=200;frameStride=1;frameSample=0.0;defaultUSDFormat=usda;parentScope=;shadingMode=useRegistry;convertMaterialsTo=[UsdPreviewSurface];exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;stripNamespaces=0" -type "USD Export" -pr -ea "C:/Users/Yizhou Zhao/Desktop/usd/remy2.usd";
