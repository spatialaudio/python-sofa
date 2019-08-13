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

"""Classes for accessing arrays and data in the underlying :class:`netCDF4.Dataset`.
"""
__version__='0.1.0'

__all__=["get_values_from_array", "Dimensions", "Metadata", "ArrayVariable", "ScalarVariable"]

import numpy as np

def filled_if_masked(array):
    if type(array) is np.ma.MaskedArray: return array.filled()
    return array

def is_integer(val):
    return np.issubdtype(type(val), np.integer)

def get_slice_tuple(dimensions, indices=None):
    if indices == None: return tuple([slice(None) for x in dimensions])
    if "M" in indices and "I" in dimensions:
        indices["I"] = 0 if is_integer(indices["M"]) else slice(None)
    return tuple([slice(None) if x not in indices else indices[x] for x in dimensions])

def get_default_dimension_order(dimensions, indices=None):
    if indices == None: return dimensions
    if "M" in indices and "I" in dimensions:
        indices["I"] = 0 if is_integer(indices["M"]) else slice(None)
    dim_order = tuple([x for x in dimensions if x not in indices or not is_integer(indices[x])])
    return dim_order

def get_dimension_order_transposition(original, new):
    old = original
    if "M" in new and "I" in old: # replace "I" with "M" if necessary
        old = list(old)
        old[old.index("I")] = "M"
    if "M" in old and "I" in new: # replace "I" with "M" if necessary
        new = list(new)
        new[new.index("I")] = "M"
    transposition = [old.index(x) for x in new]
    return tuple(transposition)

def get_values_from_array(array, dimensions, indices=None, dim_order=None):
    """Extract values of a given range from an array
    
    Parameters
    ----------
    array : array_like
        Source array
    dimensions : tuple of str
        Names of the array dimensions in order
    indices : dict(key:str, value:int or slice), optional
        Key: dimension name, value: indices to be returned, complete axis assumed if not provided
    dim_order : tuple of str
        Desired order of dimensions in the output array

    Returns
    -------
    values : np.ndarray
        Requested array range in regular or desired dimension order, if provided
    """
    sls = get_slice_tuple(dimensions, indices)
    if dim_order == None: return filled_if_masked(array[sls])

    old_dim_order = get_default_dimension_order(dimensions, indices)
    transposition = get_dimension_order_transposition(old_dim_order, dim_order)

    try: return filled_if_masked(np.transpose(array[sls], transposition))
    except Exception as e: raise Exception("dimension mismatch: cannot transpose from {0} to {1} in order {2}, error {3}".format(old_dim_order, dim_order, transposition, e))
    return transposed


class Dimensions:
    """Dimensions specified by SOFA as int"""
    def __init__(self, dataset):
        self.dataset = dataset
        return
    
    @property
    def C(self): 
        """Coordinate dimension size"""
        return self._dim_size("C")

    @property
    def I(self): 
        """Scalar dimension size"""
        return self._dim_size("I")
    
    @property
    def M(self): 
        """Number of measurements"""
        return self._dim_size("M")
    @property
    def R(self): 
        """Number of receivers"""
        return self._dim_size("R")
    @property
    def E(self): 
        """Number of emitters"""
        return self._dim_size("E")
    @property
    def N(self): 
        """Number of data samples per measurement"""
        return self._dim_size("N")
    @property
    def S(self): 
        """Largest data string size"""
        return self._dim_size("S")

    def _dim_size(self, dim):
        if dim not in self.dataset.dimensions: 
            print("dimension {0} not initialized".format(dim))
            return None
        return self.dataset.dimensions[dim].size
		
    def dump(self):
        """Prints all dimension sizes"""
        for dim in self.dataset.dimensions:
            print("{0}: {1}".format(dim, self.dataset.dimensions[dim].size))
        return

class Metadata:
#    """Access the dataset metadata"""
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
        return sorted(self.dataset.ncattrs())

    def dump(self):
        """Prints all metadata attributes"""
        for attr in self.list_attributes():
            print("{0}: {1}".format(attr, self.get_attribute(attr)))
        return
		
########################################################################
# Variable access
########################################################################
class _VariableBase:
#    """Access the values of a NETCDF4 dataset variable"""
    def __init__(self, dataset, name):
#        """
#        Parameters
#        ----------
#        dataset : :class:`netCDF4.Dataset`
#            Underlying netCDF4 dataset instance
#        name : str
#            Variable name within the dataset
#        """
        self.dataset = dataset
        self.name = name
        self.unit_proxy = None

    @property
    def _Matrix(self): 
        if self.name not in self.dataset.variables: return None
        return self.dataset[self.name]

    @property
    def Units(self):
        """Units of the values"""
        if not self.exists():
            raise Exception("failed to get Units of {0}, variable not initialized".format(self.name))
        if self.unit_proxy == None: return self._Matrix.Units
        return self.unit_proxy._Matrix.Units
    @Units.setter
    def Units(self, value):
        if not self.exists():
            raise Exception("failed to set Units of {0}, variable not initialized".format(self.name))
        self._Matrix.Units = value
   
    def exists(self):
        """Returns
        -------
        exists : bool
            True if variable exists, False otherwise
        """
        return self._Matrix != None

class ArrayVariable(_VariableBase):
    def initialize(self, dims, data_type="d", fill_value = 0):
        """Create the variable in the underlying netCDF4 dataset"""
        try: self.dataset.createVariable(self.name, data_type, dims, fill_value=fill_value)
        except Exception as ex: raise Exception("Failed to create variable for {0} of type {1} with fill value {2}, error = {3}".format(self.name, data_type, dims, fill_value, str(ex)))

    def dimensions(self):
        """Returns
        -------
        dimensions : tuple of str
            Variable dimension names in order
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

    def get_values(self, indices=None, dim_order=None):
        """
        Parameters
        ----------
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Desired order of dimensions in the output array
    
        Returns
        -------
        values : np.ndarray
            Requested array range in regular or desired dimension order, if provided
        """
        if not self.exists():
            raise Exception("failed to get values of {0}, variable not initialized".format(self.name))
        return get_values_from_array(self._Matrix, self.dimensions(), indices=indices, dim_order=dim_order)

    def set_values(self, values, indices=None, dim_order=None, repeat_dim=None):
        """
        Parameters
        ----------
        values : np.ndarray
            New values for the array range
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be set, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Dimension names in provided order, regular order assumed
        repeat_dim : tuple of str, optional
            Tuple of dimension names along which to repeat the values
        """
        if not self.exists():
            raise Exception("failed to set values of {0}, variable not initialized".format(self.name))
        dimensions = self.dimensions()
        if "I" in dimensions:
            dimensions = list(dimensions)
            dimensions[dimensions.index("I")] = "M"
            dimensions = tuple(dimensions)

            if indices != None and "M" in indices.keys(): indices["M"]=0

        if dim_order != None and "I" in dim_order:
                dim_order = list(dim_order)
                dim_order[dim_order.index("I")] = "M"
                dim_order = tuple(dim_order)
        if repeat_dim != None and "I" in repeat_dim:
                repeat_dim = list(repeat_dim)
                repeat_dim[repeat_dim.index("I")] = "M"
                repeat_dim = tuple(repeat_dim)

        sls = ()
        for d in dimensions:
            sl = slice(None)
            if indices != None and d in indices: sl = indices[d]
            sls = sls + (sl,)
        new_values = np.asarray(values)
        
        # repeat along provided dimensions
        full_dim_order = dim_order
        if repeat_dim != None:
            if full_dim_order == None:
                full_dim_order = tuple(x for x in dimensions if x not in repeat_dim)
            for d in repeat_dim:
                if dim_order != None and d in dim_order:
                    raise Exception("cannot repeat values along dimension {0}: dimension already provided".format(d))
                    return None
                i = self.axis(d)
                if i == None:
                    raise Exception("cannot repeat values along dimension {0}: dimension unused by variable {1}".format(d, self.name))
                    return None
                count = self._Matrix[sls].shape[i]
                new_values = np.repeat([new_values], count, axis = 0)
                full_dim_order = (d,) + full_dim_order

        # change order if necessary
        if full_dim_order != None:
            do = ()
            for d in dimensions:
                if d in full_dim_order:
                    if indices != None and d in indices.keys() and type(indices[d]) != slice:
                        raise Exception("cannot assign values to variable {0}: dimension {1} is {2}, not a slice".format(self.name, d, type(indices[d])))
                        return None
                    do = do + (full_dim_order.index(d),)
                elif indices == None or d not in indices.keys():
                    raise Exception("cannot assign values to variable {0}: missing dimension {1}".format(self.name, d))
                    return None
            new_values = np.transpose(new_values, do)

        # assign
        self._Matrix[sls] = new_values
        return

class ScalarVariable(_VariableBase):
    def initialize(self, data_type="d", fill_value = 0):
        """Create the variable in the underlying netCDF4 dataset"""
        dims=("I",)
        try: self.dataset.createVariable(self.name, data_type, dims, fill_value=fill_value)
        except Exception as ex: raise Exception("Failed to create variable for {0} of type {1} with fill value {2}, error = {3}".format(self.name, data_type, dims, fill_value, str(ex)))

    def get_value(self):
        """
        Returns
        -------
        value : double
        """
        if not self.exists():
            raise Exception("failed to get value of {0}, variable not initialized".format(self.name))

        return np.squeeze(self._Matrix[:])

    def set_value(self, value):
        """
        Parameters
        ----------
        value : double
            New value
        """
        if not self.exists():
            raise Exception("failed to set value of {0}, variable not initialized".format(self.name))

        self._Matrix[:] = value
        return

    # TODO: fix sphinx documentation order, currently adds inherited members in the middle
