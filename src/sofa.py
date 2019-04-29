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

"""SOFA API for Python.
"""
__version__='0.1.0'

from _sofa import *

from enum import Enum
import netCDF4 as ncdf
from datetime import datetime

def implemented_rooms():
    """Implemented SOFA room types
    
    Returns
    -------
    list
        Names of implemented SOFA room types
    """
    return list(rooms.List.keys())

def implemented_datatypes():
    """Implemented SOFA data types
    
    Returns
    -------
    list
        Names of implemented SOFA data types
    """
    return list(data.datatypes.List.keys())

def implemented_conventions():
    """Implemented SOFA dataconventions
    
    Returns
    -------
    list
        Names of implemented SOFA conventions
    """
    #TODO: versionize convention implementations
    return list(conventions.conventions.List.keys())

class InfoState(Enum):
        """Enum for the usage of spatial information."""
        Unused = None
        """spatial information not provided"""  
        Fixed = False
        """spatial information constant for each measurement"""
        Varying = True
        """spatial information varies for each measurement"""

class SpatialInfo:
    """Descriptors or data for a spatial entity (Listener, Source, Receiver, Emitter)"""

    def __init__(self, Position, View=InfoState.Unused, Up=InfoState.Unused):
        """Initializes the information for Position, View and Up

        Parameters
        ----------
        Position : :class:'InfoState'
        View : :class:'InfoState', optional
        Up : :class:'InfoState', optional
        """
        self._Position=Position
        self._View=View
        self._Up=Up

    @property
    def Position(self): return self._Position
    @property
    def View(self): return self._View
    @property
    def Up(self): return self._Up

class Database:  
    """Provides access to NETCDF4 files following the SOFA specifications and conventions"""

    def __init__(self):
        self.dataset = None
        self.convention = None

        self._Dimensions = None
        self._Listener = None
        self._Source = None
        self._Receiver = None
        self._Emitter = None
      
    @staticmethod  
    def open(path, mode='r'):
        """Opens an existing .sofa file
    
        Parameters
        ----------
        path : str
            Relative or absolute path to .sofa file
        
        mode : str, optional
            File access mode ('r': readonly, 'r+': read/write)
        """
        if mode == 'w':
            print("Invalid file creation method, use create instead.")
            return None
        sofa = Database()
        sofa.dataset = ncdf.Dataset(path, mode=mode)
        if sofa.dataset.SOFAConventions in conventions.conventions.List.keys():
            sofa.convention = conventions.conventions.List[sofa.dataset.SOFAConventions]()
        else:
            default = "General"+sofa.dataset.DataType
            sofa.convention = conventions.conventions.List[default]()
        return sofa

    @staticmethod
    def create(path, conv_name):
        """Creates a new .sofa file and sets its SOFA convention

        Parameters
        ----------
        path : str
            Relative or absolute path to .sofa file
    
        conv_name : str
            Name of the SOFA convention to create
        """
        sofa = Database()
        sofa.dataset = ncdf.Dataset(path, mode="w")
        sofa.convention = conventions.conventions.List[conv_name]()
        
        sofa.convention.add_metadata(sofa.dataset)
        sofa.DateCreated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return sofa

    def save(self):
        """Saves the underlying NETCDF4 dataset"""
        self.DateModified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dataset.sync()
            
    def close(self):
        """Saves and closes the underlying NETCDF4 dataset"""
        try: self.save()
        except: pass #avoid errors when closing files in read mode
        return self.dataset.close()
    
    def initialize_room(self, room=None):
        """Initializes the variables and attributes associated with the room of the experimental setup
        
        Parameters
        ----------
        room : str, optional
            Name of the room type to be initialized
        """
        if room is not None: self.Room.Type = room
        self.Room.create()
        return

    def initialize_measurements(self, measurements):
        """Defines the number of measurements to be recorded
        
        Parameters
        ----------
        measurements : int
            Number of measurements
        """
        self.convention.define_measurements(self, measurements)
        return

    def initialize_spatial_objects(self, listener_info, receiver_count, receiver_info, source_info, emitter_count, emitter_info):
        """Initializes the variables and attributes associated with the Listener, Source, Receiver and Emitter
        
        Parameters
        ----------
        listener_info : :class:'SpatialInfo'
            Usage information for Position, View and Up of the Listener
        receiver_count : int
            Number of Receivers used
        receiver_info : :class:'SpatialInfo'
            Usage information for Position, View and Up of the Receiver(s)
        source_info : :class:'SpatialInfo'
            Usage information for Position, View and Up of the Source
        emitter_count : int
            Number of Emitters used
        emitter_info : :class:'SpatialInfo'
            Usage information for Position, View and Up of the Emitter
        """
        self.convention.define_spatial_object(self, "Listener", listener_info)
        self.convention.define_spatial_object(self, "Source", source_info)
        self.convention.define_spatial_object(self, "Receiver", receiver_info, count=receiver_count)
        self.convention.define_spatial_object(self, "Emitter", emitter_info, count=emitter_count)
        return

    def initialize_data(self, samples, string_length = 0):
        """Initializes the dimensions and variables associated with the convention's data
        
        Parameters
        ----------
        samples : int
            Number of data samples per measurement
        string_length: int, optional
            Maximum length of data recorded as strings
        """
        self.convention.define_data(self, samples, string_length)
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
