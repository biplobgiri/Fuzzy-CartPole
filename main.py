import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from fuzzy.fuzzy import fuzzy

import math
from cartpole import cartople
from rk4 import rk4
from visualize import CartPoleVisualizer


def plot_graph(time, force, cart_positions, pole_angles,filename, show_img=False):
    fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

    # Plot Force
    axs[0].plot(time, force, color='tab:blue')
    axs[0].set_ylabel('Force (N)')
    axs[0].set_title('Force vs Time')
    axs[0].grid(True)
    axs[0].xaxis.set_major_locator(MaxNLocator(nbins=10))  # limit number of ticks
    axs[0].yaxis.set_major_locator(MaxNLocator(nbins=10))

    # Plot Cart Position
    axs[1].plot(time, cart_positions, color='tab:orange')
    axs[1].set_ylabel('Position (m)')
    axs[1].set_title('Cart Position vs Time')
    axs[1].grid(True)
    axs[1].xaxis.set_major_locator(MaxNLocator(nbins=10))
    axs[1].yaxis.set_major_locator(MaxNLocator(nbins=10))

    # Plot Pole Angle
    axs[2].plot(time, pole_angles, color='tab:green')
    axs[2].set_ylabel('Angle (radian)')
    axs[2].set_xlabel('Time (s)')
    axs[2].set_title('Pole Angle vs Time')
    axs[2].grid(True)
    axs[2].xaxis.set_major_locator(MaxNLocator(nbins=10))
    axs[2].yaxis.set_major_locator(MaxNLocator(nbins=10))

    plt.tight_layout()
    plt.savefig(f"Images/{filename}", dpi=600)
    if show_img:
        plt.show()


if __name__ == "__main__":
    '''Fuzzy Inference system'''
    fis = fuzzy("Cartpole-controller", 1, 2, 1 ,2)
    fis.input[0].name = "Theta"
    fis.input[0].range = [-math.pi, math.pi]
    fis.input[0].MembershipFunctions[0].name = "Negative"
    fis.input[0].MembershipFunctions[0].type = "zmf"
    fis.input[0].MembershipFunctions[0].params = [-0.5, 0.5]
    fis.input[0].MembershipFunctions[1].name = "Positive"
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

    rules =["If Theta is Negative Then Force is PM",
            "If Theta is Positive Then Force is NM"]
    
    fis.add_rule(rules)
    inputs = [-1.0,-0.25, 0.0, 0.25, 1.0]
    for i in inputs:
        fis.compute([i])


    # '''Simulation time'''
    # dt = 0.001
    # stop_time = 10
    # time = np.arange(0, stop_time + dt, dt)

    # print("Physical characteristics")
    # cart_mass = 1
    # pole_mass = 1
    # pole_length = 2

    # ''' states : x_dot, x, w_dot, w'''
    # states = np.empty((4, len(time)))
    # states[:,0] = [ 0.0,0.0,0.0,0.0]        # Intial State
    # # states[:,1] = [ 1.0,0.0,0.0,0.0]        # Intial State

    # cartople_ = cartople(cart_mass, pole_mass, pole_length)

    # force = np.zeros(len(time))
    # i = 0
    # t = 0
    # while True:
    #     force[i] = 0.0
    #     t = t+ dt
    #     i = i + 1
    #     if t >= 1:
    #         break

    # force[0] = 1.0
        
    # for t in range(0,len(time)-1):
    #     fn = lambda y : cartople_(y,force[t], 9.8)
    #     states[:,t+1] = rk4(fn, states[:,t].astype(float), dt )
    #     angle = (states[3, t] + math.pi) % (2 * math.pi) - math.pi
    #     states[3, t] = angle
    #     break
       
    # angle = (states[3, t+1] + math.pi) % (2 * math.pi) - math.pi
    # states[3, t+1] = angle

    # cart_positions = states[1,:]
    # pole_angles = states[3,:]
   
    # print("Pole Angle:", pole_angles)
    # plot_graph(time, force, cart_positions, pole_angles, filename="cartpole_free.png")

     
    # visualizer = CartPoleVisualizer()
    # visualizer.visualize(cart_positions, pole_angles, dt = 0.001)
    

    