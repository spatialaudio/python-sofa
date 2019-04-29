from .base import _Base

from .. import _data as data
from .. import _rooms as rooms

import numpy as np

### incomplete! Requires extending the data access to include per-measurement strings
class SimpleHeadphoneIR(_Base):
    name = "SimpleHeadphoneIR"
    version = "0.2"
    def __init__(self):
        _Base.__init__(self)
        self.default_objects["Source"]["coordinates"].Position = [0,0,1]
        self.default_objects["Source"]["system"] = data.dimensions.Coordinates.Spherical

        self.head_radius = 0.09

    def add_metadata(self, dataset):
        _Base.add_general_defaults(dataset)

        dataset.SOFAConventions = self.name
        dataset.SOFAConventionsVersion = self.version
        dataset.DataType = "FIR"
        dataset.RoomType = rooms.types.FreeField.value
        dataset.DatabaseName = ""
        dataset.ListenerShortName = ""
        return

    def define_spatial_object(self, dataset, name, info_states, count=None):
        if name is "Receiver":
            if count is None: count = 2
            if count is not 2:
                print("Invalid Receiver count, setting to mandatory 2 Receivers")
                count = 2
        if name is "Emitter":
            if count is None: count = 2
            if count is not 2:
                print("Invalid Emitter count, setting to mandatory 2 Emitters")
                count = 2
        if name is "Listener":
            if info_states.View is data.spatial.State.Unused:
                print("Invalid Listener setup, assuming fixed View")
                info_states.View = data.spatial.State.Fixed
            if info_states.Up is data.State.spatial.Unused:
                print("Invalid Listener setup, assuming fixed Up")
                info_states.Up = data.spatial.State.Fixed
            
        _Base._define_spatial_object(self, dataset, name, info_states, count)

        if name is "Receiver": # set convention default values
            self.set_default_Receiver(dataset)
        if name is "Emitter": # set convention default values
            self.set_default_Emitter(dataset)
        return
    
    def set_default_Receiver(self, dataset):
        dataset.Receiver.Position.set_default([0,self.head_radius,0], index=0)
        dataset.Receiver.Position.set_default([0,-self.head_radius,0], index=1)
    def set_default_Emitter(self, dataset):
        dataset.Emitter.Position.set_default([0,self.head_radius,0], index=0)
        dataset.Emitter.Position.set_default([0,-self.head_radius,0], index=1)
