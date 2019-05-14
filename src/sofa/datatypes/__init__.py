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

"""Classes for accessing DataType-specific measurement data.
"""
__version__ = "0.1.0"

__all__=["implemented", "FIR", "FIRE", "SOS", "TF"]

from . import dimensions

from .FIR import FIR
from .TF import TF

from .FIRE import FIRE
from .SOS import SOS

##############################
List = {
    "FIR" : FIR,
    "TF" : TF,
    "FIRE" : FIRE,
    "SOS" : SOS
}
    
def get(database):
    if database.dataset.DataType in List.keys(): return List[database.dataset.DataType](database)
    print("Unknown DataType", file.DataType, ", returning FIR instead")
    return List["FIR"](database)

def implemented():
    """Returns
    -------
    list
        Names of implemented SOFA data types
    """
    return list(List.keys())
