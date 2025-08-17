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

    # fis.input[1].name = "Theta_dot"
    # fis.input[1].range = [-5, 5]
    # fis.input[1].MembershipFunctions[0].name = "Negative"
    # fis.input[1].MembershipFunctions[0].type = "zmf"
    # fis.input[1].MembershipFunctions[0].params = [-0.5, 0.5]
    # fis.input[1].MembershipFunctions[1].name = "Positive"
    # fis.input[1].MembershipFunctions[1].type = "smf"
    # fis.input[1].MembershipFunctions[1].params = [-0.5, 0.5]
    
    fis.output[0].name = "force"
    fis.output[0].range = [-15, 15]
    fis.output[0].MembershipFunctions[0].name = "NM"
    fis.output[0].MembershipFunctions[0].type = "gbellmf"
    fis.output[0].MembershipFunctions[0].params = [5, 2, -12]
    fis.output[0].MembershipFunctions[1].name = "PM"
    fis.output[0].MembershipFunctions[1].type = "gbellmf"
    fis.output[0].MembershipFunctions[1].params = [5, 2, 12]

    # fis.output[1].name = "Torque"
    # fis.output[1].range = [-15, 15]
    # fis.output[1].MembershipFunctions[0].name = "NM"
    # fis.output[1].MembershipFunctions[0].type = "gbellmf"
    # fis.output[1].MembershipFunctions[0].params = [5, 2, -12]
    # fis.output[1].MembershipFunctions[1].name = "PM"
    # fis.output[1].MembershipFunctions[1].type = "gbellmf"
    # fis.output[1].MembershipFunctions[1].params = [5, 2, 12]

    rules =[
         "If Theta is Negative Then Force is NM",
            "If Theta is Positive Then Force is PM"
           
    ]
    
    fis.add_rule(rules)
   
     
    '''Simulation time'''
    dt = 0.01
    present_time = 0

    print("Physical characteristics")
    cart_mass = 1
    pole_mass = 1
    pole_length = 1
    # ''' states : x_dot, x, w_dot, w'''
    states = [ 0.0,0.0,0.0,0.10]      
    theta = states[3]
    cartople_ = cartople(cart_mass, pole_mass, pole_length)

    '''visualizer'''
    visualizer = CartPoleVisualizer(
        pole_length_meters=pole_length,
        cart_width_meters=0.5,
        cart_height_meters=0.5
    )


    # force[0] = 1.0
    while(True):
        outputs = fis.compute([theta])
        force = outputs[0]
        fn = lambda y : cartople_(y,force, 9.8)
        states = rk4(fn, states, dt )
        theta = (states[3] + math.pi) % (2 * math.pi) - math.pi
        states[3] = theta

        cart_pos = states[1]
        pole_angle = states[3]
        cart_vel = states[0]
        pole_vel = states[2]

        if not visualizer.update(cart_pos, pole_angle, cart_vel, pole_vel):
            break
            
        # break

        present_time += dt
        
        # angle = (states[3, t+1] + math.pi) % (2 * math.pi) - math.pi
        # states[3, t+1] = angle

        # cart_positions = states[1,:]
        # pole_angles = states[3,:]
    
        # print("Pole Angle:", pole_angles)
        # plot_graph(time, force, cart_positions, pole_angles, filename="cartpole_free.png")

        
        # visualizer = CartPoleVisualizer()
        # visualizer.visualize(cart_positions, pole_angles, dt = 0.001)
        

    