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

#__all__ = ["get_values_from_array", "DatasetVariables", "StringArray", "Variable"]

import numpy as np


def filled_if_masked(array):
    if type(array) is np.ma.MaskedArray: return array.filled()
    return array


def is_integer(val):
    return np.issubdtype(type(val), np.integer)


def get_slice_tuple(dimensions, indices=None):
    if indices is None: return tuple([slice(None) for x in dimensions])
    if "M" in indices and "I" in dimensions:
        indices["I"] = 0 if is_integer(indices["M"]) else slice(None)
    return tuple([slice(None) if x not in indices else indices[x] for x in dimensions])


def get_default_dimension_order(dimensions, indices=None):
    if indices is None: return dimensions
    if "M" in indices and "I" in dimensions:
        indices["I"] = 0 if is_integer(indices["M"]) else slice(None)
    dim_order = tuple([x for x in dimensions if x not in indices or not is_integer(indices[x])])
    return dim_order


def get_dimension_order_transposition(original, new):
    old = original
    if "M" in new and "I" in old:  # replace "I" with "M" if necessary
        old = list(old)
        old[old.index("I")] = "M"
    if "M" in old and "I" in new:  # replace "I" with "M" if necessary
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
    if dim_order is None: return filled_if_masked(array[sls])

    old_dim_order = get_default_dimension_order(dimensions, indices)
    transposition = get_dimension_order_transposition(old_dim_order, dim_order)

    try:
        return filled_if_masked(np.transpose(array[sls], transposition))
    except Exception as e:
        raise Exception(
            "dimension mismatch: cannot transpose from {0} to {1} in order {2}, error {3}".format(old_dim_order,
                                                                                                  dim_order,
                                                                                                  transposition, e))
    return transposed

class _VariableBase:
    #    """Access the values of a NETCDF4 dataset variable"""
    def __init__(self, database, name):
        #        """
        #        Parameters
        #        ----------
        #        database : :class:`sofa.Database`
        #            Parent database instance
        #        name : str
        #            Variable name within the netCDF4 dataset
        #        """
        self._database = database
        self._name = name

    @property
    def name(self):
        return self._name
    @property
    def database(self):
        return self._database

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self._Matrix.__getattribute__(name)
            except: raise

    def __setattr__(self, name, value):
        if '_' in name:
            super().__setattr__(name, value)
            return

        # TODO: are there any cases in which this is wrong?
        self._Matrix.setncattr_string(name, value)

    def initialize(self, dims, data_type="d", fill_value=0):
        """Create the variable in the underlying netCDF4 dataset"""
        defined = self.database.Dimensions.list_dimensions()
        missing = []
        for d in dims:
            if d not in defined: missing.append(d)
        if len(missing): raise Exception("Cannot initialize, dimensions undefined: {0}".format(missing))
        try:
            self.database.dataset.createVariable(self.name, data_type, dims, fill_value=fill_value)
        except Exception as ex:
            raise Exception(
                "Failed to create variable for {0} of type {1} with fill value {2}, error = {3}".format(self.name,
                                                                                                        data_type, dims,
                                                                                                        fill_value,
                                                                                                        str(ex)))

    @property
    def _Matrix(self):
        if self.name not in self.database.Variables.list_variables(): return None
        return self.database.dataset[self.name]

    def exists(self):
        """Returns
        -------
        exists : bool
            True if variable exists, False otherwise
        """
        return self._Matrix is not None

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

    def _reorder_values_for_set(self, values, indices=None, dim_order=None, repeat_dim=None):
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
            raise Exception("Variable {0} not initialized".format(self.name))
        dimensions = self.dimensions()
        if "I" in dimensions:
            dimensions = list(dimensions)
            dimensions[dimensions.index("I")] = "M"
            dimensions = tuple(dimensions)

            if indices is not None and "M" in indices.keys(): indices["M"] = 0

        if dim_order is not None and "I" in dim_order:
            dim_order = list(dim_order)
            dim_order[dim_order.index("I")] = "M"
            dim_order = tuple(dim_order)
        if repeat_dim is not None and "I" in repeat_dim:
            repeat_dim = list(repeat_dim)
            repeat_dim[repeat_dim.index("I")] = "M"
            repeat_dim = tuple(repeat_dim)

        sls = ()
        for d in dimensions:
            sl = slice(None)
            if indices is not None and d in indices: sl = indices[d]
            sls = sls + (sl,)
        new_values = np.asarray(values)

        # repeat along provided dimensions
        full_dim_order = dim_order
        if repeat_dim is not None:
            if full_dim_order is None:
                full_dim_order = tuple(x for x in dimensions if x not in repeat_dim)
            for d in repeat_dim:
                if dim_order is not None and d in dim_order:
                    raise Exception("cannot repeat values along dimension {0}: dimension already provided".format(d))
                    return None
                i = self.axis(d)
                if i is None:
                    raise Exception(
                        "cannot repeat values along dimension {0}: dimension unused by variable {1}".format(d,
                                                                                                            self.name))
                    return None
                count = self._Matrix[sls].shape[i]
                new_values = np.repeat([new_values], count, axis=0)
                full_dim_order = (d,) + full_dim_order

        # change order if necessary
        if full_dim_order is not None:
            do = ()
            for d in dimensions:
                if d in full_dim_order:
                    if indices is not None and d in indices.keys() and type(indices[d]) != slice:
                        raise Exception(
                            "cannot assign values to variable {0}: dimension {1} is {2}, not a slice".format(self.name,
                                                                                                             d, type(
                                    indices[d])))
                        return None
                    do = do + (full_dim_order.index(d),)
                elif indices is None or d not in indices.keys():
                    raise Exception("cannot assign values to variable {0}: missing dimension {1}".format(self.name, d))
                    return None
            new_values = np.transpose(new_values, do)

        return new_values, sls

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
        new_values, sls = self._reorder_values_for_set(values, indices, dim_order, repeat_dim)

        # assign
        self._Matrix[sls] = new_values
        return

class Variable(_VariableBase):
    def __init__(self, database, name):
        super().__init__(database, name)
        self._unit_proxy = None

    @property
    def Units(self):
        """Units of the values"""
        if not self.exists():
            raise Exception("failed to get Units of {0}, variable not initialized".format(self.name))
        if self._unit_proxy is None: return self._Matrix.Units
        return self._unit_proxy.Units
    @Units.setter
    def Units(self, value):
        if not self.exists():
            raise Exception("failed to set Units of {0}, variable not initialized".format(self.name))
        self._Matrix.Units = value

class DatasetVariables:
    #    """Direct access the dataset variables"""
    def __init__(self, database):
        self.database = database

    def get_variable(self, name):
        """Parameters
        ----------
        name : str
            Name of the variable

        Returns
        -------
        value : `sofa.access.Variable`
            Access object for the variable
        """
        return Variable(self.database, name)

    def get_string_array(self, name):
        """Parameters
        ----------
        name : str
            Name of the string array

        Returns
        -------
        value : `sofa.access.StringArray`
            Access object for the string array
        """
        return StringArray(self.database, name)

    def create_variable(self, name, dims, data_type="d", fill_value=0):
        """Parameters
        ----------
        name : str
            Name of the variable
        dims : tuple(str)
            Dimensions of the variable

        Returns
        -------
        value : `sofa.access.Variable`
            Access object for the variable
        """
        var = self.get_variable(name)
        if var.exists():
            # TODO: add raise error?
            print(name, "already exists in the dataset!")
            return var
        var.initialize(dims, data_type=data_type, fill_value=fill_value)
        return var

    def create_string_array(self, name, dims):
        """Parameters
        ----------
        name : str
            Name of the variable
        dims : tuple(str)
            Dimensions of the variable

        Returns
        -------
        value : `sofa.access.StringArray`
            Access object for the string array
        """
        var = self.get_string_array(name)
        if var.exists():
            # TODO: add raise error?
            print(name, "already exists in the dataset!")
            return var
        var.initialize(dims)
        return var

    def list_variables(self):
        """Returns
        -------
        attrs : list
            List of the existing dataset variable and string array names
        """
        return sorted(self.database.dataset.variables.keys())

    def dump(self):
        """Prints all variables and their dimensions"""
        for vname in self.list_variables():
            print("{0}: {1}".format(vname, self.get_variable(vname).dimensions()))
        return

class StringArray(_VariableBase):
    def initialize(self, dims, data_type="c", fill_value='\0'):
        """Create the zero-padded character array in the underlying netCDF4 dataset.
        Dimension 'S' must be the last dimension, and is appended if not included in dims."""
        if "S" not in dims: dims = dims + ("S",)
        if dims[-1] != "S": raise Exception("Failed to initialize character array with dimensions {0}, 'S' must be last dimension.".format(dims))
        super().initialize(dims, data_type, fill_value)

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
        if dim_order is not None and "S" not in dim_order: dim_order = dim_order + ("S",)
        return super().get_values(indices, dim_order)

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
        if dim_order is not None and "S" not in dim_order: dim_order = dim_order + ("S",)
        # TODO: accept nested lists of strings that may be too short, convert into proper character array
        return super().set_values(values, indices, dim_order, repeat_dim)