# Copyright (c) 2019 Jannika Lossner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__all__ =["Coordinates", "Set", "Object"]

from . import dimensions

from .. import _access as access
from .. import _util as util
from enum import Enum
import numpy as np


class Coordinates(access.VariableAccessWithUnits):
    class System(Enum):
        Cartesian = "cartesian"
        Spherical = "spherical"

    class State(Enum):
        Unused = None
        Fixed = False
        Varying = True
        def is_used(state): return state !=Coordinates.State.Unused

    def __init__(self, dataset, obj_name, descriptor):
        access.VariableAccess.__init__(self, dataset, obj_name+descriptor)
        self.obj_name = obj_name
        self.descriptor = descriptor

    @property
    def Type(self): return self._Matrix.Type
    @Type.setter
    def Type(self, value): self._Matrix.Type = value

    def set_system(self, ctype=None, cunits=None):
        if ctype == None: ctype = System.Cartesian
        self.Type = str(ctype)
        if cunits == None: cunits=dimensions.default_units[ctype]
        self.Units = str(cunits)
    #TODO: get in specified coordinate system, get local coordinates as global coordinates         

class Set:
    """Descriptors or data for a spatial entity (Listener, Source, Receiver, Emitter)"""

    def __init__(self, Position, View=Coordinates.State.Unused, Up=Coordinates.State.Unused):
        """Parameters
        ----------
        Position : :class:'InfoState'
        View : :class:'InfoState', optional
        Up : :class:'InfoState', optional
        """
        self._Position=Position
        self._View=View
        self._Up=Up

    @property
    def Position(self): return self._Position
    @Position.setter
    def Position(self, value): self._Position = value
    @property
    def View(self): return self._View
    @View.setter
    def View(self, value): self._View = value
    @property
    def Up(self): return self._Up
    @Up.setter
    def Up(self, value): self._Up = value

class Object:
    def __init__(self, database, name):
        self.database = database
        self.name = name
        return

    @property
    def dataset(self): return self.database.dataset
        
    @util.DatasetAttribute()
    def Description(self): return self.name+"Description"
    
    @property
    def Position(self): return Coordinates(self.dataset, self.name, "Position")
    @property
    def View(self): return Coordinates(self.dataset, self.name, "View")
    @property
    def Up(self): return Coordinates(self.dataset, self.name, "Up")

    def initialize(self, info_states, count=None):
        if count == None: 
            if "count" in self.database._convention.default_objects[self.name].keys(): 
                count = self.database._convention.default_objects[self.name]["count"]
            else: raise Exception(self.name, "count missing!")
        print(self.name, "count = ", str(count))
        self.database._convention.validate_spatial_object_settings(self.name, info_states, count)

        if self.name == "Emitter" or self.name == "Receiver":
            if dimensions.Definitions.names[self.name] not in self.dataset.dimensions.keys():
                self.dataset.createDimension(dimensions.Definitions.names[self.name], count)
        self._create_coordinates(info_states)
        self.database._convention.set_default_spatial_values(self)

    def _create_coordinates(self, info_states):
        rd = tuple(x for x in getattr(dimensions.Definitions, self.name)(Coordinates.State.Varying) if x!="C")
        if info_states.Position != Coordinates.State.Unused: 
            self.Position._Matrix = getattr(dimensions.Definitions, self.name)(info_states.Position)
        if info_states.View != Coordinates.State.Unused: 
            self.View._Matrix = getattr(dimensions.Definitions, self.name)(info_states.View)
        if info_states.Up != Coordinates.State.Unused: 
            self.Up._Matrix = getattr(dimensions.Definitions, self.name)(info_states.Up)
