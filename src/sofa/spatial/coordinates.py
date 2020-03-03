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
import numpy as np

# for coordinate transformations
from scipy.spatial.transform import Rotation  ## requires scipy 1.2.0


def sph2cart(alpha, beta, r):
    r"""Spherical to cartesian coordinate transform.

    .. math::
        x = r \cos \alpha \sin \beta \\
        y = r \sin \alpha \sin \beta \\
        z = r \cos \beta

    with :math:`\alpha \in [0, 2\pi), \beta \in [-\frac{\pi}{2}, \frac{\pi}{2}], r \geq 0`

    Parameters
    ----------
    alpha : float or array_like
            Azimuth angle in radians
    beta : float or array_like
            Elevation angle in radians (with 0 denoting azimuthal plane)
    r : float or array_like
            Radius

    Returns
    -------
    x : float or `numpy.ndarray`
        x-component of Cartesian coordinates
    y : float or `numpy.ndarray`
        y-component of Cartesian coordinates
    z : float or `numpy.ndarray`
        z-component of Cartesian coordinates
    """
    x = r * np.cos(alpha) * np.cos(beta)
    y = r * np.sin(alpha) * np.cos(beta)
    z = r * np.sin(beta)
    return x, y, z


def cart2sph(x, y, z):
    r"""Cartesian to spherical coordinate transform.

    .. math::
        \alpha = \arctan \left( \frac{y}{x} \right) \\
        \beta = \arccos \left( \frac{z}{r} \right) \\
        r = \sqrt{x^2 + y^2 + z^2}

    with :math:`\alpha \in [-pi, pi], \beta \in [-\frac{\pi}{2}, \frac{\pi}{2}], r \geq 0`

    Parameters
    ----------
    x : float or array_like
        x-component of Cartesian coordinates
    y : float or array_like
        y-component of Cartesian coordinates
    z : float or array_like
        z-component of Cartesian coordinates

    Returns
    -------
    alpha : float or `numpy.ndarray`
            Azimuth angle in radians
    beta : float or `numpy.ndarray`
            Elevation angle in radians (with 0 denoting azimuthal plane)
    r : float or `numpy.ndarray`
            Radius
    """
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    alpha = np.arctan2(y, x)
    beta = np.arcsin(z / np.where(r != 0, r, 1))
    return alpha, beta, r


def transform(u, rot, x0, invert, is_position):
    if not invert and is_position: u = u - x0
    t = rot.apply(u, inverse=not invert)
    if invert and is_position: t = t + x0
    return t


def _rotation_from_view_up(view, up):
    if len(view) != len(up):
        vlen = len(view)
        ulen = len(up)
        view = np.repeat(view, ulen, axis=0)
        up = np.repeat(up, vlen, axis=0)
    y_axis = np.cross(up, view)
    return Rotation.from_dcm(np.moveaxis(np.asarray([view, y_axis, up]), 0, -1))


def _get_object_transform(ref_object):
    order = ("M", "C")
    if ref_object is None:
        # global coordinate system
        position = np.asarray([[0, 0, 0]])
        view = np.asarray([[1, 0, 0]])
        up = np.asarray([[0, 0, 1]])
    else:
        if ref_object.name == "Receiver" or ref_object.name == "Emitter":
            ldim = ref_object.Position.get_local_dimension()
            if ldim not in order:
                order = (ldim,) + order
        position, view, up = ref_object.get_pose(dim_order=order, system=System.Cartesian)

    if np.size(position.shape) < 3:
        def apply_transform(values, is_position, invert=False):
            rotation = _rotation_from_view_up(view, up)
            return transform(values, rotation, position, invert, is_position)
    else:
        def apply_transform(values, is_position, invert=False):
            rotations = [_rotation_from_view_up(v, u) for v, u in zip(view, up)]
            return np.asarray([transform(values, rot, pos, invert, is_position) for rot, pos in zip(rotations, position)])
    return apply_transform, order


class Units:
    @staticmethod
    def first_unit(unit_string):
        return unit_string.split((" "))[0].split((","))[0]

    @staticmethod
    def last_unit(unit_string):
        return unit_string.split((" "))[-1].split((","))[-1]

    Metre = "metre"  # note: standard assumes british spelling
    Meter = "meter"

    @staticmethod
    def is_Metre(value):
        return Units.last_unit(value).lower() in Units._MeterAliases

    @staticmethod
    def is_Meter(value):
        return Units.last_unit(value).lower() in Units._MeterAliases

    _MeterAliases = {"meter", "meters", "metre", "metres", "m"}

    Degree = "degree"

    @staticmethod
    def is_Degree(value):
        return Units.first_unit(value).lower() in Units._DegreeAliases

    _DegreeAliases = {"degree", "degrees", "°", "deg"}

    Radians = "radians"  # not intended for standard, but necessary for calculations

    @staticmethod
    def is_Radians(value):
        return Units.first_unit(value).lower() in Units._RadiansAliases

    _RadiansAliases = {"radians", "rad"}

    @staticmethod
    def convert_angle_units(coords, dimensions, old_units, new_units):
        """
        Parameters
        ----------
        coords : array_like
            Array of spherical coordinate values
        dimensions : tuple of str
            Names of the array dimensions in order, must contain "C"
        old_units : str
            Units of the angle values in the array
        new_units : str
            Target angle units

        Returns
        -------
        new_coords : np.ndarray
            Array of converted spherical coordinate values in identical dimension order
        """
        if dimensions is None: raise Exception("missing dimension order for unit conversion")
        if new_units is None: return coords
        if old_units is None: raise Exception("missing original unit for unit conversion")

        new_units = new_units.split((" "))[0].split((","))[0]

        conversion = np.ones_like(coords)
        indices = access.get_slice_tuple(dimensions, {"C": slice(2)})

        if (Units.is_Degree(old_units) and Units.is_Degree(new_units)) or \
                (Units.is_Radians(old_units) and Units.is_Radians(new_units)):
            return coords
        elif Units.is_Degree(old_units) and Units.is_Radians(new_units):
            conversion[indices] = np.pi / 180
        elif Units.is_Radians(old_units) and Units.is_Degree(new_units):
            conversion[indices] = 180 / np.pi
        else:
            raise Exception("invalid angle unit in conversion from {0} to {1}".format(old_units, new_units))

        return np.multiply(coords, conversion)


class System:
    """Enum of valid coordinate systems"""
    Cartesian = "cartesian"
    Spherical = "spherical"

    @staticmethod
    def convert(coords, dimensions, old_system, new_system, old_angle_unit=None,
                new_angle_unit=None):  # need to take care of degree/radians unit mess.
        """
        Parameters
        ----------
        coords : array_like
            Array of coordinate values
        dimensions : tuple of str
            Names of the array dimensions in order, must contain "C"
        old_system : str
            Coordinate system of the values in the array
        new_system : str
            Target coordinate system
        old_angle_unit : str, optional
            Unit of the angular spherical coordinates
        new_angle_unit : str, optional
            Target unit of the angular spherical coordinates

        Returns
        -------
        new_coords : np.ndarray
            Array of converted coordinate values in identical dimension order
        """
        if dimensions is None: raise Exception("missing dimension order for coordinate conversion")
        if new_system is None or old_system == new_system:
            if old_system != System.Spherical: return coords
            return Units.convert_angle_units(coords, dimensions, old_angle_unit, new_angle_unit)
        old = None
        conversion = None
        if old_system == System.Cartesian and new_system == System.Spherical:
            conversion = cart2sph
            old = coords
        elif old_system == System.Spherical and new_system == System.Cartesian:
            conversion = sph2cart
            old = Units.convert_angle_units(coords, dimensions, old_angle_unit, Units.Radians)
        else:
            raise Exception("unknown coordinate conversion from {0} to {1}".format(old_system, new_system))
        c_axis = dimensions.index("C")
        # a, b, c = np.split(old, 3, c_axis)
        a = old[access.get_slice_tuple(dimensions, {"C": 0})]
        b = old[access.get_slice_tuple(dimensions, {"C": 1})]
        c = old[access.get_slice_tuple(dimensions, {"C": 2})]
        new = np.moveaxis(np.asarray(conversion(a, b, c)), 0, c_axis)

        if new_system != System.Spherical: return new
        return Units.convert_angle_units(new, dimensions, Units.Radians, new_angle_unit)


class Coordinates(access.Variable):
    """Specialized :class:`sofa.access.Variable` for spatial coordinates"""

    default_values = {
        "Position": (np.asarray([0, 0, 0]), System.Cartesian),
        "View": (np.asarray([1, 0, 0]), System.Cartesian),
        "Up": (np.asarray([0, 0, 1]), System.Cartesian),
    }

    def __init__(self, obj, descriptor):
        access.Variable.__init__(self, obj.database, obj.name + descriptor)
        self._obj_name = obj.name
        self._descriptor = descriptor
        if descriptor == "Up": self._unit_proxy = obj.View
        if descriptor == "CornerB": self._unit_proxy = obj.CornerA

        ldim = self.get_local_dimension()
        if ldim is None:
            self.standard_dimensions = [("I", "C"), ("M", "C")]
        else:
            self.standard_dimensions = [(ldim, "C", "I"), (ldim, "C", "M")]

    def initialize(self, varies, defaults=None):
        super().initialize(self.standard_dimensions[0 if not varies else 1])
        if defaults is not None:
            values, system = defaults
        elif self._descriptor in self.default_values:
            values, system = self.default_values[self._descriptor]
        else:
            values, system = self.default_values["Position"]

        self.set_system(system)
        self.set_values(values, dim_order=("C",),
                        repeat_dim=tuple([d for d in self.standard_dimensions[-1] if d != "C"]))

    @property
    def Type(self):
        """Coordinate system of the values"""
        if not self.exists():
            raise Exception("failed to get Type of {0}, variable not initialized".format(self.name))
        if self._unit_proxy == None: return self._Matrix.Type
        return self._unit_proxy._Matrix.Type

    @Type.setter
    def Type(self, value):
        if not self.exists():
            raise Exception("failed to set Type of {0}, variable not initialized".format(self.name))
        if type(value) == str:
            self._Matrix.Type = value
            return
        self._Matrix.Type = value.value

    def get_global_reference_object(self):
        if self._obj_name == "Receiver": return self.database.Listener
        if self._obj_name == "Emitter": return self.database.Source
        return None

    def get_local_dimension(self):
        if self._obj_name == "Receiver": return "R"
        if self._obj_name == "Emitter": return "E"
        return None

    def get_values(self, indices=None, dim_order=None, system=None, angle_unit=None):
        """Gets the coordinates in their original reference system

        Parameters
        ----------
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Desired order of dimensions in the output array
        system : str, optional
            Target coordinate system
        angle_unit : str, optional
            Unit for spherical angles in the output array

        Returns
        -------
        values : np.ndarray
            Coordinates in the original reference system
        """
        values = access.Variable.get_values(self, indices, dim_order)
        if system is None or system == self.Type:
            if self.Type != System.Spherical or angle_unit == None: return values
            system = self.Type
        old_angle_unit = self.Units.split(",")[0]
        if angle_unit is None: angle_unit = Units.Degree
        if dim_order is None: dim_order = access.get_default_dimension_order(self.dimensions(), indices)
        return System.convert(values, dim_order,
                              self.Type, system,
                              old_angle_unit, angle_unit)

    def get_global_values(self, indices=None, dim_order=None, system=None, angle_unit=None):
        """Transform local coordinates (such as Receiver or Emitter) into the global reference system

        Parameters
        ----------
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Desired order of dimensions in the output array
        system : str, optional
            Target coordinate system
        angle_unit : str, optional
            Unit for spherical angles in the output array

        Returns
        -------
        global_values : np.ndarray
            Transformed coordinates in global reference system
        """
        return self.get_relative_values(None, indices, dim_order, system, angle_unit)

    def get_relative_values(self, ref_object, indices=None, dim_order=None, system=None, angle_unit=None):
        """Transform coordinates (such as Receiver or Emitter) into the reference system of a given :class:`sofa.spatial.SpatialObject`, aligning the x-axis with View and the z-axis with Up

        Parameters
        ----------
        ref_object : :class:`sofa.spatial.Object`
            Spatial object providing the reference system, None for
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Desired order of dimensions in the output array
        system : str, optional
            Target coordinate system
        angle_unit : str, optional
            Unit for spherical angles in the output array

        Returns
        -------
        relative_values : np.ndarray
            Transformed coordinates in original or provided reference system
        """
        if system is None: system = self.Type
        ldim = self.get_local_dimension()

        # get transforms
        anchor_transform, at_order = _get_object_transform(self.get_global_reference_object())
        ref_transform, rt_order = _get_object_transform(ref_object)
        is_position = self._descriptor not in ["View", "Up"]

        # transform values
        if ldim is None:
            original_values = self.get_values(dim_order=at_order, system=System.Cartesian)
            transformed_values = ref_transform(anchor_transform(original_values, is_position, invert=True), is_position)
            order = rt_order
        else:
            original_values_stack = self.get_values(dim_order=(ldim,) + at_order, system=System.Cartesian)
            transformed_values = np.asarray(
                [ref_transform(anchor_transform(original_values, is_position, invert=True), is_position) for original_values in
                 original_values_stack])
            order = (ldim,) + rt_order

        # return in proper system, units and order
        if system == System.Spherical and angle_unit is None:
            angle_unit = self.Units.split(",")[0] if self.Type == System.Spherical else Units.Degree

        default_dimensions = self.dimensions()
        if len(rt_order) > 2: default_dimensions = (rt_order[0],) + default_dimensions

        if dim_order is None: dim_order = access.get_default_dimension_order(default_dimensions, indices)

        if indices is None or "C" not in indices:
            return System.convert(access.get_values_from_array(transformed_values, order,
                                                               indices=indices, dim_order=dim_order),
                                  dim_order,
                                  System.Cartesian, system,
                                  new_angle_unit=angle_unit)
        else:  # only apply "C" index after coordinate system conversion!
            return System.convert(access.get_values_from_array(transformed_values, order,
                                                               indices={i: indices[i] for i in indices if
                                                                        i != "C"},
                                                               dim_order=("C",) + dim_order),
                                  ("C",) + dim_order,
                                  System.Cartesian, system,
                                  new_angle_unit=angle_unit)[indices["C"]]

    def set_system(self, ctype=None, cunits=None):
        """Set the coordinate Type and Units"""
        if ctype is None: ctype = System.Cartesian
        if type(ctype) != str: ctype = ctype.value
        self.Type = str(ctype)
        if cunits is None:
            if ctype == System.Cartesian:
                cunits = Units.Metre
            else:
                cunits = Units.Degree
        self.Units = str(cunits)

    def set_values(self, values, indices=None, dim_order=None, repeat_dim=None, system=None, angle_unit=None):
        """Sets the coordinate values after converting them to the system and units given by the dataset variable

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
        system : str, optional
            Coordinate system of the provided values
        angle_unit : str, optional
            Angle units of the provided values
        """
        if not self.exists():
            raise Exception("failed to set values of {0}, variable not initialized".format(self.name))

        if system is None: system = self.Type
        if angle_unit is None: angle_unit = self.Units

        if indices is not None and "C" in indices:
            iwoc = {i: indices[i] for i in indices if i != "C"}
            new_values, sls = self._reorder_values_for_set(values,
                                                           indices=iwoc,
                                                           dim_order=dim_order,
                                                           repeat_dim=repeat_dim)
            new_order = access.get_default_dimension_order(self.dimensions(), iwoc)
            sls[new_order.index("C")] = indices["C"]
            self._Matrix[sls] = System.convert(new_values,
                                               new_order,
                                               system, self.Type,
                                               angle_unit, self.Units
                                               )[access.get_slice_tuple(new_order, {"C": indices["C"]})]
        else:
            new_values, sls = self._reorder_values_for_set(values, indices, dim_order, repeat_dim)
            new_order = access.get_default_dimension_order(self.dimensions(), indices)
            self._Matrix[sls] = System.convert(new_values, new_order, system, self.Type, angle_unit, self.Units)
