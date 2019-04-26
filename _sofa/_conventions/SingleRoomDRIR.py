from .base import _Base

from .. import _data as data
from .. import _rooms as rooms

class SingleRoomDRIR(_Base):
    name = "SingleRoomDRIR"
    version = "0.3"
    def __init__(self):
        _Base.__init__(self)
        self.default_objects["Source"]["coordinates"].View = [-1,0,0]

    def add_metadata(self, dataset):
        _Base.add_general_defaults(dataset)

        dataset.SOFAConventions = self.name
        dataset.SOFAConventionsVersion = self.version
        dataset.DataType = "FIR"
        dataset.RoomType = rooms.types.Reverb.value
        return

    def define_spatial_object(self, dataset, name, info_states, count=None):
        if name is "Listener":
            if info_states.View is data.State.Unused:
                print("Invalid Listener setup, assuming fixed View")
                info_states.View = data.State.Fixed
            if info_states.Up is data.State.Unused:
                print("Invalid Listener setup, assuming fixed Up")
                info_states.Up = data.State.Fixed
        if name is "Source":
            if info_states.View is data.State.Unused:
                print("Invalid Source setup, assuming fixed View")
                info_states.View = data.State.Fixed
            if info_states.Up is data.State.Unused:
                print("Invalid Source setup, assuming fixed Up")
                info_states.Up = data.State.Fixed
        
        _Base._define_spatial_object(self, dataset, name, info_states, count)
        return

