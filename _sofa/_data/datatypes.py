from enum import Enum

from . import FIR
from . import TF
from . import FIRE
from . import SOS

class Types(Enum):
    FIR = "FIR"
    TF = "TF"
    FIRE = "FIRE" 
    SOS = "SOS"
    
List = {
    "FIR" : FIR.FIR,
    "TF" : TF.TF,
    "FIRE" : FIRE.FIRE,
    "SOS" : SOS.SOS
}
    
def get(dataset):
    if dataset.DataType in List.keys(): return List[dataset.DataType](dataset)
    print("Unknown DataType", file.DataType, ", returning FIR instead")
    return List["FIR"](dataset)
