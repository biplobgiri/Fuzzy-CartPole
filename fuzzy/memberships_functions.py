import numpy as np
import matplotlib.pyplot as plt

class MembershipFunctionFactory():
    @staticmethod
    def zmf(x, params):
        a = params[0]
        b = params[1]
        if x <= a:
            output = 1

        elif x <= (a+b)/2 and x > a:
            ratio = (x-a)/(b-a)
            output= 1 -2*ratio*ratio

        elif x > (a+b)/2 and x < b:
            ratio = (x-b)/(b-a)
            output= 2*ratio*ratio

        else:
            output = 0

        return output
    
    @staticmethod
    def smf(x, params):
        a = params[0]
        b = params[1]
        if x <= a:
            output = 0

        elif x <= (a+b)/2 and x > a:
            ratio = (x-a)/(b-a)
            output= 2*ratio*ratio

        elif x > (a+b)/2 and x < b:
            ratio = (x-b)/(b-a)
            output= 1 - 2*ratio*ratio

        else:
            output = 1

        return output
    
# Validate Curves
# if __name__ == "__main__":

#     dt = 0.01
#     stop_theta = 3.14
#     theta = np.arange(-3.14, stop_theta + dt, dt)
#     params = [-0.5, 0.5]
#     zmf = lambda x: MembershipFunctionFactory.zmf(x, params)
#     smf = lambda x :MembershipFunctionFactory.smf(x, params)

#     smf_o = np.zeros(len(theta))
#     zmf_o = np.zeros(len(theta))
#     for i in range (0, len(theta)):
#         zmf_o[i] = zmf(theta[i])
#         smf_o[i] = smf(theta[i])

#     plt.plot(theta, zmf_o, label='zmf', color='blue', linewidth=1)
#     plt.plot(theta, smf_o, label='smf', color='green', linewidth=1)

#     plt.xlabel('Theta')
#     plt.ylabel('Values')
#     plt.title('Plot of zmf and smf vs Theta')
#     plt.legend()
#     plt.grid(True)
#     plt.savefig("Images/zmf_smf_graphs.png")
#     plt.show()


    
    
    
    
    
    
    