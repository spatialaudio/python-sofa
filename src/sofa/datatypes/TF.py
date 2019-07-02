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

class TF(_Base):
    @property
    def Real(self): 
        """:class:`sofa.access.ArrayVariable` for the real part of the complex spectrum"""
        return access.ArrayVariable(self.database.dataset, "Data.Real")
    @property
    def Imag(self): 
        """:class:`sofa.access.ArrayVariable` for the imaginary part of the complex spectrum"""
        return access.ArrayVariable(self.database.dataset, "Data.Imag")
    @property
    def N(self): 
        """:class:`sofa.access.ArrayVariable` for the frequency values"""
        return access.ArrayVariable(self.database.dataset, "N")
        
    def initialize(self, sample_count, string_length = 0):
        """Create the necessary variables and attributes
        
        Parameters
        ----------
        sample_count : int
            Number of samples per measurement
        string_length : int, optional
            Size of the longest data string
        """
        _Base._initialize_dimensions(self, sample_count, string_length = string_length)
        default_values = self.database._convention.default_data

        self.Real.initialize(dimensions.Definitions.DataValues(self.Type))
        if default_values["Real"] != 0: self.Real.set_values(default_values["Real"])
        self.Imag.initialize(dimensions.Definitions.DataValues(self.Type))
        if default_values["Imag"] != 0: self.Imag.set_values(default_values["Imag"])
        self.N.initialize(dimensions.Definitions.DataFrequencies(self.dataset.DataType))
        self.N.set_values(default_values["N"])
#        self.N.LongName = default_values["N.LongName"]
        self.N.Units = dimensions.default_units["frequency"]
        return

