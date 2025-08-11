from memberships_functions import MembershipFunctionFactory as mfs
import math
import numpy as np
import matplotlib.pyplot as plt

class fuzzy():
    class memFunctions:
        def __init__(self, name=" ", params=None , type=None):
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
            elif self.type == "gbellmf":
                if len(self.params) != 3:
                    print("error")
                output = mfs.gbellmf(x,self.params)
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
    fis = fuzzy("Cartpole-controller", 1, 2, 1 ,2)
    fis.input[0].name = "Theta"
    fis.input[0].range = [-math.pi, math.pi]
    fis.input[0].MembershipFunctions[0].name = "Negtive"
    fis.input[0].MembershipFunctions[0].type = "zmf"
    fis.input[0].MembershipFunctions[0].params = [-0.5, 0.5]
    fis.input[0].MembershipFunctions[1].name = "Negtive"
    fis.input[0].MembershipFunctions[1].type = "smf"
    fis.input[0].MembershipFunctions[1].params = [-0.5, 0.5]
    
    fis.output[0].name = "force"
    fis.output[0].range = [-15, 15]
    fis.output[0].MembershipFunctions[0].name = "NM"
    fis.output[0].MembershipFunctions[0].type = "gbellmf"
    fis.output[0].MembershipFunctions[0].params = [5, 2, -12]
    fis.output[0].MembershipFunctions[1].name = "PM"
    fis.output[0].MembershipFunctions[1].type = "gbellmf"
    fis.output[0].MembershipFunctions[1].params = [5, 2, 12]

    dt = 0.01
    stop_theta = 50
    theta = np.arange(-50, stop_theta + dt, dt)
    

    smf_o = np.zeros(len(theta))
    zmf_o = np.zeros(len(theta))
    gbellmf_o1 = np.zeros(len(theta))
    gbellmf_o2 = np.zeros(len(theta))
    for i in range (0, len(theta)):
        zmf_o[i] = fis.input[0].MembershipFunctions[0].getFuzzyValue(theta[i])
        smf_o[i] = fis.input[0].MembershipFunctions[1].getFuzzyValue(theta[i])
        gbellmf_o1[i] = fis.output[0].MembershipFunctions[0].getFuzzyValue(theta[i])
        gbellmf_o2[i] = fis.output[0].MembershipFunctions[1].getFuzzyValue(theta[i])


    # plt.plot(theta, zmf_o, label='zmf', color='blue', linewidth=1)
    # plt.plot(theta, smf_o, label='smf', color='green', linewidth=1)
    plt.plot(theta, gbellmf_o1, label='gbell', color='green', linewidth=1)
    plt.plot(theta, gbellmf_o2, label='gbell', color='red', linewidth=1)


    plt.xlabel('Theta')
    plt.ylabel('Values')
    plt.title('Plot of zmf and smf vs Theta')
    plt.legend()
    plt.grid(True)
    plt.show()

    