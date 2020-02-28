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

from enum import Enum
from .. import spatial

default_units = {
    spatial.Coordinates.System.Cartesian : "meter",
    spatial.Coordinates.System.Spherical : "degree, degree, meter",
    "frequency" : "hertz"
    }
    
class Definitions:
    _dims = {
        "Listener": ("I/M", "C",),
        "Source": ("I/M", "C",),
        "Receiver": ("R", "C", "I/M",),
        "Emitter": ("E", "C", "I/M",),
        
        "RoomCorner": ("I/M", "C",),
        }
        
    @staticmethod
    def _get_I_M(varies): return "M" if varies else "I"
        
    @classmethod
    def _get_dims(cls, name, varies):
        return tuple([x if x != "I/M" else Definitions._get_I_M(varies) for x in cls._dims[name]])
        
#    @classmethod
#    def __getattribute__(cls, name):
#        try: return super().__getattribute__(name)
#        except: 
#            print("Getting dimensions from list")
#            lambda v: cls._get_dims(name, v)

    @classmethod
    def Listener(cls, varies=False): return cls._get_dims("Listener", varies)
    @classmethod
    def Source(cls, varies=False): return cls._get_dims("Source", varies)
    
    @classmethod
    def Receiver(cls, varies=False): return cls._get_dims("Receiver", varies)
    @classmethod
    def Emitter(cls, varies=False): return cls._get_dims("Emitter", varies)
    
    @classmethod
    def RoomCorner(cls, varies=False): return cls._get_dims("RoomCorner", varies)    
    
    @classmethod
    def DataValues(cls, datatype):
        if datatype == "FIRE": return ("M","R","E","N",)
        return ("M","R","N",)
    @classmethod
    def DataDelay(cls, datatype, varies=False):
        if type(varies) != bool: varies = varies.value
        tup = ("I","R",)
        if varies: tup = ("M","R",)
        if datatype == "FIRE": return tup+("E",)
        return tup
    @classmethod
    def DataSamplingRate(cls, datatype, varies=False): return Definitions._get_I_M(varies)
    @classmethod
    def DataFrequencies(cls, datatype): return ("N",)
    
    names = {
        "Receiver" : "R",
        "Emitter" : "E"
        }
