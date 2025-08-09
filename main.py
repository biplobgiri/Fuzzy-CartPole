import numpy as np
# import matplotlib as plt

from cartpole import cartople
from rk4 import rk4
from visualize import CartPoleVisualizer

if __name__ == "__main__":
    '''Simulation time'''
    dt = 0.0001
    stop_time = 2
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
    force[0] = 1

    for t in range(0,100):
        fn = lambda y : cartople_(y, force , 9.8)
        states[:,t+1] = rk4(fn, states[:,t].astype(float), dt )
    
    cart_positions = states[:,1]
    pole_angles = states[:,3]

    # visualizer = CartPoleVisualizer()
    # visualizer.visualize(cart_positions, pole_angles, delay_ms=50)
    

    