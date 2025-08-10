import pygame
import numpy as np
import math
import sys

class CartPoleVisualizer:
    def __init__(self, width=800, height=600, pole_length_meters=2.0, cart_width_meters=0.750, cart_height_meters=0.50):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("CartPole Visualizer")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 100, 100)
        self.GRAY = (128, 128, 128)
        
        # Physical dimensions in meters
        self.pole_length_meters = pole_length_meters
        self.cart_width_meters = cart_width_meters
        self.cart_height_meters = cart_height_meters
        
        # Scale factor for position (pixels per meter)
        self.scale = 100
        
        # Convert physical dimensions to pixels
        self.cart_width = int(cart_width_meters * self.scale)
        self.cart_height = int(cart_height_meters * self.scale)
        self.pole_length = int(pole_length_meters * self.scale)
        self.pole_width = 8
        
        # Ground level
        self.ground_y = height - 100
        
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
        
        # Draw wheels (proportional to cart size)
        wheel_radius = max(8, int(self.cart_height * 0.3))
        wheel_y = self.ground_y - wheel_radius // 2
        pygame.draw.circle(self.screen, self.GRAY, 
                         (int(screen_x - self.cart_width // 3), wheel_y), wheel_radius)
        pygame.draw.circle(self.screen, self.GRAY, 
                         (int(screen_x + self.cart_width // 3), wheel_y), wheel_radius)
        
        return screen_x, self.ground_y - self.cart_height // 2
    
    def draw_pole(self, cart_x, cart_y, angle):
        """Draw the pole at given angle (in radians)"""
        # Calculate pole end position
        pole_end_x = cart_x + self.pole_length * math.sin(angle)
        pole_end_y = cart_y - self.pole_length * math.cos(angle)
        
        # Draw pole
        pygame.draw.line(self.screen, self.RED, 
                        (cart_x, cart_y), 
                        (pole_end_x, pole_end_y), 
                        self.pole_width)
        
        # Draw joint (pivot point) - proportional to cart size
        joint_radius = max(6, int(self.cart_height * 0.2))
        pygame.draw.circle(self.screen, self.BLACK, (int(cart_x), int(cart_y)), joint_radius)
        
        # Draw pole tip - proportional to pole
        tip_radius = max(4, int(self.pole_width * 0.8))
        pygame.draw.circle(self.screen, self.RED, (int(pole_end_x), int(pole_end_y)), tip_radius)
    
    def draw_ground(self):
        """Draw the ground line"""
        pygame.draw.line(self.screen, self.BLACK, 
                        (0, self.ground_y), 
                        (self.width, self.ground_y), 3)
    
    def draw_info(self, current_time, total_time, cart_pos, pole_angle):
        """Draw information text"""
        font = pygame.font.Font(None, 36)
        
        # Time counter
        time_text = font.render(f"Time: {current_time:.2f}s / {total_time:.2f}s", True, self.BLACK)
        self.screen.blit(time_text, (10, 10))
        
        # Position and angle
        pos_text = font.render(f"Cart Position: {cart_pos:.3f}m", True, self.BLACK)
        self.screen.blit(pos_text, (10, 50))
        
        angle_deg = math.degrees(pole_angle)
        angle_text = font.render(f"Pole Angle: {angle_deg:.1f}°", True, self.BLACK)
        self.screen.blit(angle_text, (10, 90))
        
        # Instructions
        inst_text = font.render("Press SPACE to pause/resume, ESC to quit", True, self.BLACK)
        self.screen.blit(inst_text, (10, self.height - 30))
    
    def visualize(self, cart_positions, pole_angles, dt=0.02):
        """
        Visualize the cartpole system in real time
        
        Args:
            cart_positions: numpy array of cart positions
            pole_angles: numpy array of pole angles (in radians)
            dt: time step between data points (default: 0.02s)
        """
        if len(cart_positions) != len(pole_angles):
            raise ValueError("cart_positions and pole_angles must have same length")
        
        running = True
        paused = False
        step = 0
        total_steps = len(cart_positions)
        total_time = (total_steps - 1) * dt
        
        # Real-time timing
        start_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        last_update_time = start_time
        
        while running and step < total_steps:
            current_real_time = pygame.time.get_ticks() / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        if not paused:
                            # Reset timing when unpausing
                            start_time = current_real_time - step * dt
                    elif event.key == pygame.K_r:
                        step = 0  # Restart animation
                        start_time = current_real_time
            
            if not paused:
                # Calculate which step we should be at based on real time
                elapsed_time = current_real_time - start_time
                target_step = int(elapsed_time / dt)
                
                # Update step if we need to advance
                if target_step > step and target_step < total_steps:
                    step = target_step
                
                # Clear screen
                self.screen.fill(self.WHITE)
                
                # Get current state
                current_time = step * dt
                cart_pos = cart_positions[step]
                pole_angle = pole_angles[step]
                
                # Draw components
                self.draw_ground()
                cart_screen_x, cart_screen_y = self.draw_cart(cart_pos)
                self.draw_pole(cart_screen_x, cart_screen_y, pole_angle)
                self.draw_info(current_time, total_time, cart_pos, pole_angle)
                
                # Update display
                pygame.display.flip()
            
            # Maintain consistent frame rate
            self.clock.tick(self.fps)
        
        # Keep window open at the end
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            self.clock.tick(30)
        
        pygame.quit()

# Example usage
if __name__ == "__main__":
    # Create sample data
    t = np.linspace(0, 4 * np.pi, 200)
    cart_positions = 0.5 * np.sin(0.5 * t)  # Cart oscillating
    pole_angles = 0.3 * np.sin(2 * t)       # Pole swinging
    
    # Create visualizer with 1-meter dimensions
    visualizer = CartPoleVisualizer(
        pole_length_meters=1.0,    # 1 meter pole
        cart_width_meters=1.0,     # 1 meter cart width
        cart_height_meters=1.0     # 1 meter cart height
    )
    
    # Visualize with real-time playback
    visualizer.visualize(cart_positions, pole_angles, dt=0.02)