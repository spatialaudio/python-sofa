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

class FIR(_Base):
    """Finite Impulse Response data type

    IR : `sofa.access.Variable`
        Discrete time impulse responses, dimensions ('M', 'R', 'N')
    Delay : `sofa.access.Variable`
        Broadband delay in units of dimension 'N', dimensions ('I', 'R') or ('M', 'R')
    SamplingRate : `sofa.access.Variable`
        Sampling rate, dimensions ('I') or ('M'), with attribute "Units"
    """

    def __init__(self, database):
        super().__init__(database)
        self.standard_dimensions["IR"] = [("M", "R", "N")]
        self.standard_dimensions["Delay"] = [("I", "R"), ("M", "R")]
        self.standard_dimensions["SamplingRate"] = [("I",), ("M",)]

