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

"""Class for accessing dimensions of the underlying :class:`netCDF4.Dataset`.
"""

class Dimensions:
    """Dimensions specified by SOFA as int"""

    def __init__(self, dataset):
        self.dataset = dataset
        return

    @property
    def C(self):
        """Coordinate dimension size"""
        return self.get_dimension("C")

    @property
    def I(self):
        """Scalar dimension size"""
        return self.get_dimension("I")

    @property
    def M(self):
        """Number of measurements"""
        return self.get_dimension("M")

    @property
    def R(self):
        """Number of receivers"""
        return self.get_dimension("R")

    @property
    def E(self):
        """Number of emitters"""
        return self.get_dimension("E")

    @property
    def N(self):
        """Number of data samples per measurement"""
        return self.get_dimension("N")

    @property
    def S(self):
        """Largest data string size"""
        return self.get_dimension("S")

    def get_dimension(self, dim):
        if dim not in self.dataset.dimensions:
            print("dimension {0} not initialized".format(dim))
            return None
        return self.dataset.dimensions[dim].size

    def create_dimension(self, dim, size):
        if dim in self.dataset.dimensions:
            print("Dimension {0} already initialized to {1}, cannot re-initialize to {2}.".format(dim, self.get_dimension(dim), size))
            return
        self.dataset.createDimension(dim, size)

    def list_dimensions(self):
        return self.dataset.dimensions.keys()

    def dump(self):
        """Prints all dimension sizes"""
        for dim in self.dataset.dimensions:
            print("{0}: {1}".format(dim, self.dataset.dimensions[dim].size))
        return