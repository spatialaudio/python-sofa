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


class TF(_Base):
    """Transfer Function data type

    Real : `sofa.access.Variable`
        Real part of the complex spectrum, dimensions ('M', 'R', 'N')
    Imag : `sofa.access.Variable`
        Imaginary part of the complex spectrum, dimensions ('M', 'R', 'N')
    N : `sofa.access.Variable`
        Frequency values, dimension ('N',), with attributes "LongName" and "Units"
    """

    def __init__(self, database):
        super().__init__(database)
        self.standard_dimensions["Real"] = [("M", "R", "N")]
        self.standard_dimensions["Imag"] = [("M", "R", "N")]

    @property
    def N(self):
        """Frequency values"""
        return self.database.Variables.get_variable("N")

    @N.setter
    def N(self, value): self.N.set_values(value)

    def initialize(self, sample_count=None, variances=[], string_length=None):
        super().initialize(sample_count, variances, string_length)
        var = self.database.Variables.create_variable("N", ("N",))
        # var.LongName = "frequency" # LongName not mandatory
        var.Units = "hertz"
