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

class TF(_Base):
    @property
    def Real(self): 
        """:class:`sofa.VariableAccess` for the real part of the complex spectrum"""
        return access.VariableAccess(self.dataset, "Data.Real")
    def Imag(self): 
        """:class:`sofa.VariableAccess` for the imaginary part of the complex spectrum"""
        return access.VariableAccess(self.dataset, "Data.Imag")
    @property
    def N(self): 
        """:class:`sofa.VariableAccessWithUnits` for the frequency values"""
        return access.VariableAccessWithUnits(self.dataset, "N")
        
    def _create(self, default_values):
        self.Real._Matrix = dimensions.Definitions.DataValues(self.dataset.DataType)
        self.Real.set_values(default_values["Real"])
        self.Imag._Matrix = dimensions.Definitions.DataValues(self.dataset.DataType)
        self.Imag.set_values(default_values["Imag"])
        self.N._Matrix = dimensions.Definitions.DataFrequencies(self.dataset.DataType)
        self.N.set_values(default_values["N"])
#        self.N.LongName = default_values["N.LongName"]
        self.N.Units = dimensions.default_units["frequency"]
        return

