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

"""Special access classes.
"""
__version__='0.1.0'

from . import _util as util

import numpy as np

#from . import _data as data
#from . import _rooms as rooms
#from . import _conventions as conventions

#from enum import Enum
#import netCDF4 as ncdf
#from datetime import datetime

class MetadataAccess:
    """Access the .sofa file's metadata"""
    def __init__(self, dataset):
        self.dataset = dataset

    def get_attribute(self, name):
        """Parameters
        ----------
        name : str
            Name of the attribute

        Returns
        -------
        value : str
            Value of the attribute
        """
        if name not in self.dataset.ncattrs(): return ""
        return self.dataset.getncattr(name)

    def set_attribute(self, name, value):
        """Parameters
        ----------
        name : str
            Name of the attribute
        value : str
            New value of the attribute
        """
        if name not in self.dataset.ncattrs(): return self.create_attribute(name, value=value)
        self.dataset.setncattr(name, value)

    def create_attribute(self, name, value=""):
        """Parameters
        ----------
        name : str
            Name of the attribute
        value : str, optional
            New value of the attribute
        """
        self.dataset.NewSOFAAttribute = value
        self.dataset.renameAttribute("NewSOFAAttribute", name)

    def list_attributes(self):
        """Returns
        -------
        attrs : list
            List of the existing dataset attribute names
        """
        return self.dataset.ncattrs()

class VariableAccess:
    """Access the values of a NETCDF4 dataset variable"""
    def __init__(self, dataset, name):
        self.dataset = dataset
        self.name = name

    @util.DatasetVariable()
    def _Matrix(self): return self.name
    def dimensions(self):
        """Returns
        -------
        dimensions : tuple(str)
            Tuple of dimension names in order
        """
        if not self.exists(): return None
        return self._Matrix.dimensions
    def axis(self, dim): 
        """Parameters
        ----------
        dim : str
            Name of the dimension
        Returns
        -------
        axis : int
            Index of the dimension axis or None if unused
        """
        if dim in self.dimensions(): return self.dimensions().index(dim)
        if dim == "M" and "I" in self.dimensions(): return self.dimensions().index("I")
        return None

    @property 
    def _MatrixM(self):
        if "M" in self.dimensions(): return self._Matrix[:]
        values = np.repeat(self._Matrix[:], self.dataset.dimensions["M"].size, axis=self.axis("M"))
        return values

    def exists(self):
        """Returns
        -------
        exists : bool
            True if variable exists, False otherwise
        """
        return self._Matrix != None

    def get_values(self, indices=None, dim_order=None):
        """
        Parameters
        ----------
        indices : dict(str, int or slice), optional
            Keys: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple(str), optional
            Tuple of dimension names in desired order
            
        Returns
        -------
        values : np.ndarray
            Requested array range in regular or desired dimension order, if provided
        """
        if not self.exists(): return None
        sls = ()
        for d in self.dimensions():
            sl = slice(None)
            if indices != None and d in indices.keys(): sl = indices[d]
            sls = sls + (sl,)
        if dim_order == None: return self._MatrixM[sls]

        range_dims = tuple(x for x in self.dimensions() if indices==None or x not in indices.keys() or type(indices[x]) != int)
        do = ()
        for d in dim_order:
            i = None
            if d in range_dims: i = range_dims.index(d)
            elif d=="I" and "M" in range_dims: i = range_dims.index("M")
            elif d=="M" and "I" in range_dims: i = range_dims.index("I")
            else: raise Exception('cannot transpose variable {0}: no dimension {1}'.format(self.name,d))
            do = do + (i,)
        return np.transpose(self._MatrixM[sls], do)

    def set_values(self, values, indices=None, dim_order=None, repeat_dim=None):
        """
        Parameters
        ----------
        values : np.ndarray
            New values for the array range
        indices : dict(str, int or slice), optional
            Keys: dimension name, value: indices to be set, complete axis assumed if not provided
        dim_order : tuple(str), optional
            Tuple of dimension names in provided order, regular order assumed
        repeat_dim : tuple(str), optional
            Tuple of dimension names along which to repeat the values
        """
        if not self.exists():
            print("Failed to set values of",self.name,": variable not initialized")
            return
        sls = ()
        for d in self.dimensions():
            sl = slice(None)
            if indices != None and d in indices.keys(): sl = indices[d]
            sls = sls + (sl,)
        new_values = np.asarray(values)
        
        # repeat along provided dimensions
        full_dim_order = dim_order
        if repeat_dim != None:
            if full_dim_order == None:
                full_dim_order = tuple(x for x in self.dimensions() if x not in repeat_dim)
            for d in repeat_dim:
                if dim_order != None and d in dim_order:
                    raise Exception("cannot repeat values along dimension", d, ": dimension already provided")
                    return None
                i = self.axis(d)
                if i == None:
                    raise Exception("cannot repeat values along dimension", d, ": dimension unused by variable", self.name)
                    return None
                count = self._Matrix[sls].shape[i]
                new_values = np.repeat([new_values], count, axis = 0)
                full_dim_order = (d,) + full_dim_order

        # change order if necessary
        if full_dim_order != None:
            do = ()
            for d in self.dimensions():
                if d in full_dim_order:
                    if indices != None and d in indices.keys() and type(indices[d]) != slice:
                        raise Exception("cannot assign values to variable", self.name, ": dimension", d, "not a slice")
                        return None
                    do = do + (full_dim_order.index(d),)
                elif indices == None or d not in indices.keys():
                    raise Exception("cannot assign values to variable", self.name, ": missing dimension", d)
                    return None
            new_values = np.transpose(new_values, do)

        # assign
        self._Matrix[sls] = new_values

class VariableAccessWithUnits(VariableAccess):
    @property
    def Units(self): return self._Matrix.Units
    @Units.setter
    def Units(self, value): self._Matrix.Units = value

class ScalarVariableAccess:
    """Access the value of a NETCDF4 dataset variable with sole dimension I"""
    def __init__(self, dataset, name):
        self.dataset = dataset
        self.name = name

    @util.DatasetVariable()
    def _Matrix(self): return self.name
    def dimensions(self):
        """Returns
        -------
        dimensions : tuple(str)
            Tuple of dimension names in order
        """
        if not self.exists(): return None
        return self._Matrix.dimensions
    def axis(self, dim): 
        """Parameters
        ----------
        dim : str
            Name of the dimension
        Returns
        -------
        axis : int
            Index of the dimension axis or None if unused
        """
        if dim in self.dimensions(): return self.dimensions().index(dim)
        if dim == "M" and "I" in self.dimensions(): return self.dimensions().index("I")
        return None

    def exists(self):
        """Returns
        -------
        exists : bool
            True if variable exists, False otherwise
        """
        return self._Matrix != None

    def get_value(self):
        """
        Returns
        -------
        value : double
        """
        if not self.exists(): return None
        return self._Matrix[0]

    def set_value(self, value):
        """
        Parameters
        ----------
        valuee : double
            New value
        """
        if not self.exists():
            print("Failed to set value of",self.name,": variable not initialized")
            return
        # assign
        self._Matrix[0] = value

class ScalarVariableAccessWithUnits(ScalarVariableAccess):
    @property
    def Units(self): return self._Matrix.Units
    @Units.setter
    def Units(self, value): self._Matrix.Units = value

