from .base import _Base
from . import dimensions

from .. import _util as util

class FIRE(_Base):
    @util.DatasetVariable()
    def IR(self): return "Data.IR"
    @util.DatasetVariable()
    def SamplingRate(self): return "Data.SamplingRate"
    @util.DatasetVariable()
    def Delay(self): return "Data.Delay"
        
    def create(self, default_values):
        self.IR = dimensions.Definitions.DataValues(self.dataset.DataType)
        self.IR[:] = default_values["IR"]
        self.SamplingRate = dimensions.Definitions.DataSamplingRate(self.dataset.DataType)
        self.SamplingRate[:] = default_values["SamplingRate"]
        self.SamplingRate.Units = dimensions.default_units["frequency"]
        self.Delay = dimensions.Definitions.DataDelay(self.dataset.DataType, default_values["DelayVaries"])
        self.Delay[:] = default_values["Delay"]
        return    

