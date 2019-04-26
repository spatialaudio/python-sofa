from .base import _Base
from . import dimensions

from .. import _util as util

class SOS(_Base):
    @util.DatasetVariable()
    def SOS(self): return "Data.SOS"
    @util.DatasetVariable()
    def SamplingRate(self): return "Data.SamplingRate"
    @util.DatasetVariable()
    def Delay(self): return "Data.Delay"
        
    def create(self, default_values):
        self.SOS = dimensions.Definitions.DataValues(self.dataset.DataType)
        self.SOS[:] = default_values["SOS"]
        self.SamplingRate = dimensions.Definitions.DataSamplingRate(self.dataset.DataType)
        self.SamplingRate[:] = default_values["SamplingRate"]
        self.SamplingRate.Units = dimensions.default_units["frequency"]
        self.Delay = dimensions.Definitions.DataDelay(self.dataset.DataType, True)
        self.Delay[:] = default_values["Delay"]
        return    

