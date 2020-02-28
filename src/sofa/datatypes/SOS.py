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

from .. import access


class SOS(_Base):
#    @property
#    def SOS(self): 
#        """:class:`sofa.access.Variable` for the second order sections"""
#        return access.Variable(self.database.dataset, "Data.SOS")
#    @property
#    def SamplingRate(self): 
#        """:class:`sofa.access.Variable` for the sampling rate"""
#        return access.Variable(self.database.dataset, "Data.SamplingRate")
#    @property
#    def Delay(self): 
#        """:class:`sofa.access.Variable` for the impulse response delay"""
#        return access.Variable(self.database.dataset, "Data.Delay")
        
    @staticmethod
    def optional_variance_names():
        return ["SamplingRate", "Delay"]
        
    def initialize(self, sample_count, variances=[], string_length = 0):
        """Create the necessary variables and attributes
        
        Parameters
        ----------
        sample_count : int
            Number of samples per measurement
        variances : list
            Names of the variables that vary along dimension M
        string_length : int, optional
            Size of the longest data string
        """
        super()._initialize_dimensions(sample_count, string_length = string_length)
        default_values = self.database._convention.default_data        
        
        self.create_variable("SOS", dimensions.Definitions.DataValues(self.Type))
        if default_values["SOS"] != 0: self.SOS = default_values["SOS"]
        
        self.create_variable("SamplingRate", dimensions.Definitions.DataSamplingRate(self.Type, varies="SamplingRate" in variances))
        self.SamplingRate = default_values["SamplingRate"]
        self.SamplingRate.Units = dimensions.default_units["frequency"]
        
        self.create_variable("Delay", dimensions.Definitions.DataDelay(self.Type, varies="Delay" in variances))
        if default_values["Delay"] != 0: self.Delay = default_values["Delay"]
        return    

