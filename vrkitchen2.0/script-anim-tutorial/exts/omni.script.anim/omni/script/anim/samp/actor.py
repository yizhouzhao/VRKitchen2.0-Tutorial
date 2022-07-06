# actor and bone

from ..smplx.constants import idle_joint2info

class Actor():
    def __init__(self) -> None:
        self.Bones = []

        self.init_bones()
    
    def init_bones(self):
        for key in idle_joint2info:
            self.Bones.append(Bone(key))

class Bone():
    def __init__(self, name) -> None:
        self.name = name
        self.transform = None
        
        self.actor = None
        
        self.velocity = [0,0,0]
        