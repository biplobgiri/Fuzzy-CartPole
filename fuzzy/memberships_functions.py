import numpy as np
import matplotlib.pyplot as plt
import math

class MembershipFunctionFactory():
    @staticmethod
    def zmf(x, params):
        '''
        params[0] = below this output is 1
        params[1] = above this output is 0
        '''
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
        '''
        params[0] = below this output is 0
        params[1] = above this output is 1
        '''
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

    @staticmethod
    def gbellmf(x, params):
        '''
        params[0] = width of the bell
        params[1] = slope of the curve
        params[2] = centre of the bell
        
        '''
        a = params[0]
        b = params[1]
        c = params[2]

        ratio = (x - c)/a
        den = 1 + math.pow(ratio, 2*b)
        output = 1 / den

        return output
    
# Validate Curves
# if __name__ == "__main__":

#     dt = 0.01
#     stop_theta = 3.14
#     theta = np.arange(-3.14, stop_theta + dt, dt)
#     params = [-0.5, 0.5]
#     zmf = lambda x: MembershipFunctionFactory.zmf(x, params)
#     smf = lambda x :MembershipFunctionFactory.smf(x, params)
#     params_ = [1,4,0]

#     gbellmf = lambda x :MembershipFunctionFactory.gbellmf(x, params_)

#     smf_o = np.zeros(len(theta))
#     zmf_o = np.zeros(len(theta))
#     gbellmf_o = np.zeros(len(theta))
#     for i in range (0, len(theta)):
#         zmf_o[i] = zmf(theta[i])
#         smf_o[i] = smf(theta[i])
#         gbellmf_o[i] = gbellmf(theta[i])

#     plt.plot(theta, zmf_o, label='zmf', color='blue', linewidth=1)
#     plt.plot(theta, smf_o, label='smf', color='green', linewidth=1)
#     plt.plot(theta, gbellmf_o, label='smf', color='orange', linewidth=1)

#     plt.xlabel('Theta')
#     plt.ylabel('Values')
#     plt.title('Plot of zmf and smf vs Theta')
#     plt.legend()
#     plt.grid(True)
#     # plt.savefig("Images/graphs.png")
#     plt.show()


    
    
    
    
    
    
    