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

from .base import _Base
from . import dimensions

from .. import _util as util
from .. import _access as access

class FIR(_Base):
    @property
    def IR(self): 
        """:class:`sofa.VariableAccess` for the impulse response"""
        return access.VariableAccess(self.dataset, "Data.IR")
    @property
    def SamplingRate(self): 
        """:class:`sofa.ScalarVariableAccessWithUnits` for the sampling rate"""
        return access.ScalarVariableAccessWithUnits(self.dataset, "Data.SamplingRate")
    @property
    def Delay(self): 
        """:class:`sofa.VariableAccess` for the impulse response delay"""
        return access.VariableAccess(self.dataset, "Data.Delay")
        
    def _create(self, default_values):
        self.IR._Matrix = dimensions.Definitions.DataValues(self.dataset.DataType)
        self.IR.set_values(default_values["IR"])
        self.SamplingRate._Matrix = dimensions.Definitions.DataSamplingRate(self.dataset.DataType)
        self.SamplingRate.set_value(default_values["SamplingRate"])
        self.SamplingRate.Units = dimensions.default_units["frequency"]
        self.Delay._Matrix = dimensions.Definitions.DataDelay(self.dataset.DataType, default_values["DelayVaries"])
        self.Delay.set_values(default_values["Delay"])
        return    

