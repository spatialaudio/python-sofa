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
                "coordinates" : spatial.Set(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : spatial.Coordinates.System.Cartesian
                },
            "Receiver" : {
                "coordinates" : spatial.Set(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : spatial.Coordinates.System.Cartesian
                },
            "Source" : {
                "count" : 1,
                "coordinates" : spatial.Set(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : spatial.Coordinates.System.Cartesian
                },
            "Emitter" : {
                "coordinates" : spatial.Set(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : spatial.Coordinates.System.Cartesian
                },
            }
        self.conditions = {"Position required" : lambda name, info_states, count: spatial.Coordinates.State.is_used(info_states.Position),
            "only 1 Listener considered" : lambda name, info_states, count: name != "Listener" or count == 1,
            "only 1 Source considered" : lambda name, info_states, count: name != "Source" or count == 1,
            "Up requires View" : lambda name, info_states, count: (not spatial.Coordinates.State.is_used(info_states.Up)) or (spatial.Coordinates.State.is_used(info_states.View)),
            }
        self.default_data = {
            "IR" : 0,
            "Delay" : 0,
            "SamplingRate" : 48000,

            "Real" : 0,
            "Imag" : 0,
            "N" : 0,
            "N.LongName" : "frequency",

            "SOS" : 0 #TODO permute([0 0 0 1 0 0],[3 1 2])
            }
        return

    def add_general_defaults(dataset):
        dataset.Conventions = "SOFA"
        dataset.Version = "1.0"
        dataset.Title = ""
        dataset.DateCreated = ""
        dataset.DateModified = ""
        dataset.APIName = "python-SOFA"
        dataset.APIVersion = "0.1"
        dataset.AuthorContact = ""
        dataset.Organization = ""
        dataset.License = "No license provided, ask the author for permission"

        dataset.createDimension("I", 1)
        dataset.createDimension("C", 3)
        dataset.ListenerDescription = ""
        dataset.ReceiverDescription = ""
        dataset.SourceDescription = ""
        dataset.EmitterDescription = ""
        return

    def define_measurements(self, dataset, measurement_count):
        dataset.dataset.createDimension("M", measurement_count)
        return
    
    def validate_spatial_object_settings(self, name, info_states, count):
        for con in self.conditions:
            if not self.conditions[con](name, info_states, count): raise Exception(con)

    def _set_default_spatial_values(self, spobj):
        name = spobj.name
        rd = tuple(x for x in getattr(datatypes.dimensions.Definitions, name)(spatial.Coordinates.State.Varying) if x!="C")
        if spobj.Position.exists():
            spobj.Position.set_values(self.default_objects[name]["coordinates"].Position, repeat_dim=rd)
            spobj.Position.set_system(self.default_objects[name]["system"])
        if spobj.View.exists():
            spobj.View.set_values(self.default_objects[name]["coordinates"].View, repeat_dim=rd)
            spobj.View.set_system(self.default_objects[name]["system"])
        if spobj.Up.exists():
            spobj.Up.set_values(self.default_objects[name]["coordinates"].Up, repeat_dim=rd)
        return
        

