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

"""
"""
__version__ = "0.1.1"

__all__=["implemented"]

from . import base

from . import GeneralFIR
from . import GeneralTF
from . import SimpleFreeFieldHRIR

from . import GeneralFIRE
from . import MultiSpeakerBRIR
from . import SimpleFreeFieldTF
from . import SimpleFreeFieldSOS
#from . import SimpleHeadphoneIR
from . import SingleRoomDRIR

List = {
    "GeneralFIR" : GeneralFIR.GeneralFIR,
    "GeneralTF" : GeneralTF.GeneralTF,
    "SimpleFreeFieldHRIR" : SimpleFreeFieldHRIR.SimpleFreeFieldHRIR,

    "GeneralFIRE" : GeneralFIRE.GeneralFIRE,
    "MultiSpeakerBRIR" : MultiSpeakerBRIR.MultiSpeakerBRIR,
    "SimpleFreeFieldTF" : SimpleFreeFieldTF.SimpleFreeFieldTF,
    "SimpleFreeFieldSOS" : SimpleFreeFieldSOS.SimpleFreeFieldSOS,
#    "SimpleHeadphoneIR" : SimpleHeadphoneIR.SimpleHeadphoneIR,
    "SingleRoomDRIR" : SingleRoomDRIR.SingleRoomDRIR
    }

def implemented():
    """Returns
    -------
    list
        Names of implemented SOFA conventions
    """
    #TODO: versionize convention implementations
    return list(List.keys())
