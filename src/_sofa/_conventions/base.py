from .. import _data as data

class _Base:
    def __init__(self):
        self.default_objects = {
            "Listener" : {
                "coordinates" : data.spatial.StateSet(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : data.dimensions.Coordinates.Cartesian
                },
            "Receiver" : {
                "coordinates" : data.spatial.StateSet(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : data.dimensions.Coordinates.Cartesian
                },
            "Source" : {
                "coordinates" : data.spatial.StateSet(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : data.dimensions.Coordinates.Cartesian
                },
            "Emitter" : {
                "coordinates" : data.spatial.StateSet(Position=[0,0,0], View=[1,0,0], Up=[0,0,1]),
                "system" : data.dimensions.Coordinates.Cartesian
                },
            }
        self.default_data = {
            "IR" : 0,
            "Delay" : 0,
            "DelayVaries" : False,
            "SamplingRate" : 48000,

            "Real" : 0,
            "Imag" : 0,
            "N" : 0,
            "N.Longname" : "frequency",

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
    
    def _define_spatial_object(self, dataset, name, info_states, count=None):
        spobj = getattr(dataset, name)
        if count is None: spobj.define(info_states)
        else: spobj.define(count, info_states)
        if info_states.Position is not data.spatial.State.Unused: spobj.set_default_Position(self.default_objects[name]["coordinates"].Position, self.default_objects[name]["system"])
        if info_states.View is not data.spatial.State.Unused: spobj.set_default_View(self.default_objects[name]["coordinates"].View)
        if info_states.Up is not data.spatial.State.Unused: spobj.set_default_Up(self.default_objects[name]["coordinates"].Up)
        return
        
    def define_data(self, dataset, sample_count, string_length):
        if string_length>0: dataset.dataset.createDimension("S", string_length)
        dataset.dataset.createDimension("N", sample_count)
        dataset.Data.create(self.default_data)
        return

