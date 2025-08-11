# from memberships_functions import 

class fuzzy():
    class Inputs:
        def __init__(self,Name="input", Range=[-1,1], NumMFs=1):
            self.name = Name
            self.range = Range
            self.nummfs = NumMFs
            
        def add_mem_function(self):
            pass
    
    class Outputs:
        def __init__(self, Name="output", Range=[-1,1], NumMFS=1):
            self.name = Name
            self.range = Range
            self.nummfs = NumMFS
        
        def add_mem_function(self):
            pass
    
    class memFunctions:
        pass
    
    def __init__(self,NumInputs=1, NumInputMFs=1,NumOutputs=1,NumOutputMfs=1,rule="AddRule"):
        self.inputs = [self.Inputs(NumMFs=NumInputMFs) for _ in range(NumInputs)]
        self.outputs = [self.Outputs(NumMFS=NumOutputMfs) for _ in range(NumOutputs)]

    

    