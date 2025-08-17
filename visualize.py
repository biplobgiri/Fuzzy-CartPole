import pygame
import numpy as np
import math
import sys
import time
from collections import deque

class CartPoleVisualizer:
    def __init__(self, width=800, height=600, pole_length_meters=2.0, cart_width_meters=1.0, cart_height_meters=0.5):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Real-time CartPole Visualizer")
        
        # Day/Night toggle
        self.is_night = False
        
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
        
        # Night colors
        self.NIGHT_SKY = (25, 25, 112)     # Midnight blue
        self.MOON_COLOR = (245, 245, 220)   # Beige
        self.STAR_COLOR = (255, 255, 255)   # White
        self.NIGHT_CLOUD = (70, 70, 70)     # Dark gray
        self.NIGHT_GRASS = (0, 80, 0)       # Dark green
        
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
        
        # Sun/Moon position and radius for click detection
        self.celestial_x = self.width - 100
        self.celestial_y = 80
        self.celestial_radius = 35
        
        # Generate random star positions (fixed for consistency)
        self.stars = []
        np.random.seed(42)  # Fixed seed for consistent star positions
        for _ in range(50):
            star_x = np.random.randint(0, self.width)
            star_y = np.random.randint(0, self.height // 2)
            self.stars.append((star_x, star_y))
        
        # State tracking
        self.start_time = time.time()
        self.frame_count = 0
        self.should_close = False
        
        # History for trajectory visualization (optional)
        self.position_history = deque(maxlen=200)
        self.show_trajectory = False
    
    def should_quit(self):
        """Check if the visualizer should quit (window closed or ESC pressed)"""
        return self.should_close
    
    def world_to_screen(self, x_pos):
        """Convert world coordinates to screen coordinates"""
        screen_x = self.width // 2 + x_pos * self.scale
        return screen_x
    
    def is_point_in_circle(self, point_x, point_y, circle_x, circle_y, radius):
        """Check if a point is inside a circle"""
        distance = math.sqrt((point_x - circle_x)**2 + (point_y - circle_y)**2)
        return distance <= radius
    
    def handle_events(self):
        """Handle pygame events - call this regularly to keep window responsive"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.should_close = True
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.should_close = True
                    return False
                elif event.key == pygame.K_t:
                    self.show_trajectory = not self.show_trajectory
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = event.pos
                    if self.is_point_in_circle(mouse_x, mouse_y, self.celestial_x, self.celestial_y, self.celestial_radius + 10):
                        self.is_night = not self.is_night
        return True
    
    def draw_cart(self, x_pos):
        """Draw the cart at given position with enhanced details"""
        screen_x = self.world_to_screen(x_pos)
        
        # Adjust cart color slightly for night visibility
        cart_color = (0, 80, 200) if self.is_night else self.BLUE
        
        # Main cart body with 3D effect
        cart_rect = pygame.Rect(
            screen_x - self.cart_width // 2,
            self.ground_y - self.cart_height,
            self.cart_width,
            self.cart_height
        )
        pygame.draw.rect(self.screen, cart_color, cart_rect)
        
        # 3D highlights and shadows
        highlight_color = (120, 120, 255) if not self.is_night else (100, 100, 220)
        shadow_color = (0, 50, 150) if not self.is_night else (0, 30, 120)
        
        # Top highlight
        pygame.draw.line(self.screen, highlight_color, 
                        (cart_rect.left, cart_rect.top), 
                        (cart_rect.right, cart_rect.top), 3)
        # Left highlight
        pygame.draw.line(self.screen, highlight_color, 
                        (cart_rect.left, cart_rect.top), 
                        (cart_rect.left, cart_rect.bottom), 2)
        # Bottom shadow
        pygame.draw.line(self.screen, shadow_color, 
                        (cart_rect.left, cart_rect.bottom), 
                        (cart_rect.right, cart_rect.bottom), 2)
        # Right shadow
        pygame.draw.line(self.screen, shadow_color, 
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
        
        for i in range(num_segments):
            # Calculate segment positions
            seg_start_ratio = i / num_segments
            seg_end_ratio = (i + 1) / num_segments
            
            seg_start_x = cart_x + self.pole_length * seg_start_ratio * math.sin(angle)
            seg_start_y = cart_y - self.pole_length * seg_start_ratio * math.cos(angle)
            seg_end_x = cart_x + self.pole_length * seg_end_ratio * math.sin(angle)
            seg_end_y = cart_y - self.pole_length * seg_end_ratio * math.cos(angle)
            
            # Alternate segment colors for mechanical look
            if self.is_night:
                color = (150, 40, 40) if i % 2 == 0 else (120, 25, 25)
            else:
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
        end_color = (130, 30, 30) if self.is_night else (180, 40, 40)
        pygame.draw.rect(self.screen, end_color, end_rect)
        pygame.draw.rect(self.screen, self.BLACK, end_rect, 1)
    
    def draw_stars(self):
        """Draw twinkling stars in the night sky"""
        current_time = time.time()
        
        for i, (star_x, star_y) in enumerate(self.stars):
            # Make stars twinkle by varying their brightness
            twinkle_phase = (current_time * 2 + i) % (2 * math.pi)
            brightness = int(200 + 55 * math.sin(twinkle_phase))
            star_color = (brightness, brightness, brightness)
            
            # Vary star sizes slightly
            star_size = 1 + int(0.5 * math.sin(twinkle_phase + i))
            pygame.draw.circle(self.screen, star_color, (star_x, star_y), star_size)
    
    def draw_background(self):
        """Draw background with day/night themes"""
        if self.is_night:
            # Night sky
            self.screen.fill(self.NIGHT_SKY)
            
            # Draw stars
            self.draw_stars()
            
            # Draw moon
            pygame.draw.circle(self.screen, self.MOON_COLOR, (self.celestial_x, self.celestial_y), self.celestial_radius)
            pygame.draw.circle(self.screen, (220, 220, 200), (self.celestial_x, self.celestial_y), self.celestial_radius - 8)
            
            # Moon craters
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x - 8, self.celestial_y - 5), 4)
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x + 6, self.celestial_y + 8), 3)
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x + 3, self.celestial_y - 10), 2)
            
            # Moon glow
            for radius in range(self.celestial_radius + 5, self.celestial_radius + 20, 2):
                alpha = max(0, 30 - (radius - self.celestial_radius) * 2)
                glow_surface = pygame.Surface((radius * 2, radius * 2))
                glow_surface.set_alpha(alpha)
                pygame.draw.circle(glow_surface, (200, 200, 255), (radius, radius), radius)
                self.screen.blit(glow_surface, (self.celestial_x - radius, self.celestial_y - radius))
            
            # Night clouds
            cloud_positions = [(150, 100), (400, 80), (600, 120)]
            for cloud_x, cloud_y in cloud_positions:
                # Each cloud made of multiple circles
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x, cloud_y), 25)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x + 20, cloud_y), 20)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x - 20, cloud_y), 20)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x + 10, cloud_y - 15), 18)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x - 10, cloud_y - 15), 18)
        else:
            # Day sky
            self.screen.fill(self.LIGHT_BLUE)
            
            # Draw sun
            pygame.draw.circle(self.screen, self.YELLOW, (self.celestial_x, self.celestial_y), self.celestial_radius)
            pygame.draw.circle(self.screen, (255, 255, 150), (self.celestial_x, self.celestial_y), 25)
            
            # Draw sun rays
            for i in range(8):
                angle = i * math.pi / 4
                ray_start_x = self.celestial_x + 45 * math.cos(angle)
                ray_start_y = self.celestial_y + 45 * math.sin(angle)
                ray_end_x = self.celestial_x + 60 * math.cos(angle)
                ray_end_y = self.celestial_y + 60 * math.sin(angle)
                pygame.draw.line(self.screen, self.YELLOW, 
                               (ray_start_x, ray_start_y), (ray_end_x, ray_end_y), 3)
            
            # Day clouds
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
        track_color = (100, 100, 100) if self.is_night else self.DARK_GRAY
        pygame.draw.line(self.screen, track_color, 
                        (0, self.ground_y), 
                        (self.width, self.ground_y), 4)
        
        # Track markings every 100 pixels (1 meter)
        marking_color = (200, 200, 200) if self.is_night else self.WHITE
        for x in range(0, self.width, 100):
            # Major tick marks every meter
            pygame.draw.line(self.screen, marking_color, 
                           (x, self.ground_y - 5), (x, self.ground_y + 5), 2)
            
            # Distance labels (in meters relative to center)
            if x != self.width // 2:  # Don't draw at center
                distance = (x - self.width // 2) / self.scale
                font = pygame.font.Font(None, 24)
                text = font.render(f"{distance:.0f}m", True, marking_color)
                text_rect = text.get_rect()
                text_rect.centerx = x
                text_rect.y = self.ground_y + 10
                self.screen.blit(text, text_rect)
        
        # Center line (zero position)
        center_x = self.width // 2
        center_color = (255, 255, 100) if self.is_night else (255, 255, 0)
        pygame.draw.line(self.screen, center_color, 
                        (center_x, self.ground_y - 8), (center_x, self.ground_y + 8), 3)
        
        # Grass texture above ground
        grass_y = self.ground_y - 15
        grass_color = self.NIGHT_GRASS if self.is_night else self.DARK_GREEN
        grass_tip_color = (0, 120, 0) if self.is_night else (50, 200, 50)
        
        for x in range(0, self.width, 8):
            # Random grass blade heights
            blade_height = 10 + (hash(x) % 8)
            pygame.draw.line(self.screen, grass_color, 
                           (x, grass_y), (x, grass_y + blade_height), 2)
            # Lighter grass tips
            if blade_height > 12:
                pygame.draw.line(self.screen, grass_tip_color, 
                               (x, grass_y), (x, grass_y + 4), 1)
    
    def draw_trajectory(self):
        """Draw trajectory trail if enabled"""
        if self.show_trajectory and len(self.position_history) > 1:
            trail_color = (255, 255, 100, 100) if self.is_night else (255, 0, 0, 100)
            points = []
            for i, pos in enumerate(self.position_history):
                screen_x = self.world_to_screen(pos)
                if 0 <= screen_x <= self.width:  # Only draw visible points
                    alpha = int(255 * (i / len(self.position_history)))  # Fade trail
                    points.append((screen_x, self.ground_y - 20))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, trail_color[:3], False, points, 2)
    
    def draw_info(self, current_time, cart_pos, pole_angle, cart_velocity=None, pole_velocity=None):
        """Draw information text with enhanced styling"""
        # Semi-transparent background for text
        info_height = 200 if cart_velocity is not None else 160
        info_surface = pygame.Surface((350, info_height))
        info_surface.set_alpha(200)
        bg_color = (0, 0, 50) if self.is_night else (0, 0, 0)
        info_surface.fill(bg_color)
        self.screen.blit(info_surface, (5, 5))
        
        font = pygame.font.Font(None, 36)
        text_color = (200, 200, 255) if self.is_night else self.WHITE
        
        y_offset = 10
        
        # Time counter
        time_text = font.render(f"Time: {current_time:.2f}s", True, text_color)
        self.screen.blit(time_text, (10, y_offset))
        y_offset += 40
        
        # Position and angle
        pos_text = font.render(f"Cart Position: {cart_pos:.3f}m", True, text_color)
        self.screen.blit(pos_text, (10, y_offset))
        y_offset += 40
        
        angle_deg = math.degrees(pole_angle)
        angle_text = font.render(f"Pole Angle: {angle_deg:.1f}°", True, text_color)
        self.screen.blit(angle_text, (10, y_offset))
        y_offset += 40
        
        # Velocities if provided
        if cart_velocity is not None:
            vel_text = font.render(f"Cart Velocity: {cart_velocity:.3f}m/s", True, text_color)
            self.screen.blit(vel_text, (10, y_offset))
            y_offset += 40
        
        if pole_velocity is not None:
            pole_vel_deg = math.degrees(pole_velocity)
            pole_vel_text = font.render(f"Pole Velocity: {pole_vel_deg:.1f}°/s", True, text_color)
            self.screen.blit(pole_vel_text, (10, y_offset))
            y_offset += 40
        
        # Mode and instructions with background
        mode_text = "Night Mode" if self.is_night else "Day Mode"
        mode_surface = font.render(f"Mode: {mode_text}", True, text_color)
        self.screen.blit(mode_surface, (10, y_offset))
        
        # Instructions
        inst_surface = pygame.Surface((700, 30))
        inst_surface.set_alpha(200)
        inst_surface.fill(bg_color)
        self.screen.blit(inst_surface, (5, self.height - 35))
        
        inst_text = font.render("T: toggle trajectory | Click Sun/Moon: toggle day/night | ESC: quit", True, text_color)
        self.screen.blit(inst_text, (10, self.height - 30))
    
    def update(self, cart_position, pole_angle, cart_velocity=None, pole_velocity=None, force_redraw=True):
        """
        Update visualization with current state
        
        Args:
            cart_position: Current cart position in meters
            pole_angle: Current pole angle in radians
            cart_velocity: Optional cart velocity in m/s
            pole_velocity: Optional pole angular velocity in rad/s
            force_redraw: Whether to force a screen update (default: True)
        
        Returns:
            bool: False if window should close, True otherwise
        """
        # Handle events to keep window responsive
        if not self.handle_events():
            return False
        
        # Update position history for trajectory
        self.position_history.append(cart_position)
        
        # Calculate current time
        current_time = time.time() - self.start_time
        
        # Draw everything
        self.draw_background()
        self.draw_ground()
        
        # Draw trajectory if enabled
        self.draw_trajectory()
        
        # Draw cart and pole
        cart_screen_x, cart_screen_y = self.draw_cart(cart_position)
        self.draw_pole(cart_screen_x, cart_screen_y, pole_angle)
        
        # Draw info
        self.draw_info(current_time, cart_position, pole_angle, cart_velocity, pole_velocity)
        
        # Update display
        if force_redraw:
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        self.frame_count += 1
        return True
    
    def close(self):
        """Clean up and close the visualizer"""
        pygame.quit()

# Example usage
if __name__ == "__main__":
    # Create visualizer
    visualizer = RealtimeCartPoleVisualizer(
        pole_length_meters=1.0,
        cart_width_meters=0.8,
        cart_height_meters=0.5
    )
    
    # Simulate real-time updates
    t = 0
    dt = 0.02  # 20ms timestep
    
    try:
        while not visualizer.should_quit():
            # Simulate cartpole dynamics (replace with your actual dynamics)
            cart_pos = 0.5 * np.sin(0.5 * t)
            pole_angle = 0.3 * np.sin(2 * t)
            cart_vel = 0.25 * np.cos(0.5 * t)
            pole_vel = 0.6 * np.cos(2 * t)
            
            # Update visualization
            if not visualizer.update(cart_pos, pole_angle, cart_vel, pole_vel):
                break
            
            t += dt
            time.sleep(dt)  # Control simulation speed
            
    except KeyboardInterrupt:
        print("Simulation interrupted")
    finally:
        visualizer.close()