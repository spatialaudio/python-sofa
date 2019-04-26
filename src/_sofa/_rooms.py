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
    @util.DatasetVariable()
    def CornerA(self): return "RoomCornerA"
    @util.DatasetVariable()
    def CornerB(self): return "RoomCornerB"
        
    def create(self, a_varies, b_varies):
        self.CornerA = DimensionSet.RoomCorner(a_varies)
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
   
_type_classes = {
    types.FreeField : FreeField,
    types.Reverb : Reverberant,
    types.Shoebox : Shoebox
}
    
def get(dataset):
    for typename in _type_classes.keys():
        if dataset.RoomType == typename: 
            return _type_classes[typename](dataset)
        pass
    #print("Unknown RoomType", file.RoomType)
        return _type_classes[types.Reverb](dataset)

