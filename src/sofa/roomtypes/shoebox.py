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

"""Classes for accessing RoomType-specific data.
"""

from .base import _Base
from .. import spatial

class Shoebox(_Base):

    """Shoebox room type

    CornerA : `sofa.spatial.Coordinates`
        First corner of room cuboid, dimensions ('I', 'C') or ('M', 'C')
    CornerB : `sofa.spatial.Coordinates`
        Opposite corner of room cuboid, dimensions ('I', 'C') or ('M', 'C')
    """
    def __init__(self, database):
        super().__init__(database)
        self.standard_dimensions["CornerA"] = [("I", "C"), ("M", "C")]
        self.standard_dimensions["CornerB"] = [("I", "C"), ("M", "C")]

    @property
    def CornerA(self):
        """First corner of room cuboid"""
        return spatial.Coordinates(self, "CornerA")

    @property
    def CornerB(self):
        """Opposite corner of room cuboid"""
        return spatial.Coordinates(self, "CornerB")

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
        self.CornerA.initialize("CornerA" in variances)
        self.CornerB.initialize("CornerB" in variances)
