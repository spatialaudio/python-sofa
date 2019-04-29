from . import dimensions

from .. import _util as util
from enum import Enum
import numpy as np

class State(Enum):
    Unused = None
    Fixed = False
    Varying = True

class StateSet:
    def __init__(self, Position=State.Fixed, View=State.Unused, Up=State.Unused):
        self.Position=Position
        self.View=View
        self.Up=Up
        return

class Coordinates:
    def __init__(self, dataset, obj_name, descriptor):
        self.dataset = dataset
        self.name = obj_name
        self.descriptor = descriptor

    @util.DatasetVariable()
    def Values(self): return self.name+self.descriptor
    @property 
    def _ValuesM(self):
        if self.varies: return self.Values[:]
        sh = list(self.Values[:].shape)
        values = None
        if self.is_local():
            sh[2] = self.dataset.dimensions["M"].size
            values = np.empty(sh)
            for m in np.arange(self.dataset.dimensions["M"].size):
                values[:,:,m] = self.Values[:,:,0]
        else:
            sh[0] = self.dataset.dimensions["M"].size
            values = np.empty(sh)
            for m in np.arange(self.dataset.dimensions["M"].size):
                values[m,:] = self.Values[0,:]
        return values


    @property
    def Type(self): return self.Values.Type
    @Type.setter
    def Type(self, value): self.Values.Type = value

    @property
    def Units(self): return self.Values.Units
    @Type.setter
    def Units(self, value): self.Values.Units = value

    @property
    def varies(self):
        for d in self.Values.get_dims():
            if d.name == "M": return True
        return False
    
    def exists(self):
        return self.Values != None

    def is_local(self):
        if self.name == "Receiver": return True
        if self.name == "Emitter": return True
        return False

    def get(self, index=None):
        if not self.exists(): return None
        if not self.is_local(): return self._ValuesM[:]
        if index == None: return np.transpose(self._ValuesM[:])
        return np.transpose(self._ValuesM[index,:,:])

    def set_default(self, value, index=None, coordinate_type=None, coordinate_units=None):
        if coordinate_type is not None: 
            self.Type = str(coordinate_type)
            if coordinate_units == None: coordinate_units=dimensions.default_units[coordinate_type]
        if coordinate_units is not None: self.Units = str(coordinate_units)         

        if self.name == "Listener" or self.name == "Source":
            for m in np.arange(self.Values.get_dims()[0].size):
                self.Values[m,:]=value
        elif index == None:
            for m in np.arange(self.Values.get_dims()[2].size):
                for c in np.arange(self.Values.get_dims()[0].size):
                    self.Values[c,:,m]=value
        else: 
            for m in np.arange(self.Values.get_dims()[0].size):
                self.Values[index,:,m]=value

class _Object:
    def __init__(self, dataset, name):
        self.dataset = dataset
        self.name = name
        return
        
    @util.DatasetAttribute()
    def Description(self): return self.name+"Description"
    
    @property
    def Position(self): return Coordinates(self.dataset, self.name, "Position")
    @property
    def View(self): return Coordinates(self.dataset, self.name, "View")
    @property
    def Up(self): return Coordinates(self.dataset, self.name, "Up")

    def _create_coordinates(self, info_states):
        if info_states.Position is not State.Unused: 
            self.Position.Values = getattr(dimensions.Definitions, self.name)(info_states.Position)
        if info_states.View is not State.Unused: 
            self.View.Values = getattr(dimensions.Definitions, self.name)(info_states.View)
        if info_states.Up is not State.Unused: 
            self.Up.Values = getattr(dimensions.Definitions, self.name)(info_states.Up)

class SingleObject(_Object):
    def define(self, info_states):
        _Object._create_coordinates(self, info_states)
        return

class MultiObject(_Object):
    def define(self, count, info_states):
        if dimensions.Definitions.names[self.name] not in self.dataset.dimensions.keys():
            self.dataset.createDimension(dimensions.Definitions.names[self.name], count)
        _Object._create_coordinates(self, info_states)
        return
