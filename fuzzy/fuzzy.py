from .memberships_functions import MembershipFunctionFactory as mfs
import re
import os
import math
import numpy as np
import matplotlib.pyplot as plt


class fuzzy():
    class ruleHandler:
        def __init__(self):
            self.rules: list = []
            self.parsed_rules : dict = {}
            self.numberOfRules : int = 0
            self.antecedentsLVs : dict ={}
            self.consequentLVs : dict ={}
            self.fuzzy_operators = ["and", "or", "not"]
      
        def add_rules(self, rule_string:list, antecedentLVs, consequentLVs):
            self.antecedentsLVs = antecedentLVs
            self.consequentLVs = consequentLVs

            for r in rule_string:
                self.rules.append(r)
            self.numberOfRules = len(self.rules)
            self.parse_rule()
            
        def parse_rule(self):
            antecedents_dict : dict = {}
            consequents_dict : dict = {}
            for i,r in enumerate(self.rules):
                splited = r.split("Then")
                antecedents = splited[0].split("If")[-1]
                consequents = splited[1]     

                keywords_a = [kw.lower().replace("is not", "not") 
                    for kw in re.findall(r"\b(?:is not|is|and|or)\b", antecedents, flags=re.IGNORECASE)]
                antecedents_dict = dict(re.findall(r"(\w+)\s+is(?:\s+not)?\s+(\w+)", antecedents, flags=re.IGNORECASE))

                keywords_c = [kw.lower().replace("is not", "not") 
                    for kw in re.findall(r"\b(?:is not|is|and|or)\b", consequents, flags=re.IGNORECASE)]
                consequents_dict = dict(re.findall(r"(\w+)\s+is\s+(\w+)", consequents))

                self.parsed_rules[f"rule_{i}"] = {
                    "antecedents_operations": keywords_a,
                    "antecedents": antecedents_dict,
                    "consequents_operations": keywords_c,
                    "consequents": consequents_dict
                }
        def fuzzy_or(self, x, y):
            return max(x,y)
        
        def fuzzy_and(self, x, y):
            return x*y
        
        def fuzzy_not(self, x):
            return (1.0-x)

        def rule_inference(self, memFunc_values):
            input_names = list(self.antecedentsLVs.keys())
            rules_sequence = list(self.parsed_rules.keys())
            ouptut_list : list = []
            
            # print("----Inference outputs-----")
            # print("  Input names:", input_names)
            # print("  Len:",len(rules_sequence))

            for i in range(len(rules_sequence)):
                operations_a = self.parsed_rules[rules_sequence[i]]["antecedents_operations"]
                antecedents = self.parsed_rules[rules_sequence[i]]["antecedents"]
                antecedent_keys = list(antecedents.keys())

                # print(f"Rule_{i}")
                # print(" operations:", operations_a)
                # print(" Antecedent dict:", antecedents)
                # print(" Antecedent keys", antecedent_keys)

                input_mfvalue_list : list = []

                for j, key in enumerate(antecedent_keys): 
                    value = antecedents[key]
                    input_name_index = input_names.index(key)
                    input_mfValues = memFunc_values[input_name_index]
                    
                    input_mf_index = self.antecedentsLVs[key].index(value)
                    input_mfvalue = input_mfValues[input_mf_index]
                    if operations_a[j*2].lower() == "not":
                        input_mfvalue = self.fuzzy_not(input_mfvalue)

                    input_mfvalue_list.append(input_mfvalue)   

                    # print("   ", key, ":", value)
                    # print("   Input MF values:",input_mfValues)
                    # print("   Input Mf value", input_mfvalue)

                # print("  Input Mf values list:",input_mfvalue_list)   
                out = input_mfvalue_list[0]
                if len(input_mfvalue_list) > 1:

                    for o in operations_a:
                        
                        if o.lower() == "is" or o.lower() == "not":
                            continue
                        if o.lower() == "and":
                            for i in range(1,len(input_mfvalue_list)):
                                out = self.fuzzy_and(out,input_mfvalue_list[i])
                        
                        elif o.lower() == "or":
                            for i in range(1,len(input_mfvalue_list)):
                                out = self.fuzzy_or(out,input_mfvalue_list[i])

                ouptut_list.append(out) 
                # print("   Out",out)

            # print(f"Inferene output: {ouptut_list}")

            
            return ouptut_list


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
        def __init__(self, Name="output", Range=[-1,1], NumMFs=1):
            self.name = Name
            self.range = Range
            self.nummfs = NumMFs
            self.MembershipFunctions = [fuzzy.memFunctions() for _ in range(self.nummfs) ]

            
        def add_mem_function(self, name, type, params):
            self.MembershipFunctions.append(fuzzy.memFunctions(name, type , params))
            self.nummfs += 1
    

    def __init__(self,Name = "",NumInputs=1, NumInputMFs=1,NumOutputs=1,NumOutputMFs=1,rule="AddRule"):
        self.name = Name

        self.numIn = NumInputs    
        self.numInMFS = NumInputMFs
        self.numOut = NumOutputs    
        self.numOutMFS = NumOutputMFs
        

        self.input = [self.Input(NumMFs=NumInputMFs) for _ in range(NumInputs)]
        self.output = [self.Output(NumMFs=NumOutputMFs) for _ in range(NumOutputs)]

        self.antecedentLnguisticVariables : dict = {}
        self.consequentLnguisticVariables : dict = {}

        self.ruleHndl = self.ruleHandler()

    
    def update_linguistic_variable(self):
        for i in self.input:
            key = i.name
            value = []
            for j in range(i.nummfs):
                value.append(i.MembershipFunctions[j].name)
            self.antecedentLnguisticVariables[key] = value

        for i in self.output:
            key = i.name
            value = []
            for j in range(i.nummfs):
                value.append(i.MembershipFunctions[j].name)
            self.consequentLnguisticVariables[key] = value
    
    def add_rule(self, rule):
        self.update_linguistic_variable()
        self.ruleHndl.add_rules(rule, self.antecedentLnguisticVariables, self.consequentLnguisticVariables)

    def defuzzify(self, mem_fun_params,range,out_idx):

        df=0.01
        output_range = np.arange(range[0], range[1]+df , df)

        output_seq=np.zeros(len(output_range))
        temp_output_seq=np.zeros(len(output_range))

        for idx,memfun in enumerate(self.output[out_idx].MembershipFunctions):
            if(memfun.type=="zmf"):
                temp_output_seq=[mem_fun_params[idx] if (mfs.zmf(x,memfun.params)>mem_fun_params[idx]) else mfs.zmf(x,memfun.params) for x in output_range]

            if(memfun.type=="smf"):
                temp_output_seq=[mem_fun_params[idx] if (mfs.smf(x,memfun.params)>mem_fun_params[idx]) else mfs.smf(x,memfun.params) for x in output_range]

            if(memfun.type=="gbellmf"):
                temp_output_seq=[mem_fun_params[idx] if (mfs.gbellmf(x, memfun.params)>mem_fun_params[idx]) else mfs.gbellmf(x, memfun.params) for x in output_range]


            output_seq=np.maximum(output_seq,temp_output_seq)

        numerator=np.sum(output_seq*output_range)
        denominator=np.sum(output_seq)

        if (denominator==0.0):
            return 0.0
        
        output_crisp= numerator/denominator   
        return output_crisp     
    

    def compute(self, inputs:list):
        if len(inputs) != self.numIn:
            print(len(inputs), self.numIn)
            raise IndexError(f"Number of Inputs:{len(inputs)} not equal to numIn variable:{self.numIn} ")

        memFunc_values = []
        # print("\n\n---------Fuzzy- Inference------------------")
        # print("Input values: ", inputs)
        
        for idx, i in enumerate(inputs):
            memFunc_values.append([self.input[idx].MembershipFunctions[j].getFuzzyValue(i) for j in range(self.input[idx].nummfs)])
            # print(f"{self.input[idx].name}:")
            # for c, j in enumerate(memFunc_values[idx]):
            #     print(f"   {self.input[idx].MembershipFunctions[c].name}:{i}:" ,j)
        
        o = self.ruleHndl.rule_inference(memFunc_values)
        defuz=[]
        for i in range(0,self.numOut):
            defuz.append(self.defuzzify(o,self.output[i].range,i))
        
        # print(f"defuz val{defuz}")
        return defuz
    
    def visualize_memFunc(self, dir_path=None):
        if dir_path is None:
            raise ValueError("Output directory path not provided")

        os.makedirs(dir_path, exist_ok=True)
        dt = 0.01

        # ------------------ Inputs ------------------
        n_inputs = len(self.input)
        fig, axs = plt.subplots(n_inputs, 1, figsize=(8, 4 * n_inputs), squeeze=False)

        for idx, i in enumerate(self.input):
            ax = axs[idx, 0]
            for j in range(i.nummfs):
                inputs = np.arange(i.range[0], i.range[1] + dt, dt)
                outputs = np.array([i.MembershipFunctions[j].getFuzzyValue(x) for x in inputs])
                ax.plot(inputs, outputs, label=f'{i.MembershipFunctions[j].name}', linewidth=1)
            ax.set_xlabel('x')
            ax.set_ylabel('Membership degree')
            ax.set_title(f'{i.name} Membership Functions')
            ax.legend()
            ax.grid(True)

        plt.tight_layout()
        plt.savefig(f"{dir_path}/Inputs_MF.png", dpi=600)
        plt.close()

        # ------------------ Outputs ------------------
        n_outputs = len(self.output)
        fig, axs = plt.subplots(n_outputs, 1, figsize=(8, 4 * n_outputs), squeeze=False)

        for idx, i in enumerate(self.output):
            ax = axs[idx, 0]
            for j in range(i.nummfs):
                inputs = np.arange(i.range[0], i.range[1] + dt, dt)
                outputs = np.array([i.MembershipFunctions[j].getFuzzyValue(x) for x in inputs])
                ax.plot(inputs, outputs, label=f'{i.MembershipFunctions[j].name}', linewidth=1)
            ax.set_xlabel('x')
            ax.set_ylabel('Membership degree')
            ax.set_title(f'{i.name} Membership Functions')
            ax.legend()
            ax.grid(True)

        plt.tight_layout()
        plt.savefig(f"{dir_path}/Outputs_MF.png", dpi=600)
        plt.close()



def test():
    parsed_rules : dict = {}
    antecedents_dict : dict = {}
    consequents_dict : dict = {}
    rules =["If Angle is Negative Then Force is PM",
            "If Angle is Positive Then Force is NM",]
    for i,r in enumerate(rules):
                splited = r.split("Then")
                antecedents = splited[0].split("If")[-1]
                consequents = splited[1]     

                keywords_a = re.findall(r"\b(?:is|and|or|not)\b", antecedents, flags=re.IGNORECASE)
                antecedents_dict = dict(re.findall(r"(\w+)\s+is\s+(\w+)", antecedents))

                keywords_c = re.findall(r"\b(?:is|and|or|not)\b", consequents, flags=re.IGNORECASE)
                consequents_dict = dict(re.findall(r"(\w+)\s+is\s+(\w+)", consequents))

                parsed_rules[f"rule_{i}"] = {
                    "antecedents_operations": keywords_a,
                    "antecedents": antecedents_dict,
                    "consequents_operations": keywords_c,
                    "consequents": consequents_dict
                }
                # print(keywords_a)
                # print(keywords_c)
    print(parsed_rules)

                
if __name__ == "__main__":
    # test()
    fis = fuzzy("Cartpole-controller", 2, 2, 1 ,2)
    fis.input[0].name = "Theta"
    fis.input[0].range = [-math.pi, math.pi]
    fis.input[0].MembershipFunctions[0].name = "Negative"
    fis.input[0].MembershipFunctions[0].type = "zmf"
    fis.input[0].MembershipFunctions[0].params = [-0.5, 0.5]
    fis.input[0].MembershipFunctions[1].name = "Positives"
    fis.input[0].MembershipFunctions[1].type = "smf"
    fis.input[0].MembershipFunctions[1].params = [-0.5, 0.5]

    fis.input[1].name = "Theta_dot"
    fis.input[1].range = [-5, 5]
    fis.input[1].MembershipFunctions[0].name = "Negative"
    fis.input[1].MembershipFunctions[0].type = "zmf"
    fis.input[1].MembershipFunctions[0].params = [-0.5, 0.5]
    fis.input[1].MembershipFunctions[1].name = "Positives"
    fis.input[1].MembershipFunctions[1].type = "smf"
    fis.input[1].MembershipFunctions[1].params = [-0.5, 0.5]
    
    fis.output[0].name = "force"
    fis.output[0].range = [-15, 15]
    fis.output[0].MembershipFunctions[0].name = "NM"
    fis.output[0].MembershipFunctions[0].type = "gbellmf"
    fis.output[0].MembershipFunctions[0].params = [5, 2, -12]
    fis.output[0].MembershipFunctions[1].name = "PM"
    fis.output[0].MembershipFunctions[1].type = "gbellmf"
    fis.output[0].MembershipFunctions[1].params = [5, 2, 12]

    rules =["If Angle is Negative Then Force is PM",
            "If Angle is Positive Then Force is NM"]
    
    fis.add_rule(rules)
    
    
   

    