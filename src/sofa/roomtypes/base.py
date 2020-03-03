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

from .. import access

class _Base(access.ProxyObject):
    def __init__(self, database):
        super().__init__(database, "Room")

    @property
    def Type(self): 
        """SOFA data type"""
        return self.database.Metadata.get_attribute("RoomType")
    @Type.setter
    def Type(self, value): self.database.Metadata.set_attribute("RoomType", value)

    def optional_variance_names(self):
        """Returns a list of standardized data elements that may vary between measurements"""
        vardims = []
        for k, v in self.standard_dimensions:
            if any(["I" in dims for dims in v]) and any(["M" in dims for dims in v]): vardims.append(k)
        return vardims

    def initialize(self, variances=[], string_length=None):
        """Create the necessary variables and attributes

        Parameters
        ----------
        measurement_count : int
            Number of measurements
        sample_count : int
            Number of samples per measurement
        variances : list
            Names of the variables that vary along dimension M
        string_length : int, optional
            Size of the longest data string
        """
        if string_length is not None: self.database.Dimensions.create_dimension("S", string_length)

        default_values = self.database._convention.default_data

        for k, v in self.standard_dimensions:
            i = 0 if k not in variances else 1
            if any(["S" in dims for dims in v]):
                var = self.create_string_array(k, v[i])
            else:
                var = self.create_variable(k, v[i])
                if k + ":Type" in default_values: var.Type = default_values[k + ":Type"]
                if k + ":Units" in default_values: var.Units = default_values[k + ":Units"]
            if k in default_values and default_values[k] != 0:
                var.set_values(default_values[k])
        return