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

"""Classes for accessing RoomType-specific data.
"""
__version__ = "0.1.0"
__all__ = ["implemented", "FreeField", "Reverberant", "Shoebox"]

from . import spatial
from .datatypes import dimensions

def implemented():
    """Returns
    -------
    list
        Names of implemented SOFA room types
    """
    return list(List.keys())

class _Base:
    def __init__(self, database):
        self.database = database
        self.name="Room"
            
    @property
    def Type(self): 
        """SOFA room type"""
        return self.database.dataset.RoomType
    @Type.setter
    def Type(self, value):
        if type(value) == str: 
            self.database.dataset.RoomType = value 
            return
        self.database.dataset.RoomType = value.value
    
class FreeField(_Base):
    def initialize(self):
        """Create the necessary variables and attributes"""
        return
    pass
        
    
class Reverberant(_Base):    
    @property
    def Description(self): 
        """Informal description of the room"""
        return self.database.dataset.RoomDescription
    @Description.setter
    def Description(self, value): self.database.dataset.RoomDescription = value 
    
    def initialize(self):
        """Create the necessary variables and attributes"""
        self.Description = ""
        return
    
class Shoebox(_Base):
    @property
    def Description(self):
        """Informal description of the room"""
        return self.database.dataset.RoomDescription
    @Description.setter
    def Description(self, value): self.database.dataset.RoomDescription = value 

    @property
    def CornerA(self): 
        """:class:`sofa.spatial.Coordinates` for the first corner of the shoebox"""
        return spatial.Coordinates(self, "CornerA")
    @property
    def CornerB(self):
        """:class:`sofa.spatial.Coordinates` for the opposing corner of the shoebox"""
        return spatial.Coordinates(self, "CornerB")
        
    def initialize(self, corner_a=spatial.Coordinates.State.Fixed, corner_b=spatial.Coordinates.State.Fixed):
        """Create the necessary variables and attributes
        
        Parameters
        ----------
        corner_a : :class:`sofa.spatial.Coordinates.State`
        corner_b : :class:`sofa.spatial.Coordinates.State`
        """
        self.Description = ""
        self.CornerA.initialize(dimensions.Definitions.RoomCorner(corner_a==spatial.Coordinates.State.Varying))
        self.CornerA.set_system(ctype="cartesian", cunits="meter")
            
        self.CornerB.initialize(dimensions.Definitions.RoomCorner(corner_b==spatial.Coordinates.State.Varying))
        return
        
List = {
    "free field" : FreeField,
    "reverberant" : Reverberant,
    "shoebox" : Shoebox
}
    
def get(database):
    for typename in List.keys():
        if database.dataset.RoomType == typename: 
            return List[typename](database)
        pass
    print("Unknown RoomType", database.dataset.RoomType)
    return List[types.Reverb.value](database)


