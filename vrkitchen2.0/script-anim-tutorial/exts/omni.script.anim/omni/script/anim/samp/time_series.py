# time series
import enum

from pxr import Gf


class TimeSeries:
    def __init__(self, pastKeys: int, futureKeys: int, 
            pastWindow: float,  futureWindow: float,  resolution: int):
        self.Pivot = 0
        self.Resolution = 0
        self.PastWindow = 0
        self.FutureWindow = 0

        samples = pastKeys + futureKeys + 1
        self.keycount = samples

        if samples == 1 and resolution != 1:
            resolution = 1
            print("Resolution corrected to 1 because only one sample is available.")

        self.Samples = []
        self.Pivot = pastKeys * resolution
        self.Resolution = resolution

        for i in range(self.Pivot):
            self.Samples.append(Sample(i, -pastWindow + i*pastWindow/(pastKeys*resolution)))
        
        self.Samples.append(Sample(self.Pivot, 0))

        for i in range(self.Pivot + 1, (samples-1)*resolution+1):
            self.Samples.append(Sample(i, (i-self.Pivot)*futureWindow/(futureKeys*resolution)))

        self.PastWindow = pastWindow
        self.FutureWindow = futureWindow

        # series
        self.Data = []


class Sample:
    def __init__(self, index, timestamp) -> None:
        self.index = index
        self.timestamp = timestamp


class Series:
    def __init__(self) -> None: 
        self.ID = "Root"  # {Root, Style, Goal, Contact, Phase, Alignment, Length}
        self.TimeSeries = None

class Root (Series):
    def __init__(self, timeSeries: TimeSeries) -> None:
        super().__init__()
        timeSeries.Data.append(self)
        self.Transformations = []
        self.Velocities = []
        for i in range(len(timeSeries.Samples)):
            self.Transformations.append(Gf.Matrix4f().SetIdentity())
            self.Velocities.append(Gf.Vec3f(0))
       
        
        self.Speeds = []

    def GetID(self):
        return "Root"
    

class Style (Series):
    def __init__(self, timeSeries: TimeSeries, styles: list) -> None:
        super().__init__()
        timeSeries.Data.append(self)
        self.Styles = styles
        self.Values = [[0 for j in range(len(styles))] for i in range(len(timeSeries.Samples))]

    def GetID(self):
        return "Style"

class Goal (Series):
    def __init__(self, timeSeries: TimeSeries, actions: list) -> None:
        super().__init__()
        timeSeries.Data.append(self)
        self.Transformations = []
        self.Actions = actions
    
        for i in range(len(timeSeries.Samples)):
            self.Transformations.append(Gf.Matrix4f().SetIdentity())
        
        self.Values = [[0 for j in range(len(actions))] for i in range(len(timeSeries.Samples))]

    def GetID(self):
        return "Goal"

class Contact (Series):
    def __init__(self, timeSeries: TimeSeries, bones: list) -> None:
        super().__init__()
        timeSeries.Data.append(self)
        self.Indices = []
        self.Bones = bones
        self.Values = [[0 for j in range(len(bones))] for i in range(len(timeSeries.Samples))]

    def GetID(self):
        return "Contact"