
import time
import math
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from fuzzy.fuzzy import fuzzy

from cartpole import cartople
from rk4 import rk4
from visualize import RealtimeCartPoleVisualizer



from matplotlib.ticker import MaxNLocator
def plot_graph(dt, lv, dir_path, filename, show_img=False):
    if dir_path is None:
        raise ValueError("Output directory path not provided")

    os.makedirs(dir_path, exist_ok=True)

    force      = lv[0, :]
    target     = lv[1, :]
    car_vel    = lv[2, :]
    car_pos    = lv[3, :]
    pole_vel   = lv[4, :]
    pole_angle = np.degrees(lv[5, :])

    time = np.arange(0, len(force) * dt, dt)

    # create "grid" layout for subplots
    fig = plt.figure(figsize=(8, 12))

    # --- Plot 1: Force ---
    ax1 = plt.subplot2grid((5,1), (0,0))
    ax1.plot(time, force, color='tab:blue')
    ax1.set_ylabel('Force (N)')
    ax1.set_title('Force vs Time')
    ax1.grid(True)
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=10))
    ax1.yaxis.set_major_locator(MaxNLocator(nbins=10))

    # --- Plot 2: Target & Cart Position ---
    ax2 = plt.subplot2grid((5,1), (1,0))
    ax2.plot(time, target, label="Target", color='tab:red')
    ax2.plot(time, car_pos, label="Cart Position", color='tab:orange')
    ax2.set_ylabel('Position (m)')
    ax2.set_title('Target & Cart Position vs Time')
    ax2.legend()
    ax2.grid(True)
    ax2.xaxis.set_major_locator(MaxNLocator(nbins=10))
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=10))

    # --- Plot 3a: Car Velocity ---
    ax3 = plt.subplot2grid((5,1), (2,0))
    ax3.plot(time, car_vel, color='tab:blue')
    ax3.set_ylabel('Car Vel (m/s)')
    ax3.grid(True)

    # --- Plot 3b: Pole Velocity ---
    ax4 = plt.subplot2grid((5,1), (3,0))
    ax4.plot(time, pole_vel, color='tab:green')
    ax4.set_ylabel('Pole Vel (rad/s)')
    ax4.grid(True)

    # --- Plot 3c: Pole Angle ---
    ax5 = plt.subplot2grid((5,1), (4,0))
    ax5.plot(time, pole_angle, color='tab:purple')
    ax5.set_ylabel('Pole Angle (deg)')
    ax5.set_xlabel('Time (s)')
    ax5.grid(True)

    plt.tight_layout()
    plt.savefig(f"{dir_path}/{filename}", dpi=600)

    if show_img:
        plt.show()
    else:
        plt.close()


if __name__ == "__main__":
    '''Fuzzy Inference system'''
    fis = fuzzy("Cartpole-controller", 4, 2, 1 ,8)

    fis.input[0].name = "Theta"
    fis.input[0].range = [-math.pi, math.pi]
    fis.input[0].MembershipFunctions[0].name = "Negative"
    fis.input[0].MembershipFunctions[0].type = "zmf"
    fis.input[0].MembershipFunctions[0].params = [-0.5, 0.5]
    fis.input[0].MembershipFunctions[1].name = "Positive"
    fis.input[0].MembershipFunctions[1].type = "smf"
    fis.input[0].MembershipFunctions[1].params = [-0.5, 0.5]

    fis.input[1].name = "Theta_dot"
    fis.input[1].range = [-10, 10]
    fis.input[1].MembershipFunctions[0].name = "Negative"
    fis.input[1].MembershipFunctions[0].type = "zmf"
    fis.input[1].MembershipFunctions[0].params = [-5, 5]
    fis.input[1].MembershipFunctions[1].name = "Positive"
    fis.input[1].MembershipFunctions[1].type = "smf"
    fis.input[1].MembershipFunctions[1].params = [-5, 5]

    fis.input[2].name = "Cart_Position"
    fis.input[2].range = [-5, 5]
    fis.input[2].MembershipFunctions[0].name = "Negative"
    fis.input[2].MembershipFunctions[0].type = "zmf"
    fis.input[2].MembershipFunctions[0].params = [-1, 1]
    fis.input[2].MembershipFunctions[1].name = "Positive"
    fis.input[2].MembershipFunctions[1].type = "smf"
    fis.input[2].MembershipFunctions[1].params = [-1, 1]

    fis.input[3].name = "Cart_Velocity"
    fis.input[3].range = [-5, 5]
    fis.input[3].MembershipFunctions[0].name = "Negative"
    fis.input[3].MembershipFunctions[0].type = "zmf"
    fis.input[3].MembershipFunctions[0].params = [-5, 5]
    fis.input[3].MembershipFunctions[1].name = "Positive"
    fis.input[3].MembershipFunctions[1].type = "smf"
    fis.input[3].MembershipFunctions[1].params = [-5, 5]
    
    fis.output[0].name = "force"
    fis.output[0].range = [-20, 20]
    fis.output[0].MembershipFunctions[0].name = "NM"
    fis.output[0].MembershipFunctions[0].type = "gbellmf"
    fis.output[0].MembershipFunctions[0].params = [5, 2, -12]
    fis.output[0].MembershipFunctions[1].name = "PM"
    fis.output[0].MembershipFunctions[1].type = "gbellmf"
    fis.output[0].MembershipFunctions[1].params = [5, 2, 12]

    fis.output[0].MembershipFunctions[2].name = "NL"
    fis.output[0].MembershipFunctions[2].type = "gbellmf"
    fis.output[0].MembershipFunctions[2].params = [5, 2, -20]
    fis.output[0].MembershipFunctions[3].name = "PL"
    fis.output[0].MembershipFunctions[3].type = "gbellmf"
    fis.output[0].MembershipFunctions[3].params = [5, 2, 20]

    fis.output[0].MembershipFunctions[4].name = "NS"
    fis.output[0].MembershipFunctions[4].type = "gbellmf"
    fis.output[0].MembershipFunctions[4].params = [2, 2, -2]
    fis.output[0].MembershipFunctions[5].name = "PS"
    fis.output[0].MembershipFunctions[5].type = "gbellmf"
    fis.output[0].MembershipFunctions[5].params = [2, 2, 2]

    fis.output[0].MembershipFunctions[6].name = "NM1"
    fis.output[0].MembershipFunctions[6].type = "gbellmf"
    fis.output[0].MembershipFunctions[6].params = [3, 2, -6]
    fis.output[0].MembershipFunctions[7].name = "PM2"
    fis.output[0].MembershipFunctions[7].type = "gbellmf"
    fis.output[0].MembershipFunctions[7].params = [3, 2, 6]

  

    rules =[
        "If Theta is Negative Then Force is NM",
        "If Theta is Positive Then Force is PM",
        "If Theta_dot is Negative Then Force is NL",
        "If Theta_dot is Positive Then Force is PL",
        "If Cart_Position is Positive Then Force is NS",
        "If Cart_Position is Negative Then Force is PS",
        "If Cart_Velocity is Negative Then Force is NM1",
        "If Cart_Velocity is Positive Then Force is PM1",

        # "If Theta is Negative AND Theta_dot is Positive Then Force is NM",
        # "If Theta is Positive AND Theta_dot is Negative Then Force is PM",
        # "If Theta is Negative AND Theta_dot is Negative Then Force is NL",
        # "If Theta is Positive AND Theta_dot is Positive Then Force is PL",
        # "If Theta is Positive And Theta_dot is Negative Then Force is NM",
        # "If Theta is Negative And Theta_dot is Positive Then Force is PM",
        # "If Theta is Negative And Theta_dot is Negative Then Force is NL",
        # "If Theta is Positive And Theta_dot is Positive Then Force is PL"  
        
    ]
    
    fis.add_rule(rules)
    # fis.visualize_memFunc("/home/kuns/stuffs/AI_lab/Fuzzy-CartPole/Images/member_functions")
     
    '''Simulation time'''
    dt = 0.05
    present_time = 0

    cart_mass = 1
    pole_mass = 0.1
    pole_length = 1

    ''' states : x_dot, x, w_dot, w'''
    states = [ 0.0,0.0,0.0,0.0]      
    theta = states[3]
    cartople_ = cartople(cart_mass, pole_mass, pole_length)

    '''visualizer'''
    visualizer = RealtimeCartPoleVisualizer(
        pole_length_meters=pole_length,
        cart_width_meters=1.0,
        cart_height_meters=0.5
    )

    target_pos = 0.0
    logged_variables =[]
    while(True):
        start = time.time()
        target_pos = visualizer.get_target_position()

        outputs = fis.compute([theta,states[2],(target_pos - states[1]),states[0]])
        force = outputs[0]

        fn = lambda y : cartople_(y,force, 9.8)
        states = rk4(fn, states, dt )

        theta = (states[3] + math.pi) % (2 * math.pi) - math.pi
        states[3] = theta

        # Get current target position from slider
        cart_vel = states[0]
        cart_pos = states[1]
        pole_vel = states[2]
        pole_angle = states[3]
    
        if not visualizer.update(cart_pos, pole_angle, cart_vel, pole_vel):
            print("Visualization Ended")
            break

        present_time += dt
        finish = time.time()
        logged_variables.append([
            float(force),
            float(target_pos),
            float(cart_vel),
            float(cart_pos),
            float(pole_vel),
            float(pole_angle)
        ])
       
    logged_variables = np.array(logged_variables).T
    plot = False
    if plot:
        plot_graph(dt,logged_variables, "/home/kuns/stuffs/AI_lab/Fuzzy-CartPole/Images", "states.png",)
    