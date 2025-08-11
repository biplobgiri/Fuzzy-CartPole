from memberships_functions import MembershipFunctionFactory as mfs
import math
import numpy as np
import matplotlib.pyplot as plt

class fuzzy():
    class memFunctions:
        def __init__(self, name=" ", params=None , type="zmf",):
            self.name = name
            if params is None:
                params=[0.0,0.0]
            self.params = params
            self.type = type

        def getFuzzyValue(self,x):
            output : float = 0.0
            if self.type == "zmf":
                output = mfs.zmf(x,self.params)
            elif self.type == "smf":
                output = mfs.smf(x,self.params)
            return output

    class Input:
        def __init__(self,Name="input", Range=[-1,1], NumMFs=1):
            self.name = Name
            self.range = Range
            self.nummfs = NumMFs
            self.MembershipFunctions = [fuzzy.memFunctions() for _ in range(self.nummfs) ]

            
        def add_mem_function(self, name, type, params):
            self.MembershipFunctions.append(fuzzy.memFunctions(name, type , params))
            self.nummfs += 1

    
    class Output:
        def __init__(self, Name="output", Range=[-1,1], NumMFS=1):
            self.name = Name
            self.range = Range
            self.nummfs = NumMFS
            self.MembershipFunctions = [fuzzy.memFunctions() for _ in range(self.nummfs) ]

            
        def add_mem_function(self, name, type, params):
            self.MembershipFunctions.append(fuzzy.memFunctions(name, type , params))
            self.nummfs += 1
    

    def __init__(self,Name = "",NumInputs=1, NumInputMFs=1,NumOutputs=1,NumOutputMfs=1,rule="AddRule"):
        self.name = Name
        self.input = [self.Input(NumMFs=NumInputMFs) for _ in range(NumInputs)]
        self.output = [self.Output(NumMFS=NumOutputMfs) for _ in range(NumOutputs)]




if __name__ == "__main__":
    fis = fuzzy("Cartpole-controller", 1, 2, 2 ,2)
    fis.input[0].name = "Theta"
    fis.input[0].range = [-math.pi, math.pi]
    fis.input[0].MembershipFunctions[0].name = "Negtive"
    fis.input[0].MembershipFunctions[0].type = "zmf"
    fis.input[0].MembershipFunctions[0].params = [-0.5, 0.5]
    fis.input[0].MembershipFunctions[1].name = "Negtive"
    fis.input[0].MembershipFunctions[1].type = "smf"
    fis.input[0].MembershipFunctions[1].params = [-0.5, 0.5]
    print(fis.name)

    dt = 0.01
    stop_theta = 3.14
    theta = np.arange(-3.14, stop_theta + dt, dt)
    params = [-0.5, 0.5]
    

    smf_o = np.zeros(len(theta))
    zmf_o = np.zeros(len(theta))
    for i in range (0, len(theta)):
        zmf_o[i] = fis.input[0].MembershipFunctions[0].getFuzzyValue(theta[i])
        smf_o[i] = fis.input[0].MembershipFunctions[1].getFuzzyValue(theta[i])


    plt.plot(theta, zmf_o, label='zmf', color='blue', linewidth=1)
    plt.plot(theta, smf_o, label='smf', color='green', linewidth=1)

    plt.xlabel('Theta')
    plt.ylabel('Values')
    plt.title('Plot of zmf and smf vs Theta')
    plt.legend()
    plt.grid(True)
    plt.show()

    