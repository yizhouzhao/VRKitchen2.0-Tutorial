# geo

from pxr import Gf

from .utils import interpolate_mat


class CuboidMap:
    def __init__(self, resolution) -> None:
        self.Resolution = resolution

        self.Pivot = None
        self.Points = []
        self.References = []
        self.Occupancies = []
        self.Size = Gf.Vec3f(1.0)

        self.Generate()

    def Generate(self):
        for y in range(self.Resolution[1]):
            for x in range(self.Resolution[0]):
                for z in range(self.Resolution[2]):
                    self.Points.append([-0.5 + (x+0.5)/self.Resolution[0], -0.5 + (y+0.5)/self.Resolution[1], -0.5 + (z+0.5)/self.Resolution[2]])
                    self.References.append([Gf.Vec3f(0)])
                    self.Occupancies.append(0)


    def GetDimensionality(self):
        return self.Resolution[0] * self.Resolution[1] * self.Resolution[2]

    
    def Sense(self, pivot, size, smoothing):
        self.Pivot = interpolate_mat( 1 - smoothing, self.Pivot, pivot) 
        pivotPosition = self.Pivot.ExtractTranslation()
        Size = Gf.Vec3f(0)

        for i in range(len(self.Points)):
            self.References[i] = pivotPosition
            self.Occupancies[i] = 0

