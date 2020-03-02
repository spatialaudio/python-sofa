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

"""Classes for accessing attribute in the underlying :class:`netCDF4.Dataset`.
"""

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
        if name in self.list_attributes():
            print(name, "already in .SOFA dataset, setting value instead")
            self.set_attribute(name, value)
            return
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