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

from .. import datatypes
from .. import spatial

class _Base:
    def __init__(self):
        self.default_objects = {
            "Listener" : {
                "count" : 1,
                "coordinates" : {},
                "system" : {}
                },
            "Receiver" : {
                "coordinates": {},
                "system": {}
            },
            "Source" : {
                "count" : 1,
                "coordinates" : {},
                "system" : {}
                },
            "Emitter" : {
                "coordinates": {},
                "system": {}
            },
            }
        self.conditions = {
            "only 1 Listener considered" : lambda name, fixed, variances, count: name != "Listener" or count == 1,
            "only 1 Source considered" : lambda name, fixed, variances, count: name != "Source" or count == 1,
            }
        self.default_data = {
            "IR" : 0,
            "Delay" : 0,
            "SamplingRate" : 48000,
            "SamplingRate:Units" : "hertz",

            "Real" : 0,
            "Imag" : 0,
            "N" : 0,
            "N.LongName" : "frequency",

            "SOS" : 0 #TODO repeat [0 0 0 1 0 0] along N
            }
        return

    @staticmethod
    def add_general_defaults(database):
        database.Metadata.set_attribute("Conventions", "SOFA")
        database.Metadata.set_attribute("Version", "1.0")
        database.Metadata.set_attribute("Title", "")
        database.Metadata.set_attribute("DateCreated", "")
        database.Metadata.set_attribute("DateModified", "")
        database.Metadata.set_attribute("APIName", "python-SOFA")
        database.Metadata.set_attribute("APIVersion", "0.2")
        database.Metadata.set_attribute("AuthorContact", "")
        database.Metadata.set_attribute("Organization", "")
        database.Metadata.set_attribute("License", "No license provided, ask the author for permission")

        database.Metadata.set_attribute("RoomType", "free field")
        database.Metadata.set_attribute("DataType", "FIR")

        database.Dimensions.create_dimension("I", 1)
        database.Dimensions.create_dimension("C", 3)
        return

    def add_metadata(self, database):
        _Base.add_general_defaults(database)

    def validate_spatial_object_settings(self, name, fixed, variances, count):
        for con in self.conditions:
            if not self.conditions[con](name, fixed, variances, count): raise Exception(con)

    def set_default_spatial_values(self, spobj):
        name = spobj.name
        if name not in self.default_objects: return
        coordinates = self.default_objects[name]["coordinates"]
        system = self.default_objects[name]["system"]

        if spobj.Position.exists():
            rd = tuple(x for x in spobj.Position.dimensions() if x != "C")
            if "Position" in system: spobj.Position.set_system(csystem=system)
            if "Position" in coordinates: spobj.Position.set_values(coordinates["Position"], repeat_dim = rd)
        if spobj.View.exists():
            rd = tuple(x for x in spobj.View.dimensions() if x != "C")
            if "View" in system: spobj.View.set_system(csystem=system)
            if "View" in coordinates: spobj.View.set_values(coordinates["View"], repeat_dim = rd)
        if spobj.Up.exists():
            rd = tuple(x for x in spobj.Up.dimensions() if x != "C")
            if "Up" in system: spobj.Up.set_system(csystem=system)
            if "Up" in coordinates: spobj.View.set_values(coordinates["Up"], repeat_dim = rd)
        return
        

