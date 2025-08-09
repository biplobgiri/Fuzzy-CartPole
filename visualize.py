import pygame
import numpy as np
import math
import sys

class CartPole:
    def __init__(self, cart_mass, pole_mass, pole_length, friction=False, dimensions="2D"):
        self.cart_mass = cart_mass
        self.pole_mass = pole_mass
        self.pole_length = pole_length
        self.pole_half_length = pole_length / 2
        self.friction = friction
        self.dimensions = dimensions
        print("CartPole Initialized")
    
    def __call__(self, states, force, g=9.8):
        x_dot = states[0]  # Cart Linear velocity
        x = states[1]      # Cart X position
        w_dot = states[2]  # Pole Angular velocity
        w = states[3]      # Pole Angular position
        
        s_theta = math.sin(w)
        c_theta = math.cos(w)
        total_mass = self.cart_mass + self.pole_mass
        
        # Calculate w_ddot
        inside_bracket = (-force - self.pole_mass * self.pole_half_length * w_dot * w_dot * s_theta) / total_mass
        num = g * s_theta + c_theta * inside_bracket
        deno = self.pole_half_length * (4/3 - (self.pole_mass * c_theta * c_theta) / total_mass)
        w_ddot = num / deno
        
        # Calculate x_ddot
        inside_bracket = w_dot * w_dot * s_theta - w_ddot * c_theta
        num = force + self.pole_mass * self.pole_half_length * inside_bracket
        deno = total_mass
        x_ddot = num / deno
        
        return [x_ddot, x_dot, w_ddot, w_dot]

class CartPoleVisualizer:
    def __init__(self, width=800, height=600, pole_length_pixels=None):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("CartPole Physics Simulation")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 100, 100)
        self.GRAY = (128, 128, 128)
        self.GREEN = (0, 200, 0)
        
        # Cart and pole dimensions
        self.cart_width = 60
        self.cart_height = 30
        self.pole_length_pixels = pole_length_pixels or 100  # Visual pole length
        self.pole_width = 8
        
        # Ground level
        self.ground_y = height - 100
        
        # Scale factor for position (pixels per meter)
        self.scale = 100
        
        # Animation settings
        self.clock = pygame.time.Clock()
        self.fps = 60
        
    def world_to_screen(self, x_pos):
        """Convert world coordinates to screen coordinates"""
        screen_x = self.width // 2 + x_pos * self.scale
        return screen_x
    
    def draw_cart(self, x_pos):
        """Draw the cart at given position"""
        screen_x = self.world_to_screen(x_pos)
        cart_rect = pygame.Rect(
            screen_x - self.cart_width // 2,
            self.ground_y - self.cart_height,
            self.cart_width,
            self.cart_height
        )
        pygame.draw.rect(self.screen, self.BLUE, cart_rect)
        
        # Draw wheels
        wheel_radius = 10
        wheel_y = self.ground_y - 5
        pygame.draw.circle(self.screen, self.GRAY, 
                         (int(screen_x - self.cart_width // 3), wheel_y), wheel_radius)
        pygame.draw.circle(self.screen, self.GRAY, 
                         (int(screen_x + self.cart_width // 3), wheel_y), wheel_radius)
        
        return screen_x, self.ground_y - self.cart_height // 2
    
    def draw_pole(self, cart_x, cart_y, angle, pole_length_meters=None):
        """Draw the pole at given angle (in radians)"""
        # Use provided pole length or default visual length
        if pole_length_meters:
            pole_pixels = pole_length_meters * self.scale
        else:
            pole_pixels = self.pole_length_pixels
            
        # Calculate pole end position
        pole_end_x = cart_x + pole_pixels * math.sin(angle)
        pole_end_y = cart_y - pole_pixels * math.cos(angle)
        
        # Draw pole
        pygame.draw.line(self.screen, self.RED, 
                        (cart_x, cart_y), 
                        (pole_end_x, pole_end_y), 
                        self.pole_width)
        
        # Draw joint (pivot point)
        pygame.draw.circle(self.screen, self.BLACK, (int(cart_x), int(cart_y)), 8)
        
        # Draw pole tip
        pygame.draw.circle(self.screen, self.RED, (int(pole_end_x), int(pole_end_y)), 6)
    
    def draw_ground(self):
        """Draw the ground line"""
        pygame.draw.line(self.screen, self.BLACK, 
                        (0, self.ground_y), 
                        (self.width, self.ground_y), 3)
    
    def draw_info(self, step, total_steps, cart_pos, cart_vel, pole_angle, pole_vel, force):
        """Draw information text"""
        font = pygame.font.Font(None, 28)
        
        info_lines = [
            f"Step: {step}/{total_steps}",
            f"Cart Pos: {cart_pos:.3f}m",
            f"Cart Vel: {cart_vel:.3f}m/s",
            f"Pole Angle: {math.degrees(pole_angle):.1f}°",
            f"Pole Vel: {math.degrees(pole_vel):.1f}°/s",
            f"Force: {force:.1f}N"
        ]
        
        for i, line in enumerate(info_lines):
            text = font.render(line, True, self.BLACK)
            self.screen.blit(text, (10, 10 + i * 30))
        
        # Instructions
        inst_font = pygame.font.Font(None, 24)
        instructions = [
            "Controls: LEFT/RIGHT arrows - Apply force",
            "SPACE - Pause/Resume, R - Reset, ESC - Quit"
        ]
        for i, inst in enumerate(instructions):
            text = inst_font.render(inst, True, self.BLACK)
            self.screen.blit(text, (10, self.height - 50 + i * 25))

class CartPoleSimulation:
    def __init__(self, cart_mass=1.0, pole_mass=0.1, pole_length=0.5):
        self.cartpole = CartPole(cart_mass, pole_mass, pole_length)
        self.visualizer = CartPoleVisualizer(pole_length_pixels=pole_length * 100)  # Convert to pixels
        
        # Initial state: [x_dot, x, w_dot, w]
        self.initial_state = [0.0, 0.0, 0.0, 0.1]  # Small initial angle
        self.reset()
        
        # Simulation parameters
        self.dt = 0.02  # Time step
        self.max_force = 20.0
        
    def reset(self):
        """Reset simulation to initial state"""
        self.state = self.initial_state.copy()
        self.time = 0.0
        
    def step(self, force):
        """Advance simulation by one time step"""
        # Get derivatives from CartPole model
        derivatives = self.cartpole(self.state, force)
        
        # Euler integration
        self.state[0] += derivatives[0] * self.dt  # x_dot
        self.state[1] += derivatives[1] * self.dt  # x
        self.state[2] += derivatives[2] * self.dt  # w_dot
        self.state[3] += derivatives[3] * self.dt  # w
        
        self.time += self.dt
        
        return self.state.copy()
    
    def run_simulation(self):
        """Run interactive simulation"""
        running = True
        paused = False
        force = 0.0
        step_count = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        self.reset()
                        step_count = 0
            
            # Handle continuous key presses for force application
            keys = pygame.key.get_pressed()
            force = 0.0
            if keys[pygame.K_LEFT]:
                force = -self.max_force
            elif keys[pygame.K_RIGHT]:
                force = self.max_force
            
            if not paused:
                # Step simulation
                self.step(force)
                step_count += 1
                
                # Clear screen
                self.visualizer.screen.fill(self.visualizer.WHITE)
                
                # Draw components
                self.visualizer.draw_ground()
                cart_x, cart_y = self.visualizer.draw_cart(self.state[1])
                self.visualizer.draw_pole(cart_x, cart_y, self.state[3], self.cartpole.pole_length)
                
                # Draw info
                self.visualizer.draw_info(
                    step_count, "∞", 
                    self.state[1], self.state[0],  # position, velocity
                    self.state[3], self.state[2],  # angle, angular velocity
                    force
                )
                
                # Update display
                pygame.display.flip()
            
            self.visualizer.clock.tick(self.visualizer.fps)
        
        pygame.quit()
    

    
    def visualize_precomputed_states(self, cart_positions, cart_velocities, pole_angles, pole_velocities, forces=None):
        """
        Visualize pre-computed simulation states
        
        Args:
            cart_positions: numpy array of cart positions
            cart_velocities: numpy array of cart velocities  
            pole_angles: numpy array of pole angles (in radians)
            pole_velocities: numpy array of pole angular velocities (in rad/s)
            forces: optional numpy array of applied forces
        """
        # Validate input arrays
        arrays = [cart_positions, cart_velocities, pole_angles, pole_velocities]
        lengths = [len(arr) for arr in arrays]
        
        if not all(length == lengths[0] for length in lengths):
            raise ValueError("All input arrays must have the same length")
        
        if forces is not None and len(forces) != lengths[0]:
            raise ValueError("Forces array must have same length as state arrays")
        
        if forces is None:
            forces = np.zeros(lengths[0])  # Default to zero force
        
        running = True
        paused = False
        step = 0
        total_steps = lengths[0]
        
        while running and step < total_steps:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        step = 0  # Restart animation
            
            if not paused:
                # Clear screen
                self.visualizer.screen.fill(self.visualizer.WHITE)
                
                # Get current state
                cart_pos = cart_positions[step]
                cart_vel = cart_velocities[step]
                pole_angle = pole_angles[step]
                pole_vel = pole_velocities[step]
                force = forces[step]
                
                # Draw components
                self.visualizer.draw_ground()
                cart_x, cart_y = self.visualizer.draw_cart(cart_pos)
                self.visualizer.draw_pole(cart_x, cart_y, pole_angle, self.cartpole.pole_length)
                
                # Draw info
                self.visualizer.draw_info(
                    step + 1, total_steps,
                    cart_pos, cart_vel,
                    pole_angle, pole_vel,
                    force
                )
                
                # Update display
                pygame.display.flip()
                
                step += 1
                pygame.time.wait(20)  # 50 fps playback
            else:
                self.visualizer.clock.tick(30)
        
        # Keep window open at the end
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            self.visualizer.clock.tick(30)
        
        pygame.quit()
    
    def visualize_results(self, cart_positions, pole_angles, forces):
        """Visualize pre-computed simulation results"""
        running = True
        paused = False
        step = 0
        total_steps = len(cart_positions)
        
        while running and step < total_steps:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        step = 0  # Restart animation
            
            if not paused:
                # Clear screen
                self.visualizer.screen.fill(self.visualizer.WHITE)
                
                # Get current state
                cart_pos = cart_positions[step]
                pole_angle = pole_angles[step]
                force = forces[step] if step < len(forces) else 0
                
                # Calculate velocities (simple finite difference)
                cart_vel = 0
                pole_vel = 0
                if step > 0:
                    cart_vel = (cart_positions[step] - cart_positions[step-1]) / self.dt
                    pole_vel = (pole_angles[step] - pole_angles[step-1]) / self.dt
                
                # Draw components
                self.visualizer.draw_ground()
                cart_x, cart_y = self.visualizer.draw_cart(cart_pos)
                self.visualizer.draw_pole(cart_x, cart_y, pole_angle, self.cartpole.pole_length)
                
                # Draw info
                self.visualizer.draw_info(
                    step + 1, total_steps,
                    cart_pos, cart_vel,
                    pole_angle, pole_vel,
                    force
                )
                
                # Update display
                pygame.display.flip()
                
                step += 1
                pygame.time.wait(20)  # 50 fps playback
            else:
                self.visualizer.clock.tick(30)
        
        # Keep window open at the end
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            self.visualizer.clock.tick(30)
        
        pygame.quit()

# Example usage
if __name__ == "__main__":
    # Create simulation with custom parameters
    sim = CartPoleSimulation(cart_mass=1.0, pole_mass=0.1, pole_length=0.5)
    
    # Visualize your pre-computed states
    # Example with sample data - replace with your actual computed states
    t = np.linspace(0, 10, 500)
    cart_positions = 0.5 * np.sin(0.5 * t)              # Your computed cart positions
    cart_velocities = 0.25 * np.cos(0.5 * t)            # Your computed cart velocities
    pole_angles = 0.3 * np.sin(2 * t)                   # Your computed pole angles (radians)
    pole_velocities = 0.6 * np.cos(2 * t)               # Your computed pole angular velocities
    forces = 10 * np.sin(0.8 * t)                       # Your applied forces (optional)
    
    print("Starting visualization of pre-computed states...")
    print("SPACE to pause/resume, R to restart, ESC to quit")
    sim.visualize_precomputed_states(cart_positions, cart_velocities, 
                                   pole_angles, pole_velocities, forces)