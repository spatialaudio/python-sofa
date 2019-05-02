__all__ = ["implemented", "FreeField", "Reverberant", "Shoebox"]

from . import util
from enum import Enum

### SOFA room types
class _Base:
    def __init__(self, dataset):
        self.dataset = dataset
            
    @property
    def Type(self): return self.dataset.RoomType
    @Type.setter
    def Type(self, value): self.dataset.RoomType = value
    
class FreeField(_Base):
    def create(self):
        return
    pass
        
    
class Reverberant(_Base):
    @util.DatasetAttribute()
    def Description(self): return "RoomDescription"
    
    def create(self):
        self.dataset.RoomDescription = ""
        return
    
class Shoebox(_Base):
    @property
    def CornerA(self): return Coordinates(self.dataset, "RoomCorner", "A")
    @property
    def CornerB(self): return Coordinates(self.dataset, "RoomCorner", "B")
        
    def create(self, a_varies, b_varies):
        self.CornerA.Values = DimensionSet.RoomCorner(a_varies)
        self.CornerA.Type = "cartesian"
        self.CornerA.Units = "meter"
        self.CornerA.Description = ""
            
        self.CornerB = DimensionSet.RoomCorner(b_varies)
        return
        
class types(Enum):
        FreeField = "free field"
        Reverb = "reverberant"
        Shoebox = "shoebox"
        pass

List = {
    types.FreeField.value : FreeField,
    types.Reverb.value : Reverberant,
    types.Shoebox.value : Shoebox
}
    
def get(dataset):
    for typename in List.keys():
        if dataset.RoomType == typename: 
            return List[typename](dataset)
        pass
    #print("Unknown RoomType", file.RoomType)
        return List[types.Reverb.value](dataset)

def implemented():
    """Returns
    -------
    list
        Names of implemented SOFA room types
    """
    return list(List.keys())
