from . import GeneralFIR
from . import GeneralTF
from . import SimpleFreeFieldHRIR

from . import GeneralFIRE
from . import MultiSpeakerBRIR
from . import SimpleFreeFieldTF
from . import SimpleFreeFieldSOS
#from . import SimpleHeadphoneIR
from . import SingleRoomDRIR

List = {
    "GeneralFIR" : GeneralFIR.GeneralFIR,
    "GeneralTF" : GeneralTF.GeneralTF,
    "SimpleFreeFieldHRIR" : SimpleFreeFieldHRIR.SimpleFreeFieldHRIR,

    "GeneralFIRE" : GeneralFIRE.GeneralFIRE,
    "MultiSpeakerBRIR" : MultiSpeakerBRIR.MultiSpeakerBRIR,
    "SimpleFreeFieldTF" : SimpleFreeFieldTF.SimpleFreeFieldTF,
    "SimpleFreeFieldSOS" : SimpleFreeFieldSOS.SimpleFreeFieldSOS,
#    "SimpleHeadphoneIR" : SimpleHeadphoneIR.SimpleHeadphoneIR,
    "SingleRoomDRIR" : SingleRoomDRIR.SingleRoomDRIR
    }

