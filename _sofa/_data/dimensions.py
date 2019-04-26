from enum import Enum

class Coordinates(Enum):
    Cartesian = "cartesian"
    Spherical = "spherical"

default_units = {
    Coordinates.Cartesian : "meter",
    Coordinates.Spherical : "degree, degree, meter",
    "frequency" : "hertz"
    }

class Access:
    def __init__(self, dataset):
        self.dataset = dataset
        return
    
    @property
    def I(self): return self.dataset.dimensions["I"].size
    @property
    def C(self): return self.dataset.dimensions["C"].size
    @property
    def M(self): return self.dataset.dimensions["M"].size
    @property
    def R(self): return self.dataset.dimensions["R"].size
    @property
    def E(self): return self.dataset.dimensions["E"].size
    @property
    def N(self): return self.dataset.dimensions["N"].size
    @property
    def S(self): return self.dataset.dimensions["S"].size
    
class Definitions:
    def Listener(varies=False):
        if varies: return ("M","C",)
        return ("I","C",)
    def Source(varies=False):
        if varies: return ("M","C",)
        return ("I","C",)
    
    
    def Receiver(varies=False):
        if varies: return ("R","C","M",)
        return ("R","C","I",)
    def Emitter(varies=False):
        if varies: return ("E","C","M",)
        return ("E","C","I",)
    
    
    def RoomCorner(varies=False):
        if varies: return ("M","C",)
        return ("I","C",)
    
    
    def DataValues(datatype):
        if datatype is "FIRE": return ("M","R","E","N",)
        return ("M","R","N",)
    def DataDelay(datatype, varies=False):
        tup = ("I","R",)
        if varies: tup = ("M","R",)
        if datatype is "FIRE": return tup+("E",)
        return tup
    def DataSamplingRate(datatype):
        return ("I",)
    def DataFrequencies(datatype):
        return ("N",)
    
    names = {
        "Receiver" : "R",
        "Emitter" : "E"
        }
