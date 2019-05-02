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

from . import _access as access
from . import _util as util
from . import _data as data
from . import _rooms as rooms
from . import _conventions as conventions

from enum import Enum
import netCDF4 as ncdf
from datetime import datetime

class Database:  
    """Read and write NETCDF4 files following the SOFA specifications and conventions"""

    def __init__(self):
        self.dataset = None
        self._convention = None

        self._Dimensions = None
        self._Listener = None
        self._Source = None
        self._Receiver = None
        self._Emitter = None

        self._Metadata = None
      
    @staticmethod  
    def open(path, mode='r'):
        """Parameters
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
        if sofa.dataset.SOFAConventions in conventions.implemented():
            sofa.convention = conventions.List[sofa.dataset.SOFAConventions]()
        else:
            default = "General"+sofa.dataset.DataType
            sofa.convention = conventions.List[default]()
        return sofa

    @staticmethod
    def create(path, convention):
        """Create a new .sofa file following a SOFA convention

        Parameters
        ----------
        path : str
            Relative or absolute path to .sofa file
    
        convention : str
            Name of the SOFA convention to create, see :func:`sofa.conventions.implemented`
        """
        sofa = Database()
        sofa.dataset = ncdf.Dataset(path, mode="w")
        sofa._convention = conventions.List[convention]()
        
        sofa._convention.add_metadata(sofa.dataset)
        sofa.DateCreated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return sofa

    def save(self):
#        """Save the underlying NETCDF4 dataset"""
        if self.dataset == None: return
        self.DateModified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dataset.sync()
            
    def close(self):
#        """Save and close the underlying NETCDF4 dataset"""
        try: 
            self.save()
        except: pass #avoid errors when closing files in read mode
        if self.dataset != None: self.dataset.close()

        self.dataset = None
        self.convention = None

        self._Dimensions = None
        self._Listener = None
        self._Source = None
        self._Receiver = None
        self._Emitter = None

        self._Metadata = None

        return 
    
    def initialize_room(self, room=None): #TODO: move to rooms
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
        self._convention.define_measurements(self, measurements)
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
        self._convention.define_data(self, samples, string_length)
        return

    @property
    def Dimensions(self): 
        """:class:`sofa.DimensionAccess` for the file dimensions"""
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Dimensions is None: self._Dimensions = data.dimensions.DimensionAccess(self.dataset)
        return self._Dimensions
    
    ## experimental setup
    @property
    def Listener(self): 
        """:class:`sofa.spatial.Object` for the Listener"""
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Listener is None: self._Listener = data.spatial.Object(self, "Listener")
        return self._Listener
    
    @property
    def Source(self):
        """:class:`sofa.spatial.Object` for the Source"""
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Source is None: self._Source = data.spatial.Object(self, "Source")
        return self._Source
    
    @property
    def Receiver(self): 
        """:class:`sofa.spatial.Object` for the Receiver(s)"""
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Receiver is None: self._Receiver = data.spatial.Object(self, "Receiver")
        return self._Receiver
    
    @property
    def Emitter(self): 
        """:class:`sofa.spatial.Object` for the Emitter(s)"""
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Emitter is None: self._Emitter = data.spatial.Object(self, "Emitter")
        return self._Emitter
        
    ## room
    @property
    def Room(self): 
        """RoomType specific access for the room data, see :mod:`sofa.roomtypes`"""
        return rooms.get(self.dataset)
    
    ## data
    @property
    def Data(self): 
        """DataType specific access for the measurement data, see :mod:`sofa.datatypes`"""
        return data.get(self.dataset)

    ## metadata
    @property
    def Metadata(self): 
        """:class:`sofa.Metadata` for the file metadata"""
        if self.dataset is None: 
            print("No dataset open!")
            return None
        if self._Metadata is None: self._Metadata = access.MetadataAccess(self.dataset)
        return self._Metadata

