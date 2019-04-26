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

class _Object:
    def __init__(self, dataset, name):
        self.dataset = dataset
        self.name = name
        self.info_states = None
        return
        
    @util.DatasetAttribute()
    def Description(self): return self.name+"Description"
    
    @util.DatasetVariable()
    def Position(self): return self.name+"Position"
    @util.DatasetVariable()
    def View(self): return self.name+"View"
    @util.DatasetVariable()
    def Up(self): return self.name+"Up"

    def _create_coordinates(self):
        if self.info_states.Position is not State.Unused: 
            self.Position = getattr(dimensions.Definitions, self.name)(self.info_states.Position)
        if self.info_states.View is not State.Unused: 
            self.View = getattr(dimensions.Definitions, self.name)(self.info_states.View)
        if self.info_states.Up is not State.Unused: 
            self.Up = getattr(dimensions.Definitions, self.name)(self.info_states.Up)

class SingleObject(_Object):
    def define(self, info_states):
        self.info_states = info_states
        _Object._create_coordinates(self)
        return

    def set_default_Position(self, value=None, coordinate_type=None, coordinate_units=None):
        if value == None: value=default_values["Position"]
        if coordinate_type == None: coordinate_type=default_values["Coordinates"]
        if coordinate_units == None: coordinate_units=dimensions.default_units[coordinate_type]
        for m in np.arange(self.Position.get_dims()[0].size):
            self.Position[m,:]=value
        self.Position.Type = str(coordinate_type)
        self.Position.Units = str(coordinate_units)

    def set_default_View(self, value=None):
        if value == None: value=default_values["View"]
        for m in np.arange(self.View.get_dims()[0].size):
            self.View[m,:]=value

    def set_default_Up(self, value=None):
        if value == None: value=default_values["Up"]
        for m in np.arange(self.Up.get_dims()[0].size):
            self.Up[m,:]=value

class MultiObject(_Object):
    def define(self, count, info_states):
        self.info_states = info_states

        if dimensions.Definitions.names[self.name] not in self.dataset.dimensions.keys():
            self.dataset.createDimension(dimensions.Definitions.names[self.name], count)
        _Object._create_coordinates(self)
        return
        
    def set_default_Position(self, value=None, coordinate_type=None, coordinate_units=None):
        if value == None: value=default_values["Position"]
        if coordinate_type == None: coordinate_type=default_values["Coordinates"]
        if coordinate_units == None: coordinate_units=dimensions.default_units[coordinate_type]
        for i in np.arange(self.Position.get_dims()[0].size):
            for m in np.arange(self.Position.get_dims()[2].size):
                self.Position[i,:,m]=value
        self.Position.Type = str(coordinate_type)
        self.Position.Units = str(coordinate_units)

    def set_default_View(self, value=None):
        if value == None: value=default_values["View"]
        for i in np.arange(self.View.get_dims()[0].size):
            for m in np.arange(self.View.get_dims()[2].size):
                self.View[i,:,m]=value

    def set_default_Up(self, value=None):
        if value == None: value=default_values["Up"]
        for i in np.arange(self.Up.get_dims()[0].size):
            for m in np.arange(self.Up.get_dims()[2].size):
                self.Up[i,:,m]=value
