from .base import _Base

from .. import _data as data
from .. import _rooms as rooms

import numpy as np

class MultiSpeakerBRIR(_Base):
    name = "MultiSpeakerBRIR"
    version = "0.3"
    def __init__(self):
        _Base.__init__(self)
        self.default_objects["Source"]["coordinates"].Position = [0,0,1]
        self.default_objects["Source"]["system"] = data.dimensions.Coordinates.Spherical

        self.default_data["IR"]=1

        self.head_radius = 0.09

    def add_metadata(self, dataset):
        _Base.add_general_defaults(dataset)

        dataset.SOFAConventions = self.name
        dataset.SOFAConventionsVersion = self.version
        dataset.DataType = "FIRE"
        dataset.RoomType = rooms.types.Reverb.value
        dataset.DatabaseName = ""
        dataset.ListenerShortName = ""
        return

    def define_spatial_object(self, dataset, name, info_states, count=None):
        if name is "Receiver":
            if count is None: count = 2
            if count is not 2:
                print("Invalid Receiver count, setting to mandatory 2 Receivers")
                count = 2
        if name is "Listener":
            if info_states.View is data.State.Unused:
                print("Invalid Listener setup, assuming fixed View")
                info_states.View = data.State.Fixed
            if info_states.Up is data.State.Unused:
                print("Invalid Listener setup, assuming fixed Up")
                info_states.Up = data.State.Fixed
        if name is "Emitter":
            if info_states.View is data.State.Unused:
                if info_states.Up is not data.State.Unused:
                    print("Invalid Emitter setup, assuming fixed View")
                    info_states.View = data.State.Fixed
            if info_states.Up is data.State.Unused:
                if info_states.View is not data.State.Unused:
                    print("Invalid Emitter setup, assuming fixed Up")
                    info_states.Up = data.State.Fixed

        _Base._define_spatial_object(self, dataset, name, info_states, count)

        if name is "Receiver": # set convention default values
            self.set_default_Receiver(dataset)
        return
    
    def set_default_Receiver(self, dataset):
        for m in np.arange(dataset.Receiver.Position.get_dims()[2].size):
            dataset.Receiver.Position[0,:,m]=[0,self.head_radius,0]
            dataset.Receiver.Position[1,:,m]=[0,-self.head_radius,0]

