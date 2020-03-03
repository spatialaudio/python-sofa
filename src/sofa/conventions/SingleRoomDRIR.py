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

from .. import spatial

class SingleRoomDRIR(_Base):
    name = "SingleRoomDRIR"
    version = "0.3"
    
    def __init__(self):
        _Base.__init__(self)
        self.default_objects["Source"]["coordinates"]["View"] = [-1,0,0]
        self.default_objects["Emitter"]["count"] = 1

        self.conditions["must have 1 Emitter"] = lambda name, fixed, variances, count: name != "Emitter" or count == 1
        self.conditions["must have Listener Up and View"] = lambda name, fixed, variances, count: name != "Listener" or ("Up" in fixed + variances and "View" in fixed + variances)
        self.conditions["must have Source Up and View"] = lambda name, fixed, variances, count: name != "Source" or ("Up" in fixed + variances and "View" in fixed + variances)

    def add_metadata(self, database):
        super().add_metadata(database)

        database.Metadata.set_attribute("SOFAConventions", self.name)
        database.Metadata.set_attribute("SOFAConventionsVersion", self.version)

        database.Data.Type = "FIR"
        database.Room.Type = "reverberant"
        return
