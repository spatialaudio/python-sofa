from _sofa import *
import netCDF4 as ncdf
from datetime import datetime

def DataTypes():
    return data.datatypes.List.keys()
def Conventions():
    return conventions.conventions.List.keys()

class Database:  
    def __init__(self):
        self.dataset = None
        self.convention = None

        self._Dimensions = None
        self._Listener = None
        self._Source = None
        self._Receiver = None
        self._Emitter = None
        
    def close(self):
        try: self.save()
        except: pass #avoid errors when closing files in read mode
        return self.dataset.close()
    
    def open(path, mode="r"):
        sofa = Database()
        sofa.dataset = ncdf.Dataset(path, mode=mode)
        if sofa.dataset.SOFAConventions in conventions.conventions.List.keys():
            sofa.convention = conventions.conventions.List[sofa.dataset.SOFAConventions]()
        else:
            default = "General"+sofa.dataset.DataType
            sofa.convention = conventions.conventions.List[default]()
        return sofa

    def create(path, conv_name):
        sofa = Database()
        sofa.dataset = ncdf.Dataset(path, mode="w")
        sofa.convention = conventions.conventions.List[conv_name]()
        
        sofa.convention.add_metadata(sofa.dataset)
        sofa.DateCreated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return sofa

    def save(self):
        self.DateModified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dataset.sync()
            
    def initialize_room(self, room=None):
        if room is not None: self.Room.Type = room
        self.Room.create()
        return

    def initialize_experiment(self, measurements, string_length = 0):
        self.convention.define_experiment(self, measurements, string_length)
        return

    def initialize_spatial_objects(self, listener_info, receiver_count, receiver_info, source_info, emitter_count, emitter_info):
        self.convention.define_spatial_object(self, "Listener", listener_info)
        self.convention.define_spatial_object(self, "Source", source_info)
        self.convention.define_spatial_object(self, "Receiver", receiver_info, count=receiver_count)
        self.convention.define_spatial_object(self, "Emitter", emitter_info, count=emitter_count)
        return

    def initialize_data(self, samples):
        self.convention.define_data(self, samples)
        return

    @property
    def Dimensions(self): 
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Dimensions is None: self._Dimensions = data.dimensions.Access(self.dataset)
        return self._Dimensions
    
    ## experimental setup
    @property
    def Listener(self): 
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Listener is None: self._Listener = data.spatial.SingleObject(self.dataset, "Listener")
        return self._Listener
    
    @property
    def Source(self):
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Source is None: self._Source = data.spatial.SingleObject(self.dataset, "Source")
        return self._Source
    
    @property
    def Receiver(self): 
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Receiver is None: self._Receiver = data.spatial.MultiObject(self.dataset, "Receiver")
        return self._Receiver
    
    @property
    def Emitter(self): 
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Emitter is None: self._Emitter = data.spatial.MultiObject(self.dataset, "Emitter")
        return self._Emitter
        
    ## room
    @property
    def Room(self): return rooms.get(self.dataset)
    
    ## data
    @property
    def Data(self): return data.datatypes.get(self.dataset)

    ## metadata
    @util.DatasetAttribute()
    def Conventions(self): return "Conventions"
    @util.DatasetAttribute()
    def Version(self): return "Version"
    @util.DatasetAttribute()
    def SOFAConventions(self): return "SOFAConventions"
    @util.DatasetAttribute()
    def SOFAConventionsVersion(self): return "SOFAConventionsVersion"
#    @util.DatasetAttribute()
#    def DataType(self): return "DataType"
#    @util.DatasetAttribute()
#    def RoomType(self): return "RoomType"
    @util.DatasetAttribute()
    def Title(self): return "Title"
    @util.DatasetAttribute()
    def DateCreated(self): return "DateCreated"
    @util.DatasetAttribute()
    def DateModified(self): return "DateModified"
    @util.DatasetAttribute()
    def APIName(self): return "APIName"
    @util.DatasetAttribute()
    def APIVersion(self): return "APIVersion"
    @util.DatasetAttribute()
    def AuthorContact(self): return "AuthorContact"
    @util.DatasetAttribute()
    def Organization(self): return "Organization"
    @util.DatasetAttribute()
    def License(self): return "License"
    @util.DatasetAttribute()
    def ApplicationName(self): return "ApplicationName"
    @util.DatasetAttribute()
    def ApplicationVersion(self): return "ApplicationVersion"
    @util.DatasetAttribute()
    def Comment(self): return "Comment"
    @util.DatasetAttribute()
    def History(self): return "History"
    @util.DatasetAttribute()
    def References(self): return "References"
    @util.DatasetAttribute()
    def Origin(self): return "Origin"
 
# TODO: access to additional attributes from conventions or user definitions
