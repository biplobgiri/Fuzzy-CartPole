import pygame
import numpy as np
import math
import sys

class CartPoleVisualizer:
    def __init__(self, width=800, height=600, pole_length_meters=2.0, cart_width_meters=1.0, cart_height_meters=0.5):
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
        self.LIGHT_BLUE = (135, 206, 250)  # Sky blue
        self.DARK_GREEN = (34, 139, 34)    # Forest green
        self.BROWN = (139, 69, 19)         # Saddle brown
        self.LIGHT_GRAY = (211, 211, 211)  # Light gray
        self.DARK_GRAY = (105, 105, 105)   # Dim gray
        self.YELLOW = (255, 255, 0)        # Sun yellow
        
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
        """Draw the cart at given position with enhanced details"""
        screen_x = self.world_to_screen(x_pos)
        
        # Main cart body with 3D effect
        cart_rect = pygame.Rect(
            screen_x - self.cart_width // 2,
            self.ground_y - self.cart_height,
            self.cart_width,
            self.cart_height
        )
        pygame.draw.rect(self.screen, self.BLUE, cart_rect)
        
        # 3D highlights and shadows
        # Top highlight
        pygame.draw.line(self.screen, (150, 150, 255), 
                        (cart_rect.left, cart_rect.top), 
                        (cart_rect.right, cart_rect.top), 3)
        # Left highlight
        pygame.draw.line(self.screen, (120, 120, 255), 
                        (cart_rect.left, cart_rect.top), 
                        (cart_rect.left, cart_rect.bottom), 2)
        # Bottom shadow
        pygame.draw.line(self.screen, (0, 50, 150), 
                        (cart_rect.left, cart_rect.bottom), 
                        (cart_rect.right, cart_rect.bottom), 2)
        # Right shadow
        pygame.draw.line(self.screen, (0, 50, 150), 
                        (cart_rect.right, cart_rect.top), 
                        (cart_rect.right, cart_rect.bottom), 2)
        
        # Draw enhanced wheels with spokes
        wheel_radius = max(8, int(self.cart_height * 0.3))
        wheel_y = self.ground_y - wheel_radius // 2
        
        # Left wheel
        left_wheel_x = int(screen_x - self.cart_width // 3)
        # Outer rim
        pygame.draw.circle(self.screen, self.BLACK, (left_wheel_x, wheel_y), wheel_radius + 1)
        pygame.draw.circle(self.screen, self.DARK_GRAY, (left_wheel_x, wheel_y), wheel_radius)
        # Inner wheel
        pygame.draw.circle(self.screen, self.LIGHT_GRAY, (left_wheel_x, wheel_y), wheel_radius - 4)
        # Spokes
        for i in range(4):
            angle = i * math.pi / 2
            spoke_end_x = left_wheel_x + (wheel_radius - 5) * math.cos(angle)
            spoke_end_y = wheel_y + (wheel_radius - 5) * math.sin(angle)
            pygame.draw.line(self.screen, self.BLACK, 
                           (left_wheel_x, wheel_y), (spoke_end_x, spoke_end_y), 2)
        # Center hub
        pygame.draw.circle(self.screen, self.BLACK, (left_wheel_x, wheel_y), 4)
        
        # Right wheel (same design)
        right_wheel_x = int(screen_x + self.cart_width // 3)
        # Outer rim
        pygame.draw.circle(self.screen, self.BLACK, (right_wheel_x, wheel_y), wheel_radius + 1)
        pygame.draw.circle(self.screen, self.DARK_GRAY, (right_wheel_x, wheel_y), wheel_radius)
        # Inner wheel
        pygame.draw.circle(self.screen, self.LIGHT_GRAY, (right_wheel_x, wheel_y), wheel_radius - 4)
        # Spokes
        for i in range(4):
            angle = i * math.pi / 2
            spoke_end_x = right_wheel_x + (wheel_radius - 5) * math.cos(angle)
            spoke_end_y = wheel_y + (wheel_radius - 5) * math.sin(angle)
            pygame.draw.line(self.screen, self.BLACK, 
                           (right_wheel_x, wheel_y), (spoke_end_x, spoke_end_y), 2)
        # Center hub
        pygame.draw.circle(self.screen, self.BLACK, (right_wheel_x, wheel_y), 4)
        
        return screen_x, self.ground_y - self.cart_height // 2
    
    def draw_pole(self, cart_x, cart_y, angle):
        """Draw the pole as a mechanical rod with segments"""
        # Calculate pole end position
        pole_end_x = cart_x + self.pole_length * math.sin(angle)
        pole_end_y = cart_y - self.pole_length * math.cos(angle)
        
        # Draw pole as segmented mechanical rod
        num_segments = 5
        segment_length = self.pole_length / num_segments
        
        for i in range(num_segments):
            # Calculate segment positions
            seg_start_ratio = i / num_segments
            seg_end_ratio = (i + 1) / num_segments
            
            seg_start_x = cart_x + self.pole_length * seg_start_ratio * math.sin(angle)
            seg_start_y = cart_y - self.pole_length * seg_start_ratio * math.cos(angle)
            seg_end_x = cart_x + self.pole_length * seg_end_ratio * math.sin(angle)
            seg_end_y = cart_y - self.pole_length * seg_end_ratio * math.cos(angle)
            
            # Alternate segment colors for mechanical look
            color = (200, 50, 50) if i % 2 == 0 else (150, 30, 30)
            pygame.draw.line(self.screen, color,
                           (seg_start_x, seg_start_y), (seg_end_x, seg_end_y), 
                           self.pole_width)
            
            # Add joint markers between segments
            if i > 0:
                joint_color = self.BLACK
                pygame.draw.circle(self.screen, joint_color, 
                                 (int(seg_start_x), int(seg_start_y)), 3)
        
        # Draw main pole structure outline
        pygame.draw.line(self.screen, self.BLACK,
                        (cart_x, cart_y), (pole_end_x, pole_end_y), 2)
        
        # Draw rectangular base joint (more mechanical)
        joint_size = max(8, int(self.cart_height * 0.25))
        joint_rect = pygame.Rect(
            int(cart_x - joint_size // 2),
            int(cart_y - joint_size // 2),
            joint_size,
            joint_size
        )
        pygame.draw.rect(self.screen, self.DARK_GRAY, joint_rect)
        pygame.draw.rect(self.screen, self.BLACK, joint_rect, 2)
        # Bolt holes
        pygame.draw.circle(self.screen, self.BLACK, 
                         (int(cart_x - joint_size // 4), int(cart_y - joint_size // 4)), 1)
        pygame.draw.circle(self.screen, self.BLACK, 
                         (int(cart_x + joint_size // 4), int(cart_y + joint_size // 4)), 1)
        
        # Draw rectangular end cap instead of round tip
        end_size = max(6, int(self.pole_width))
        end_rect = pygame.Rect(
            int(pole_end_x - end_size // 2),
            int(pole_end_y - end_size // 2),
            end_size,
            end_size
        )
        pygame.draw.rect(self.screen, (180, 40, 40), end_rect)
        pygame.draw.rect(self.screen, self.BLACK, end_rect, 1)
    
    def draw_background(self):
        """Draw an interesting background with sky, clouds, and sun"""
        # Sky gradient (simple approach - fill with sky blue)
        self.screen.fill(self.LIGHT_BLUE)
        
        # Draw sun
        sun_x, sun_y = self.width - 100, 80
        pygame.draw.circle(self.screen, self.YELLOW, (sun_x, sun_y), 35)
        pygame.draw.circle(self.screen, (255, 255, 150), (sun_x, sun_y), 25)  # Bright center
        
        # Draw sun rays
        for i in range(8):
            angle = i * math.pi / 4
            ray_start_x = sun_x + 45 * math.cos(angle)
            ray_start_y = sun_y + 45 * math.sin(angle)
            ray_end_x = sun_x + 60 * math.cos(angle)
            ray_end_y = sun_y + 60 * math.sin(angle)
            pygame.draw.line(self.screen, self.YELLOW, 
                           (ray_start_x, ray_start_y), (ray_end_x, ray_end_y), 3)
        
        # Draw clouds
        cloud_positions = [(150, 100), (400, 80), (600, 120)]
        for cloud_x, cloud_y in cloud_positions:
            # Each cloud made of multiple circles
            pygame.draw.circle(self.screen, self.WHITE, (cloud_x, cloud_y), 25)
            pygame.draw.circle(self.screen, self.WHITE, (cloud_x + 20, cloud_y), 20)
            pygame.draw.circle(self.screen, self.WHITE, (cloud_x - 20, cloud_y), 20)
            pygame.draw.circle(self.screen, self.WHITE, (cloud_x + 10, cloud_y - 15), 18)
            pygame.draw.circle(self.screen, self.WHITE, (cloud_x - 10, cloud_y - 15), 18)
    
    def draw_ground(self):
        """Draw an interesting ground surface with grass texture"""
        # Underground/soil layer
        underground_rect = pygame.Rect(0, self.ground_y, self.width, self.height - self.ground_y)
        pygame.draw.rect(self.screen, self.BROWN, underground_rect)
        
        # Ground surface line (main track)
        pygame.draw.line(self.screen, self.DARK_GRAY, 
                        (0, self.ground_y), 
                        (self.width, self.ground_y), 4)
        
        # Track markings every 100 pixels (1 meter)
        for x in range(0, self.width, 100):
            # Major tick marks every meter
            pygame.draw.line(self.screen, self.WHITE, 
                           (x, self.ground_y - 5), (x, self.ground_y + 5), 2)
            
            # Distance labels (in meters relative to center)
            if x != self.width // 2:  # Don't draw at center
                distance = (x - self.width // 2) / self.scale
                font = pygame.font.Font(None, 24)
                text = font.render(f"{distance:.0f}m", True, self.WHITE)
                text_rect = text.get_rect()
                text_rect.centerx = x
                text_rect.y = self.ground_y + 10
                self.screen.blit(text, text_rect)
        
        # Center line (zero position)
        center_x = self.width // 2
        pygame.draw.line(self.screen, (255, 255, 0), 
                        (center_x, self.ground_y - 8), (center_x, self.ground_y + 8), 3)
        
        # Grass texture above ground
        grass_y = self.ground_y - 15
        for x in range(0, self.width, 8):
            # Random grass blade heights
            blade_height = 10 + (hash(x) % 8)
            pygame.draw.line(self.screen, self.DARK_GREEN, 
                           (x, grass_y), (x, grass_y + blade_height), 2)
            # Lighter grass tips
            if blade_height > 12:
                pygame.draw.line(self.screen, (50, 200, 50), 
                               (x, grass_y), (x, grass_y + 4), 1)
    
    def draw_info(self, current_time, total_time, cart_pos, pole_angle):
        """Draw information text with enhanced styling"""
        # Semi-transparent background for text
        info_surface = pygame.Surface((300, 140))
        info_surface.set_alpha(200)
        info_surface.fill((0, 0, 0))
        self.screen.blit(info_surface, (5, 5))
        
        font = pygame.font.Font(None, 36)
        
        # Time counter
        time_text = font.render(f"Time: {current_time:.2f}s / {total_time:.2f}s", True, self.WHITE)
        self.screen.blit(time_text, (10, 10))
        
        # Position and angle
        pos_text = font.render(f"Cart Position: {cart_pos:.3f}m", True, self.WHITE)
        self.screen.blit(pos_text, (10, 50))
        
        angle_deg = math.degrees(pole_angle)
        angle_text = font.render(f"Pole Angle: {angle_deg:.1f}°", True, self.WHITE)
        self.screen.blit(angle_text, (10, 90))
        
        # Instructions with background
        inst_surface = pygame.Surface((400, 30))
        inst_surface.set_alpha(200)
        inst_surface.fill((0, 0, 0))
        self.screen.blit(inst_surface, (5, self.height - 35))
        
        inst_text = font.render("SPACE: pause/resume | R: restart | ESC: quit", True, self.WHITE)
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
                
                # Draw background first
                self.draw_background()
                
                # Get current state
                current_time = step * dt
                cart_pos = cart_positions[step]
                pole_angle = pole_angles[step]
                
                # Draw components (order matters for layering)
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