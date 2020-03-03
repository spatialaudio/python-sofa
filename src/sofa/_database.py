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
__version__ = '0.1.0'

from . import access
from . import datatypes
from . import roomtypes
from . import conventions

from . import spatial

from enum import Enum
import netCDF4 as ncdf
from datetime import datetime


class Database(access.ProxyObject):
    """Read and write NETCDF4 files following the SOFA specifications and conventions"""

    def __init__(self):
        super().__init__(self, "")

        self._dataset = None
        self._convention = None

        self._Dimensions = None
        self._Listener = None
        self._Source = None
        self._Receiver = None
        self._Emitter = None

        self._Metadata = None
        self._Variables = None

    @staticmethod
    def create(path, convention, dimensions=None):
        """Create a new .sofa file following a SOFA convention

        Parameters
        ----------
        path : str
            Relative or absolute path to .sofa file    
        convention : str
            Name of the SOFA convention to create, see :func:`sofa.conventions.implemented`
        dimensions : dict or int, optional
            Number of measurements or dict of dimensions to define (standard dimensions: "M": measurements, "R": receivers, "E": emitters, "N": data length)

        Returns
        -------
        database : :class:`sofa.Database`
        """
        sofa = Database()
        sofa.dataset = ncdf.Dataset(path, mode="w")
        if dimensions is not None:
            try:
                for d,v in dimensions.items():
                    sofa.Dimensions.create_dimension(d, v)
            except:
                sofa.Dimensions.create_dimension("M", dimensions)

        sofa._convention = conventions.List[convention]()

        sofa.convention.add_metadata(sofa)
        sofa.DateCreated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return sofa

    @staticmethod
    def open(path, mode='r', parallel=False):
        """Parameters
        ----------
        path : str
            Relative or absolute path to .sofa file
        mode : str, optional
            File access mode ('r': readonly, 'r+': read/write)
        parallel : bool, optional
            Whether to open the file with parallel access enabled (requires parallel-enabled netCDF4)

        Returns
        -------
        database : :class:`sofa.Database`
        """
        if mode == 'w':
            print("Invalid file creation method, use create instead.")
            return None
        sofa = Database()
        sofa.dataset = ncdf.Dataset(path, mode=mode, parallel=parallel)
        if sofa.dataset.SOFAConventions in conventions.implemented():
            sofa._convention = conventions.List[sofa.dataset.SOFAConventions]()
        else:
            default = "General" + sofa.dataset.DataType
            sofa._convention = conventions.List[default]()
        return sofa

    def close(self):
        #        """Save and close the underlying NETCDF4 dataset"""
        try:
            self.save()
        except:
            pass  # avoid errors when closing files in read mode
        if self.dataset is not None: self.dataset.close()

        self._dataset = None
        self._convention = None

        self._Dimensions = None
        self._Listener = None
        self._Source = None
        self._Receiver = None
        self._Emitter = None

        self._Metadata = None

        return

    def save(self):
        #        """Save the underlying NETCDF4 dataset"""
        if self.dataset is None: return
        self.DateModified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dataset.sync()

    @property
    def convention(self): return self._convention

    ## data    
    @property
    def Data(self):
        """DataType specific access for the measurement data, see :mod:`sofa.datatypes`"""
        return datatypes.get(self)

    @property
    def Dimensions(self):
        """:class:`sofa.access.Dimensions` for the database dimensions"""
        if self.dataset is None:
            print("No dataset open!")
            return None
        if self._Dimensions is None: self._Dimensions = access.Dimensions(self.dataset)
        return self._Dimensions

    ## experimental setup
    @property
    def Listener(self):
        """:class:`sofa.spatial.SpatialObject` for the Listener"""
        if self.dataset is None:
            print("No dataset open!")
            return None
        if self._Listener is None: self._Listener = spatial.SpatialObject(self, "Listener")
        return self._Listener

    @property
    def Source(self):
        """:class:`sofa.spatial.SpatialObject` for the Source"""
        if self.dataset is None:
            print("No dataset open!")
            return None
        if self._Source is None: self._Source = spatial.SpatialObject(self, "Source")
        return self._Source

    @property
    def Receiver(self):
        """:class:`sofa.spatial.SpatialObject` for the Receiver(s)"""
        if self.dataset is None:
            print("No dataset open!")
            return None
        if self._Receiver is None: self._Receiver = spatial.SpatialObject(self, "Receiver")
        return self._Receiver

    @property
    def Emitter(self):
        """:class:`sofa.spatial.SpatialObject` for the Emitter(s)"""
        if self.dataset is None:
            print("No dataset open!")
            return None
        if self._Emitter is None: self._Emitter = spatial.SpatialObject(self, "Emitter")
        return self._Emitter

    ## room
    @property
    def Room(self):
        """RoomType specific access for the room data, see :mod:`sofa.roomtypes`"""
        return roomtypes.get(self)

    ## metadata
    @property
    def Metadata(self):
        """:class:`sofa.access.Metadata` for the database metadata"""
        if self.dataset is None:
            print("No dataset open!")
            return None
        if self._Metadata is None: self._Metadata = access.Metadata(self.dataset)
        return self._Metadata

    ## direct access to variables
    @property
    def Variables(self):
        """:class:`sofa.access.DatasetVariables` for direct access to database variables"""
        if self.dataset is None:
            print("No dataset open!")
            return None
        if self._Variables is None: self._Variables = access.DatasetVariables(self)
        return self._Variables
