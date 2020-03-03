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

class ProxyObject:
    """Proxy object that provides access to variables and attributes of a name group in the netCDF4 dataset"""

    def __init__(self, database, name):
        self._database = database
        self._name = name
        self.standard_dimensions = dict()
        return

    @property
    def database(self):
        return self._database

    @property
    def name(self):
        return self._name

    @property
    def dataset(self):
        try:
            return self._dataset
        except:
            if self.database is None: return None
            return self.database.dataset

    @dataset.setter
    def dataset(self, value):
        try: self._dataset = value
        except: raise

    @staticmethod
    def _valid_data_name(name):
        if "_" in name: return False
        if name in ["name", "database", "dataset", "Metadata", "Variables", "Type", "Units"]: return False
        return True

    def _get_dataset_value_or_none(self, name):
        if self.dataset is None: raise Exception("No dataset open!")
        if not ProxyObject._valid_data_name(name): raise Exception("{0} is not a valid name for a dataset value.")

        container_name = self.name + name
        if container_name in self.database.Variables.list_variables():
            # attribute is a variable, return proper access class
            var = self.database.Variables.get_variable(container_name)
            if "S" not in var.dimensions(): return var
            else: return self.database.Variables.get_string_array(container_name)
        elif container_name in self.database.Metadata.list_attributes():
            # attribute is an attribute in the netcdf-4 dataset
            return self.database.Metadata.get_attribute(container_name)
        else:
            return None

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if not ProxyObject._valid_data_name(name): raise
            value = self._get_dataset_value_or_none(name)
            if value is None:
                print(self.name+name, "not part of .SOFA dataset")
                raise
            return value

    def __setattr__(self, name, value):
        if not ProxyObject._valid_data_name(name) or self.dataset is None:
            super().__setattr__(name, value)
            return

        existing = self._get_dataset_value_or_none(name)
        if existing is None:
            if type(value) == str: # attempting to set an attribute
                print("Adding attribute {0} to .SOFA dataset".format(self.name+name))
                self.create_attribute(name, value)
                return
            raise AttributeError("{0} not part of {1}, use create_... instead.".format(name, self.name)) # we don't know what or where it should be

        container_name = self.name + name

        if type(value) == str:
            self.database.Metadata.set_attribute(container_name, value)
            return

        try: existing.set_values(value)
        except:
            print("Failed to set values on", container_name, "directly, use set_values instead.")
            raise

    def create_attribute(self, name, value=""):
        """Creates the attribute in the netCDF4 dataset with its full name self.name+name

        Parameters
        ----------
        name : str
            Name of the variable
        value : str, optional
            Initial value of the attribute
        """
        self.database.Metadata.create_attribute(self.name + name, value=value)

    def create_variable(self, name, dims, data_type="d", fill_value=0):
        """Creates the variable in the netCDF4 dataset with its full name self.name+name
        
        Parameters
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
        if name in self.standard_dimensions:
            std_dims = self.standard_dimensions[name]
            if dims not in std_dims: raise ValueError("Dimensions {0} not standard: {1}".format(dims, std_dims))
        return self.database.Variables.create_variable(self.name + name, dims, data_type=data_type,
                                                       fill_value=fill_value)

    def create_string_array(self, name, dims):
        """Creates the string array in the netCDF4 dataset with its full name self.name+name

        Parameters
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
        if name in self.standard_dimensions:
            std_dims = self.standard_dimensions[name]
            if dims not in std_dims: raise ValueError("Dimensions {0} not standard: {1}".format(dims, std_dims))
        return self.database.Variables.create_string_array(self.name + name, dims)

#    @property
#    def Description(self):
#        """Informal description of the object"""
#        return self.database.__getattribute__(self.name + "Description")

#    @Description.setter
#    def Description(self, value):
#        self.database.__setattr__(self.name + "Description", value)
