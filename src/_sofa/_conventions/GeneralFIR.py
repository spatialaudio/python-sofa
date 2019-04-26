from .base import _Base

from .. import _data as data
from .. import _rooms as rooms

class GeneralFIR(_Base):
    name = "GeneralFIR"
    version = "1.0"
    def __init__(self):
        _Base.__init__(self)
        self.default_objects["Source"]["coordinates"].Position = [0,0,1]
        self.default_objects["Source"]["system"] = data.dimensions.Coordinates.Spherical

    def add_metadata(self, dataset):
        _Base.add_general_defaults(dataset)

        dataset.SOFAConventions = self.name
        dataset.SOFAConventionsVersion = self.version
        dataset.DataType = "FIR"
        dataset.RoomType = rooms.types.FreeField.value
        return

    def define_spatial_object(self, dataset, name, info_states, count=None):
        _Base._define_spatial_object(self, dataset, name, info_states, count)
        return

