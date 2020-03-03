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

from .. import access
from .coordinates import *
import numpy as np


class SpatialObject(access.ProxyObject):
    """Spatial object such as Listener, Receiver, Source, Emitter"""

    def __init__(self, database, name):
        super().__init__(database, name)
        return

    @property
    def Position(self):
        """Position of the spatial object relative to its reference system"""
        return Coordinates(self, "Position")

    @property
    def View(self):
        """View (x-axis) of the spatial object relative to its reference system"""
        return Coordinates(self, "View")

    @property
    def Up(self):
        """Up (z-axis) of the spatial object relative to its reference system"""
        return Coordinates(self, "Up")

    @property
    def Type(self):
        """Coordinate syste, of the values"""
        if not self.exists():
            raise Exception("failed to get Type of {0}, variable not initialized".format(self.name))
        if self._unit_proxy is None: return self._Matrix.Type
        return self._unit_proxy.Type
    @Type.setter
    def Type(self, value):
        if not self.exists():
            raise Exception("failed to set Type of {0}, variable not initialized".format(self.name))
        self._Matrix.Type = value

    def initialize(self, fixed=[], variances=[], count=None):
        """Create the necessary variables and attributes

        Parameters
        ----------
        fixed : list(str), optional
            List of spatial coordinates that are fixed for all measurements ["Position", "View", "Up"]
        variances : list(str), optional
            List of spatial coordinates that vary between measurements ["Position", "View", "Up"],
            overrides mentions in fixed
        count : int, optional
            Number of objects (such as Emitters or Receivers), ignored for Listener and Source
        """
        mentioned = fixed + variances
        if "Position" not in mentioned:
            if not self.Position.exists(): raise ValueError("{0}.initialize: Missing 'Position' in fixed or variances argument".format(self.name))
        if "Up" in mentioned and "View" not in mentioned:
            if not self.View.exists(): raise ValueError("{0}.initialize: Missing 'View' in fixed or variances argument".format(self.name))

        ldim = self.Position.get_local_dimension()
        if ldim is None:
            if count is None: count = 1
        else:
            if count is None and ldim in self.database.Dimensions.list_dimensions():
                count = self.database.Dimensions.get_dimension(ldim)
            if count is None and "count" in self.database.convention.default_objects[self.name].keys():
                count = self.database.convention.default_objects[self.name]["count"]
            if count is None: raise Exception(self.name, "{0} count missing!".format(self.name))
        self.database.convention.validate_spatial_object_settings(self.name, fixed, variances, count)
        if ldim is not None and ldim not in self.database.Dimensions.list_dimensions():
            self.database.Dimensions.create_dimension(ldim, count)

        self.create_attribute("Description")
        self.initialize_coordinates(fixed, variances)
        self.database.convention.set_default_spatial_values(self)

    def initialize_coordinates(self, fixed=[], variances=[]):
        """
        Parameters
        ----------
        fixed : list(str), optional
            List of spatial coordinates that are fixed for all measurements ["Position", "View", "Up"]
        variances : list(str), optional
            List of spatial coordinates that vary between measurements ["Position", "View", "Up"],
            overrides mentions in fixed
        """
        mentioned = fixed + variances
        for c in mentioned:
            var = self.__getattribute__(c)
            if not var.exists(): var.initialize(c in variances)

    def get_pose(self, indices=None, dim_order=None, system=None, angle_unit=None):
        """ Gets the spatial object coordinates or their defaults if they have not been defined. Relative spatial objects return their global pose, or their reference object's pose values if theirs are undefined.

        Parameters
        ----------
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Desired order of dimensions in the output arrays
        system : str, optional
            Target coordinate system
        angle_unit : str, optional
            Unit for spherical angles in the output arrays

        Returns
        -------
        position, view, up : np.ndarray, np.ndarray, np.ndarray
            Spatial object reference system

        """

        if angle_unit is None: angle_unit = "rad"
        anchor = self.Position.get_global_reference_object()
        if anchor is None:  # this is an object in the global coordinate system
            default_order = ("I", "C")
            position = np.asarray([[0, 0, 0]])
            view = np.asarray([[1, 0, 0]])
            up = np.asarray([[0, 0, 1]])

        else:  # this is an object defined relative to another
            ldim = self.Position.get_local_dimension()
            lcount = self.database.Dimensions.get_dimension(ldim)

            anchor_order = ("I", "C")
            default_order = (ldim,) + anchor_order
            if dim_order is None: dim_order = access.get_default_dimension_order(self.Position.dimensions(), indices)

            anchor_position, anchor_view, anchor_up = anchor.get_pose(indices=indices, dim_order=anchor_order,
                                                                      system=System.Cartesian)
            position = np.repeat(np.expand_dims(anchor_position, 0), lcount, axis=0)
            view = np.repeat(np.expand_dims(anchor_view, 0), lcount, axis=0)
            up = np.repeat(np.expand_dims(anchor_up, 0), lcount, axis=0)

        # get existing values or use defaults
        if self.Position.exists():
            position = self.Position.get_global_values(indices, dim_order, system, angle_unit)
        else:
            position = access.get_values_from_array(
                System.convert(position, default_order, System.Cartesian, system, angle_unit,
                                           angle_unit),
                default_order, dim_order=dim_order)

        if self.View.exists():
            view = self.View.get_global_values(indices, dim_order, system, angle_unit)
        else:
            view = access.get_values_from_array(
                System.convert(view, default_order, System.Cartesian, system, angle_unit,
                                           angle_unit),
                default_order, dim_order=dim_order)

        if self.Up.exists():
            up = self.Up.get_global_values(indices, dim_order, system, angle_unit)
        else:
            up = access.get_values_from_array(
                System.convert(up, default_order, System.Cartesian, system, angle_unit,
                                           angle_unit),
                default_order, dim_order=dim_order)

        return position, view, up
