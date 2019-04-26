from .. import _util as util

class _Base:
    def __init__(self, dataset):
        self.dataset = dataset
        
    @util.DatasetAttribute()
    def Type(self): return "DataType"
    
