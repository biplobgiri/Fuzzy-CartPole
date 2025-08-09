import math 
import numpy as np

class cartople:
    def __init__(self, cart_mass, pole_mass, pole_length, firction=False, dimensions="2D"):
        self.cart_mass = cart_mass
        self.pole_mass = pole_mass
        self.pole_length = pole_length
        self.pole_half_length = pole_length / 2
        self.firction = firction
        self.dimensions = dimensions
        print("CartPole Initialized")
    
    def __call__(self, states,force, g = 9.8):
        x_dot = states[0]  # Cart Linear velocity
        x = states[1]      # Cart X position
        w_dot = states[2]  # Pole Anuglar velocity
        w = states[3]      # Pole Anuglar position

        s_theta = math.sin(w)
        c_theta = math.cos(w)

        total_mass = self.cart_mass + self.pole_mass

        ''' Calculate w_ddot'''
        inside_bracket = (- force - self.pole_mass * self.pole_half_length * w_dot* w_dot * s_theta) / total_mass
        num = g*s_theta + c_theta * inside_bracket
        deno = self.pole_half_length * ( 4/3 - (self.pole_mass* c_theta * c_theta)/total_mass)

        w_ddot = num/deno

        ''' Calculate x_ddot'''
        inside_bracket = w_dot*w_dot*s_theta - w_ddot*w_ddot*c_theta
        num = force + self.pole_mass * self.pole_half_length * inside_bracket
        deno = total_mass

        x_ddot = num/deno

        return np.array([x_ddot,x_dot,w_ddot,w_dot],  dtype=float)
