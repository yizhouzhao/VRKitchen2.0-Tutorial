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

