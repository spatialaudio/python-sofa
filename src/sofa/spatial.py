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

__all__ =["Coordinates", "Set", "Object"]

from .datatypes import dimensions

from . import access
import numpy as np

# for coordinate transformations
from scipy.spatial.transform import Rotation ## requires scipy 1.2.0
from sfs.util import cart2sph
from sfs.util import sph2cart


class Coordinates(access.ArrayVariable):
    """Specialized :class:`sofa.access.ArrayVariable` for spatial coordinates"""
    class System:
        """Enum of valid coordinate systems"""
        Cartesian = "cartesian"
        Spherical = "spherical"

        @staticmethod
        def convert(coords, dimensions, old_system, new_system):
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

            Returns
            -------
            new_coords : np.ndarray
                Array of converted coordinate values in identical dimension order
            """
            if dimensions == None: raise Exception("missing dimension order for coordinate conversion")
            if type(old_system) != str: old_system = old_system.value
            if type(new_system) != str: new_system = new_system.value
            if old_system == new_system: return coords
            conversion = None
            if old_system == Coordinates.System.Cartesian.value and new_system == Coordinates.System.Spherical.value: conversion = cart2sph
            elif old_system == Coordinates.System.Spherical.value and new_system == Coordinates.System.Cartesian.value: conversion = sph2cart
            else: raise Exception("unknown coordinate conversion from {0} to {1}".format(old_system, new_system))

            c_axis = dimensions.index("C")
            sl=()
            for d in dimensions:
                sl = sl+(slice(None),)
    
            a_sl = list(sl)
            a_sl[c_axis] = 0
            a_sl = tuple(a_sl)
            b_sl = list(sl)
            b_sl[c_axis] = 1
            b_sl = tuple(b_sl)
            c_sl = list(sl)
            c_sl[c_axis] = 2
            c_sl = tuple(c_sl)
            return np.moveaxis(np.asarray(conversion(coords[a_sl],coords[b_sl],coords[c_sl])), 0, c_axis)

    class State:
        """Enum of valid coordinate systems"""
        Unused = None
        Fixed = False
        Varying = True

        @staticmethod
        def is_used(state): return state !=Coordinates.State.Unused

    def __init__(self, obj, descriptor):
        self.database = obj.database
        access.Variable.__init__(self, self.database.dataset, obj.name+descriptor)
        self.obj_name = obj.name
        self.descriptor = descriptor

    @property
    def Type(self):
        """Coordinate system of the values"""
        if not self.exists():
            raise Exception("failed to get Type of {0}, variable not initialized".format(self.name))
        return self._Matrix.Type
    @Type.setter
    def Type(self, value): 
        if not self.exists():
            raise Exception("failed to set Type of {0}, variable not initialized".format(self.name))
        if type(value) == str:
            self._Matrix.Type = value
            return
        self._Matrix.Type = value.value

    def get_global_values(self, indices=None, dim_order=None, system=None):
        """Transform local coordinates (such as Receiver or Emitter) into the global reference system
        
        Parameters
        ----------
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Desired order of dimensions in the output array
        system : str, optional
            Target coordinate system

        Returns
        -------
        global_values : np.ndarray
            Transformed coordinates in original or target coordinate system, if provided
        """
        if system==None: system=self.Type
        anchor = None
        ldim = None
        if self.obj_name == "Receiver": 
            anchor = self.database.Listener
            ldim = "R"
        if self.obj_name == "Emitter": 
            anchor = self.database.Source
            ldim = "E"
        if anchor == None: 
            if dim_order == None:
                dimensions = list(self.dimensions())
                if "I" in dimensions and "I" not in indices: dimensions[dimensions.index("I")]="M"
                dim_order = tuple([x for x in dimensions if indices == None or x not in indices or type(indices[x]) != int])
            return Coordinates.System.convert(self.get_values(indices=indices, dim_order=dim_order), dim_order, self.Type, system)
        
        view = np.asarray([[1, 0, 0]])
        up = np.asarray([[0, 0, 1]])
        if anchor.View.exists(): 
            view = anchor.View.get_values()
            if anchor.View.Type == Coordinates.System.Spherical:
                view[:,2] = 1 # enforce normal vector length
                view = Coordinates.System.convert(view, anchor.View.dimensions(), anchor.View.Type, Coordinates.System.Cartesian)
        if anchor.Up.exists(): 
            up = anchor.Up.get_values()
            if anchor.View.Type == Coordinates.System.Spherical:
                up[:,2] = 1 # enforce normal vector length
                up = Coordinates.System.convert(up, anchor.Up.dimensions(), anchor.View.Type, Coordinates.System.Cartesian)

        if len(view)!=len(up):
            view = np.repeat(view, len(up), axis=0)
            up = np.repeat(up, len(view), axis=0)
    
        y_axis = np.cross(up, view)
        dcm = np.moveaxis(np.asarray([view, y_axis, up]),0,-1)
        rotations = Rotation.from_dcm(dcm)

        order = ("M","C")
        count = self.get_values().shape[self.axis(ldim)]
        glob = np.empty((count, self.database.Dimensions.C, self.database.Dimensions.M))
        for c in np.arange(count):
            g_vals = rotations.apply(Coordinates.System.convert(self.get_values(indices={ldim:c}, dim_order=order), order, self.Type, Coordinates.System.Cartesian))
            if self.descriptor == "Position": 
                g_vals = g_vals + Coordinates.System.convert(anchor.Position.get_values(), anchor.Position.dimensions(), anchor.Position.Type, Coordinates.System.Cartesian)
            glob[c,:,:] = g_vals.T

        return access.get_values_from_array(Coordinates.System.convert(glob,self.dimensions(),Coordinates.System.Cartesian, system), self.dimensions(), indices=indices, dim_order=dim_order)

    def get_relative_values(self, ref_obj, indices=None, dim_order=None, system=None):
        """Transform coordinates (such as Receiver or Emitter) into the reference system of a given :class:`sofa.spatial.Object`, aligning the x-axis with View and the z-axis with Up
        
        Parameters
        ----------
        ref_obj : :class:`sofa.spatial.Object`
            Spatial object providing the reference system
        indices : dict(key:str, value:int or slice), optional
            Key: dimension name, value: indices to be returned, complete axis assumed if not provided
        dim_order : tuple of str, optional
            Desired order of dimensions in the output array
        system : str, optional
            Target coordinate system

        Returns
        -------
        relative_values : np.ndarray
            Transformed coordinates in original or target coordinate system, if provided
        """
        if system==None: system=self.Type
        anchor = ref_obj
        ldim = None
        if self.obj_name == "Receiver": 
            ldim = "R"
        if self.obj_name == "Emitter": 
            ldim = "E"
        
        view = np.asarray([[1, 0, 0]])
        up = np.asarray([[0, 0, 1]])
        if anchor.View.exists(): 
            view = anchor.View.get_values()
            if anchor.View.Type == Coordinates.System.Spherical:
                view[:,2] = 1 # enforce normal vector length
                view = Coordinates.System.convert(view, anchor.View.dimensions(), anchor.View.Type, Coordinates.System.Cartesian)
        if anchor.Up.exists(): 
            up = anchor.Up.get_values()
            if anchor.View.Type == Coordinates.System.Spherical:
                up[:,2] = 1 # enforce normal vector length
                up = Coordinates.System.convert(up, anchor.Up.dimensions(), anchor.View.Type, Coordinates.System.Cartesian)    

        if len(view)!=len(up):
            view = np.repeat(view, len(up), axis=0)
            up = np.repeat(up, len(view), axis=0)
    
        y_axis = np.cross(up, view)
        dcm = np.moveaxis(np.asarray([view, y_axis, up]),0,-1)
        rotations = Rotation.from_dcm(dcm)

        # inverse of local to global
        order = ("M","C")        
        loc = None
        if ldim == None:
            loc = np.empty((self.database.Dimensions.M, self.database.Dimensions.C))
            g_vals = self.get_global_values(dim_order=order, system=Coordinates.System.Cartesian)
            if self.descriptor == "Position": 
                g_vals = g_vals - Coordinates.System.convert(anchor.Position.get_values(), anchor.Position.dimensions(), anchor.Position.Type, Coordinates.System.Cartesian)
            l_vals = rotations.apply(g_vals, inverse=True)
            loc[:,:] = l_vals
        else:
            count = self.get_values().shape[self.axis(ldim)]
            loc = np.empty((count, self.database.Dimensions.C, self.database.Dimensions.M))
            for c in np.arange(count):
                g_vals = self.get_global_values(indices={ldim:c}, dim_order=order, system=Coordinates.System.Cartesian)
                if self.descriptor == "Position": 
                    g_vals = g_vals - Coordinates.System.convert(anchor.Position.get_values(), anchor.Position.dimensions(), anchor.Position.Type, Coordinates.System.Cartesian)
                l_vals = rotations.apply(g_vals, inverse=True)
                loc[c,:,:] = l_vals.T

        return access.get_values_from_array(Coordinates.System.convert(loc,self.dimensions(),Coordinates.System.Cartesian, system), self.dimensions(), indices=indices, dim_order=dim_order)


    def set_system(self, ctype=None, cunits=None):
        """Set the coordinate Type and Units"""
        if ctype == None: ctype = Coordinates.System.Cartesian
        if type(ctype) != str: ctype = ctype.value
        self.Type = str(ctype)
        if cunits == None: cunits=dimensions.default_units[ctype]
        self.Units = str(cunits)      

class Set:
    """Descriptors or data for a spatial entity (Listener, Source, Receiver, Emitter)"""

    def __init__(self, Position, View=Coordinates.State.Unused, Up=Coordinates.State.Unused):
        """Parameters
        ----------
        Position : :class:`sofa.spatial.Coordinates.State`
        View : :class:`sofa.spatial.Coordinates.State`, optional
        Up : :class:`sofa.spatial.Coordinates.State`, optional
        """
        self.Position=Position
        self.View=View
        self.Up=Up

#    @property
#    def Position(self): return self._Position
#    @Position.setter
#    def Position(self, value): self._Position = value
#    @property
#    def View(self): return self._View
#    @View.setter
#    def View(self, value): self._View = value
#    @property
#    def Up(self): return self._Up
#    @Up.setter
#    def Up(self, value): self._Up = value

class Object:
    """Spatial object such as Listener, Receiver, Source, Emitter"""
    def __init__(self, database, name):
        self.database = database
        self.dataset = database.dataset
        self.name = name
        return

    @property
    def Description(self):
        """Informal description of the spatial object"""
        return self.database.Metadata.get_attribute(self.name+"Description")
    @Description.setter
    def Description(self, value): self.database.Metadata.set_attribute(self.name+"Description", value)
    
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

    def initialize(self, info_states, count=None):
        """Create the necessary variables and attributes

        Parameters
        ----------
        info_states : :class:`sofa.spatial.Set`
            Usage states for the object coordinates
        count : int, optional
            Number of objects (such as Emitters or Receivers)
        """
        if count == None: 
            if "count" in self.database._convention.default_objects[self.name].keys(): 
                count = self.database._convention.default_objects[self.name]["count"]
            else: raise Exception(self.name, "count missing!")
        print(self.name, "count = ", str(count))
        self.database._convention.validate_spatial_object_settings(self.name, info_states, count)

        if self.name == "Emitter" or self.name == "Receiver":
            if dimensions.Definitions.names[self.name] not in self.dataset.dimensions.keys():
                self.dataset.createDimension(dimensions.Definitions.names[self.name], count)
        self._create_coordinates(info_states)
        self.database._convention.set_default_spatial_values(self)

    def _create_coordinates(self, info_states):
        rd = tuple(x for x in getattr(dimensions.Definitions, self.name)(Coordinates.State.Varying) if x!="C")
        if info_states.Position != Coordinates.State.Unused: 
            self.Position.initialize(getattr(dimensions.Definitions, self.name)(info_states.Position))
        if info_states.View != Coordinates.State.Unused: 
            self.View.initialize(getattr(dimensions.Definitions, self.name)(info_states.View))
        if info_states.Up != Coordinates.State.Unused: 
            self.Up.initialize(getattr(dimensions.Definitions, self.name)(info_states.Up))
