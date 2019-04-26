from .base import _Base
from . import dimensions

from .. import _util as util

class TF(_Base):
    @util.DatasetVariable()
    def N(self): return "N"
    @util.DatasetVariable()
    def Real(self): return "Data.Real"
    @util.DatasetVariable()
    def Imag(self): return "Data.Imag"
        
    def create(self, default_values):
        self.Real = dimensions.Definitions.DataValues(self.dataset.DataType)
        self.Real[:] = default_values["Real"]
        self.Imag = dimensions.Definitions.DataValues(self.dataset.DataType)
        self.Imag[:] = default_values["Imag"]
            
        self.N = dimensions.Definitions.DataFrequencies(self.dataset.DataType)
        self.N[:] = default_values["N"]
        self.N.LongName = default_values["N.LongName"]
        self.N.Units = dimensions.default_units["frequency"]
        return

