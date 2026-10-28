class SymbolTable:

    def __init__(self):
        self.classLevelSymbolTable = {}
        self.methodLevelSymbolTable = {}
        self.varCountTable = {
                        'static': 0,
                        'field': 0,
                        'arg': 0,
                        'var': 0
        }

    def reset(self):
        self.methodLevelSymbolTable = {}
        self.varCountTable['arg'] = 0
        self.varCountTable['var'] = 0

    def define(self, name, type, kind):
        if kind in ['static', 'field']:
            self.classLevelSymbolTable[name] = (type, kind,
                                                self.varCount(kind))
        else:
            self.methodLevelSymbolTable[name] = (type, kind,
                                                 self.varCount(kind))
        self.varCountTable[kind] += 1

    def varCount(self, kind):
        return self.varCountTable[kind]

    def kindOf(self, name):
        if name in self.classLevelSymbolTable:
            return self.classLevelSymbolTable[name][1]
        elif name in self.methodLevelSymbolTable:
            return self.methodLevelSymbolTable[name][1]
        else:
            return None

    def typeOf(self, name):
        if name in self.classLevelSymbolTable:
            return self.classLevelSymbolTable[name][0]
        elif name in self.methodLevelSymbolTable:
            return self.methodLevelSymbolTable[name][0]
        else:
            return None

    def indexOf(self, name):
        if name in self.classLevelSymbolTable:
            return self.classLevelSymbolTable[name][2]
        elif name in self.methodLevelSymbolTable:
            return self.methodLevelSymbolTable[name][2]
        else:
            return None
