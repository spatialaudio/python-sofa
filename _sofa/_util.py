### convenience access to dataset attributes and variables
# convenience attribute checking
def hasattr(source, attrname):
    for attr in source.ncattrs():
        if attr == attrname:
            return True
        pass
    return False

# convenience variable checking
def hasvar(source, varname):
    for var in source.variables:
        if var == varname:
            return True
        pass
    return False

class DatasetVariable:
    def __init__(self, data_attr="dataset"):
        self._data_attr = data_attr
        return
    
    def __call__(self, tag):        
        @property
        def wrapped_variable(parent):
            dataset = getattr(parent, self._data_attr)
            if hasvar(dataset, tag(parent)): return dataset[tag(parent)]
            return None
        @wrapped_variable.setter
        def wrapped_variable(parent, dimensions):
            dataset = getattr(parent, self._data_attr)
            if hasvar(dataset, tag(parent)): 
                print("dataset variables cannot be assigned directly")
                return
            dataset.createVariable(tag(parent), "d", dimensions)
            return
            
        return wrapped_variable

class DatasetAttribute:
    def __init__(self, data_attr="dataset"):
        self._data_attr = data_attr
        return
    
    def __call__(self, tag):        
        @property
        def wrapped_attribute(parent):
            dataset = getattr(parent, self._data_attr)
            if hasattr(dataset, tag(parent)): return dataset.getncattr(tag(parent))
            print("attribute",tag(parent),"does not exist")
            return None
        @wrapped_attribute.setter
        def wrapped_attribute(parent, value):
            dataset = getattr(parent, self._data_attr)
            if hasattr(dataset, tag(parent)) == False: 
                print("dataset attribute not initialized")
                return
            dataset.setncattr(tag(parent), value)
            return
            
        return wrapped_attribute


