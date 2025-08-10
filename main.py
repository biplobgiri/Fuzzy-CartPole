import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

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
    axs[2].set_ylabel('Angle (deg)')
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
    '''Simulation time'''
    dt = 0.001
    stop_time = 10
    time = np.arange(0, stop_time + dt, dt)

    print("Physical characteristics")
    cart_mass = 1
    pole_mass = 1
    pole_length = 2

    ''' states : x_dot, x, w_dot, w'''
    states = np.empty((4, len(time)))
    states[:,0] = [ 0.0,0.0,0.0,0.0]        # Intial State

    cartople_ = cartople(cart_mass, pole_mass, pole_length)

    force = np.zeros(len(time))
    i = 0
    t = 0
    while True:
        force[i] = 1.0
        t = t+ dt
        i = i + 1
        if t >= 1:
            break

    # force[0] = 1.0
        
    for t in range(0,len(time)-1):
        fn = lambda y : cartople_(y,force[t], 9.8)
        states[:,t+1] = rk4(fn, states[:,t].astype(float), dt )
        if states[3,t] > math.pi:
            states[3,t] -= 2*math.pi
        elif states[3,t] < -math.pi:
            states[3,t] += 2*math.pi
    
    cart_positions = states[1,:]
    pole_angles = states[3,:]
   
    print("Pole Angle:", pole_angles)
    plot_graph(time, force, cart_positions, pole_angles, filename="cartpole_step_test(2).png")

     
    visualizer = CartPoleVisualizer()
    visualizer.visualize(cart_positions, pole_angles, dt = 0.001)
    

    