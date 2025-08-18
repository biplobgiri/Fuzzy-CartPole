import pygame
import numpy as np
import math
import sys
import time
from collections import deque

class RealtimeCartPoleVisualizer:
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
        self.LIGHT_BLUE = (135, 206, 250)
        self.DARK_GREEN = (34, 139, 34)
        self.BROWN = (139, 69, 19)
        self.LIGHT_GRAY = (211, 211, 211)
        self.DARK_GRAY = (105, 105, 105)
        self.YELLOW = (255, 255, 0)
        
        # Night colors
        self.NIGHT_SKY = (25, 25, 112)
        self.MOON_COLOR = (245, 245, 220)
        self.STAR_COLOR = (255, 255, 255)
        self.NIGHT_CLOUD = (70, 70, 70)
        self.NIGHT_GRASS = (0, 80, 0)
        
        # Physical dimensions
        self.pole_length_meters = pole_length_meters
        self.cart_width_meters = cart_width_meters
        self.cart_height_meters = cart_height_meters
        self.scale = 100
        
        self.cart_width = int(cart_width_meters * self.scale)
        self.cart_height = int(cart_height_meters * self.scale)
        self.pole_length = int(pole_length_meters * self.scale)
        self.pole_width = 8
        
        self.ground_y = height - 100
        
        # Animation settings
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Sun/Moon settings
        self.celestial_x = self.width - 100
        self.celestial_y = 80
        self.celestial_radius = 35
        
        # Stars
        self.stars = []
        np.random.seed(42)
        for _ in range(50):
            star_x = np.random.randint(0, self.width)
            star_y = np.random.randint(0, self.height // 2)
            self.stars.append((star_x, star_y))
        
        # State tracking
        self.start_time = time.time()
        self.frame_count = 0
        self.should_close = False
        
        # Trajectory
        self.position_history = deque(maxlen=200)
        self.show_trajectory = False
        
        # Target position slider (integrated with ground track)
        self.slider_min_pos = -3.0
        self.slider_max_pos = 3.0
        self.target_position = 0.0
        self.slider_dragging = False
        self.slider_knob_radius = 15
        
        # Calculate slider bounds based on screen and scale
        self.slider_left_x = self.world_to_screen(self.slider_min_pos)
        self.slider_right_x = self.world_to_screen(self.slider_max_pos)
        
        # Add missing slider rectangle attributes
        self.slider_x = self.slider_left_x
        self.slider_y = self.ground_y + 35
        self.slider_width = self.slider_right_x - self.slider_left_x
        self.slider_height = 20
    
    def should_quit(self):
        return self.should_close
    
    def world_to_screen(self, x_pos):
        screen_x = self.width // 2 + x_pos * self.scale
        return screen_x
    
    def is_point_in_circle(self, point_x, point_y, circle_x, circle_y, radius):
        distance = math.sqrt((point_x - circle_x)**2 + (point_y - circle_y)**2)
        return distance <= radius
    
    def get_slider_knob_x(self):
        """Get the x position of the slider knob based on target position"""
        return self.world_to_screen(self.target_position)
    
    def set_target_from_mouse_x(self, mouse_x):
        """Set target position based on mouse x coordinate"""
        # Convert screen x to world position
        target_world_pos = (mouse_x - self.width // 2) / self.scale
        # Clamp to slider bounds
        self.target_position = max(self.slider_min_pos, min(self.slider_max_pos, target_world_pos))
    
    def is_point_in_slider(self, mouse_x, mouse_y):
        """Check if mouse is over the slider knob"""
        knob_x = self.get_slider_knob_x()
        knob_y = self.slider_y + self.slider_height // 2
        return (abs(mouse_x - knob_x) <= self.slider_knob_radius and 
                abs(mouse_y - knob_y) <= self.slider_knob_radius)
    
    def is_mouse_on_track(self, mouse_x, mouse_y):
        """Check if mouse is on the ground track area for target setting"""
        return (self.slider_left_x <= mouse_x <= self.slider_right_x and 
                self.ground_y - 10 <= mouse_y <= self.ground_y + 60)
    
    def handle_events(self):
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
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if self.is_point_in_circle(mouse_x, mouse_y, self.celestial_x, self.celestial_y, self.celestial_radius + 10):
                        self.is_night = not self.is_night
                    elif self.is_point_in_slider(mouse_x, mouse_y):
                        self.slider_dragging = True
                    elif (self.slider_x <= mouse_x <= self.slider_x + self.slider_width and
                          self.slider_y <= mouse_y <= self.slider_y + self.slider_height):
                        self.set_target_from_mouse_x(mouse_x)
                        self.slider_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.slider_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.slider_dragging:
                    mouse_x, mouse_y = event.pos
                    self.set_target_from_mouse_x(mouse_x)
        return True
    
    def draw_cart(self, x_pos):
        screen_x = self.world_to_screen(x_pos)
        cart_color = (0, 80, 200) if self.is_night else self.BLUE
        
        cart_rect = pygame.Rect(
            screen_x - self.cart_width // 2,
            self.ground_y - self.cart_height,
            self.cart_width,
            self.cart_height
        )
        pygame.draw.rect(self.screen, cart_color, cart_rect)
        
        highlight_color = (120, 120, 255) if not self.is_night else (100, 100, 220)
        shadow_color = (0, 50, 150) if not self.is_night else (0, 30, 120)
        
        pygame.draw.line(self.screen, highlight_color, 
                        (cart_rect.left, cart_rect.top), 
                        (cart_rect.right, cart_rect.top), 3)
        pygame.draw.line(self.screen, highlight_color, 
                        (cart_rect.left, cart_rect.top), 
                        (cart_rect.left, cart_rect.bottom), 2)
        pygame.draw.line(self.screen, shadow_color, 
                        (cart_rect.left, cart_rect.bottom), 
                        (cart_rect.right, cart_rect.bottom), 2)
        pygame.draw.line(self.screen, shadow_color, 
                        (cart_rect.right, cart_rect.top), 
                        (cart_rect.right, cart_rect.bottom), 2)
        
        wheel_radius = max(8, int(self.cart_height * 0.3))
        wheel_y = self.ground_y - wheel_radius // 2
        
        for wheel_offset in [-self.cart_width // 3, self.cart_width // 3]:
            wheel_x = int(screen_x + wheel_offset)
            pygame.draw.circle(self.screen, self.BLACK, (wheel_x, wheel_y), wheel_radius + 1)
            pygame.draw.circle(self.screen, self.DARK_GRAY, (wheel_x, wheel_y), wheel_radius)
            pygame.draw.circle(self.screen, self.LIGHT_GRAY, (wheel_x, wheel_y), wheel_radius - 4)
            
            for i in range(4):
                angle = i * math.pi / 2
                spoke_end_x = wheel_x + (wheel_radius - 5) * math.cos(angle)
                spoke_end_y = wheel_y + (wheel_radius - 5) * math.sin(angle)
                pygame.draw.line(self.screen, self.BLACK, 
                               (wheel_x, wheel_y), (spoke_end_x, spoke_end_y), 2)
            pygame.draw.circle(self.screen, self.BLACK, (wheel_x, wheel_y), 4)
        
        return screen_x, self.ground_y - self.cart_height // 2
    
    def draw_pole(self, cart_x, cart_y, angle):
        pole_end_x = cart_x + self.pole_length * math.sin(angle)
        pole_end_y = cart_y - self.pole_length * math.cos(angle)
        
        num_segments = 5
        for i in range(num_segments):
            seg_start_ratio = i / num_segments
            seg_end_ratio = (i + 1) / num_segments
            
            seg_start_x = cart_x + self.pole_length * seg_start_ratio * math.sin(angle)
            seg_start_y = cart_y - self.pole_length * seg_start_ratio * math.cos(angle)
            seg_end_x = cart_x + self.pole_length * seg_end_ratio * math.sin(angle)
            seg_end_y = cart_y - self.pole_length * seg_end_ratio * math.cos(angle)
            
            if self.is_night:
                color = (150, 40, 40) if i % 2 == 0 else (120, 25, 25)
            else:
                color = (200, 50, 50) if i % 2 == 0 else (150, 30, 30)
            
            pygame.draw.line(self.screen, color,
                           (seg_start_x, seg_start_y), (seg_end_x, seg_end_y), 
                           self.pole_width)
            
            if i > 0:
                pygame.draw.circle(self.screen, self.BLACK, 
                                 (int(seg_start_x), int(seg_start_y)), 3)
        
        pygame.draw.line(self.screen, self.BLACK,
                        (cart_x, cart_y), (pole_end_x, pole_end_y), 2)
        
        joint_size = max(8, int(self.cart_height * 0.25))
        joint_rect = pygame.Rect(
            int(cart_x - joint_size // 2),
            int(cart_y - joint_size // 2),
            joint_size,
            joint_size
        )
        pygame.draw.rect(self.screen, self.DARK_GRAY, joint_rect)
        pygame.draw.rect(self.screen, self.BLACK, joint_rect, 2)
        
        pygame.draw.circle(self.screen, self.BLACK, 
                         (int(cart_x - joint_size // 4), int(cart_y - joint_size // 4)), 1)
        pygame.draw.circle(self.screen, self.BLACK, 
                         (int(cart_x + joint_size // 4), int(cart_y + joint_size // 4)), 1)
        
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
        current_time = time.time()
        for i, (star_x, star_y) in enumerate(self.stars):
            twinkle_phase = (current_time * 2 + i) % (2 * math.pi)
            brightness = int(200 + 55 * math.sin(twinkle_phase))
            star_color = (brightness, brightness, brightness)
            star_size = 1 + int(0.5 * math.sin(twinkle_phase + i))
            pygame.draw.circle(self.screen, star_color, (star_x, star_y), star_size)
    
    def draw_background(self):
        if self.is_night:
            self.screen.fill(self.NIGHT_SKY)
            self.draw_stars()
            
            pygame.draw.circle(self.screen, self.MOON_COLOR, (self.celestial_x, self.celestial_y), self.celestial_radius)
            pygame.draw.circle(self.screen, (220, 220, 200), (self.celestial_x, self.celestial_y), self.celestial_radius - 8)
            
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x - 8, self.celestial_y - 5), 4)
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x + 6, self.celestial_y + 8), 3)
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x + 3, self.celestial_y - 10), 2)
            
            cloud_positions = [(150, 100), (400, 80), (600, 120)]
            for cloud_x, cloud_y in cloud_positions:
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x, cloud_y), 25)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x + 20, cloud_y), 20)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x - 20, cloud_y), 20)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x + 10, cloud_y - 15), 18)
                pygame.draw.circle(self.screen, self.NIGHT_CLOUD, (cloud_x - 10, cloud_y - 15), 18)
        else:
            self.screen.fill(self.LIGHT_BLUE)
            
            pygame.draw.circle(self.screen, self.YELLOW, (self.celestial_x, self.celestial_y), self.celestial_radius)
            pygame.draw.circle(self.screen, (255, 255, 150), (self.celestial_x, self.celestial_y), 25)
            
            for i in range(8):
                angle = i * math.pi / 4
                ray_start_x = self.celestial_x + 45 * math.cos(angle)
                ray_start_y = self.celestial_y + 45 * math.sin(angle)
                ray_end_x = self.celestial_x + 60 * math.cos(angle)
                ray_end_y = self.celestial_y + 60 * math.sin(angle)
                pygame.draw.line(self.screen, self.YELLOW, 
                               (ray_start_x, ray_start_y), (ray_end_x, ray_end_y), 3)
            
            cloud_positions = [(150, 100), (400, 80), (600, 120)]
            for cloud_x, cloud_y in cloud_positions:
                pygame.draw.circle(self.screen, self.WHITE, (cloud_x, cloud_y), 25)
                pygame.draw.circle(self.screen, self.WHITE, (cloud_x + 20, cloud_y), 20)
                pygame.draw.circle(self.screen, self.WHITE, (cloud_x - 20, cloud_y), 20)
                pygame.draw.circle(self.screen, self.WHITE, (cloud_x + 10, cloud_y - 15), 18)
                pygame.draw.circle(self.screen, self.WHITE, (cloud_x - 10, cloud_y - 15), 18)
    
    def draw_ground(self):
        underground_rect = pygame.Rect(0, self.ground_y, self.width, self.height - self.ground_y)
        pygame.draw.rect(self.screen, self.BROWN, underground_rect)
        
        track_color = (100, 100, 100) if self.is_night else self.DARK_GRAY
        pygame.draw.line(self.screen, track_color, 
                        (0, self.ground_y), 
                        (self.width, self.ground_y), 4)
        
        marking_color = (200, 200, 200) if self.is_night else self.WHITE
        for x in range(0, self.width, 100):
            pygame.draw.line(self.screen, marking_color, 
                           (x, self.ground_y - 5), (x, self.ground_y + 5), 2)
            
            if x != self.width // 2:
                distance = (x - self.width // 2) / self.scale
                font = pygame.font.Font(None, 24)
                text = font.render(f"{distance:.0f}m", True, marking_color)
                text_rect = text.get_rect()
                text_rect.centerx = x
                text_rect.y = self.ground_y + 10
                self.screen.blit(text, text_rect)
        
        center_x = self.width // 2
        center_color = (255, 255, 100) if self.is_night else (255, 255, 0)
        pygame.draw.line(self.screen, center_color, 
                        (center_x, self.ground_y - 8), (center_x, self.ground_y + 8), 3)
        
        grass_y = self.ground_y - 15
        grass_color = self.NIGHT_GRASS if self.is_night else self.DARK_GREEN
        grass_tip_color = (0, 120, 0) if self.is_night else (50, 200, 50)
        
        for x in range(0, self.width, 8):
            blade_height = 10 + (hash(x) % 8)
            pygame.draw.line(self.screen, grass_color, 
                           (x, grass_y), (x, grass_y + blade_height), 2)
            if blade_height > 12:
                pygame.draw.line(self.screen, grass_tip_color, 
                               (x, grass_y), (x, grass_y + 4), 1)
    
    def draw_target_slider(self):
        track_color = (80, 80, 80) if self.is_night else (60, 60, 60)
        track_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height)
        pygame.draw.rect(self.screen, track_color, track_rect)
        pygame.draw.rect(self.screen, self.BLACK, track_rect, 2)
        
        marking_color = (200, 200, 200) if self.is_night else self.WHITE
        font = pygame.font.Font(None, 20)
        
        for pos in np.arange(self.slider_min_pos, self.slider_max_pos + 0.5, 0.5):
            normalized = (pos - self.slider_min_pos) / (self.slider_max_pos - self.slider_min_pos)
            mark_x = self.slider_x + normalized * self.slider_width
            
            pygame.draw.line(self.screen, marking_color, 
                           (mark_x, self.slider_y - 5), (mark_x, self.slider_y + self.slider_height + 5), 1)
            
            if abs(pos) < 0.01:
                label_text = "0"
                label_color = (255, 255, 0) if self.is_night else (255, 0, 0)
            else:
                label_text = f"{pos:.1f}"
                label_color = marking_color
            
            label = font.render(label_text, True, label_color)
            label_rect = label.get_rect()
            label_rect.centerx = mark_x
            label_rect.y = self.slider_y + self.slider_height + 8
            self.screen.blit(label, label_rect)
        
        target_screen_x = self.world_to_screen(self.target_position)
        if 0 <= target_screen_x <= self.width:
            target_color = (255, 100, 100) if self.is_night else (255, 0, 0)
            pygame.draw.line(self.screen, target_color,
                           (target_screen_x, self.ground_y - 15),
                           (target_screen_x, self.ground_y + 5), 4)
            
            triangle_points = [
                (target_screen_x, self.ground_y - 25),
                (target_screen_x - 8, self.ground_y - 15),
                (target_screen_x + 8, self.ground_y - 15)
            ]
            pygame.draw.polygon(self.screen, target_color, triangle_points)
            pygame.draw.polygon(self.screen, self.BLACK, triangle_points, 2)
            
            target_font = pygame.font.Font(None, 24)
            target_text = target_font.render(f"Target: {self.target_position:.2f}m", True, target_color)
            target_rect = target_text.get_rect()
            target_rect.centerx = target_screen_x
            target_rect.y = self.ground_y - 50
            
            bg_rect = target_rect.copy()
            bg_rect.inflate(10, 4)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(200)
            bg_color = (0, 0, 50) if self.is_night else (0, 0, 0)
            bg_surface.fill(bg_color)
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(target_text, target_rect)
        
        knob_x = self.get_slider_knob_x()
        knob_y = self.slider_y + self.slider_height // 2
        
        shadow_color = (30, 30, 30) if self.is_night else (100, 100, 100)
        pygame.draw.circle(self.screen, shadow_color, (knob_x + 2, knob_y + 2), self.slider_knob_radius)
        
        knob_color = (150, 200, 255) if self.is_night else (100, 150, 255)
        pygame.draw.circle(self.screen, knob_color, (knob_x, knob_y), self.slider_knob_radius)
        pygame.draw.circle(self.screen, self.BLACK, (knob_x, knob_y), self.slider_knob_radius, 2)
        
        highlight_color = (200, 220, 255) if self.is_night else (150, 200, 255)
        pygame.draw.circle(self.screen, highlight_color, (knob_x - 3, knob_y - 3), 4)
        
        title_font = pygame.font.Font(None, 28)
        title_color = (200, 200, 255) if self.is_night else self.BLACK
        title_text = title_font.render("Target Position (meters)", True, title_color)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.slider_x + self.slider_width // 2
        title_rect.y = self.slider_y - 30
        self.screen.blit(title_text, title_rect)
    
    def draw_trajectory(self):
        if self.show_trajectory and len(self.position_history) > 1:
            trail_color = (255, 255, 100) if self.is_night else (255, 0, 0)
            points = []
            for i, pos in enumerate(self.position_history):
                screen_x = self.world_to_screen(pos)
                if 0 <= screen_x <= self.width:
                    points.append((screen_x, self.ground_y - 20))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, trail_color, False, points, 2)
    
    def draw_info(self, current_time, cart_pos, pole_angle, cart_velocity=None, pole_velocity=None):
        info_height = 200 if cart_velocity is not None else 160
        info_surface = pygame.Surface((350, info_height))
        info_surface.set_alpha(200)
        bg_color = (0, 0, 50) if self.is_night else (0, 0, 0)
        info_surface.fill(bg_color)
        self.screen.blit(info_surface, (5, 5))
        
        font = pygame.font.Font(None, 36)
        text_color = (200, 200, 255) if self.is_night else self.WHITE
        
        y_offset = 10
        
        time_text = font.render(f"Time: {current_time:.2f}s", True, text_color)
        self.screen.blit(time_text, (10, y_offset))
        y_offset += 40
        
        pos_text = font.render(f"Cart Position: {cart_pos:.3f}m", True, text_color)
        self.screen.blit(pos_text, (10, y_offset))
        y_offset += 40
        
        angle_deg = math.degrees(pole_angle)
        angle_text = font.render(f"Pole Angle: {angle_deg:.1f}°", True, text_color)
        self.screen.blit(angle_text, (10, y_offset))
        y_offset += 40
        
        if cart_velocity is not None:
            vel_text = font.render(f"Cart Velocity: {cart_velocity:.3f}m/s", True, text_color)
            self.screen.blit(vel_text, (10, y_offset))
            y_offset += 40
        
        if pole_velocity is not None:
            pole_vel_deg = math.degrees(pole_velocity)
            pole_vel_text = font.render(f"Pole Velocity: {pole_vel_deg:.1f}°/s", True, text_color)
            self.screen.blit(pole_vel_text, (10, y_offset))
            y_offset += 40
        
        mode_text = "Night Mode" if self.is_night else "Day Mode"
        mode_surface = font.render(f"Mode: {mode_text}", True, text_color)
        self.screen.blit(mode_surface, (10, y_offset))
        
        inst_surface = pygame.Surface((800, 30))
        inst_surface.set_alpha(200)
        inst_surface.fill(bg_color)
        self.screen.blit(inst_surface, (5, self.height - 35))
        
        inst_text = font.render("T: toggle trajectory | Click/drag slider: set target | Click Sun/Moon: toggle day/night | ESC: quit", True, text_color)
        self.screen.blit(inst_text, (10, self.height - 30))
    
    def update(self, cart_position, pole_angle, cart_velocity=None, pole_velocity=None, force_redraw=True):
        if not self.handle_events():
            return False
        
        self.position_history.append(cart_position)
        
        current_time = time.time() - self.start_time
        
        self.draw_background()
        self.draw_ground()
        self.draw_target_slider()
        self.draw_trajectory()
        
        cart_screen_x, cart_screen_y = self.draw_cart(cart_position)
        self.draw_pole(cart_screen_x, cart_screen_y, pole_angle)
        
        self.draw_info(current_time, cart_position, pole_angle, cart_velocity, pole_velocity)
        
        if force_redraw:
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        self.frame_count += 1
        return True
    
    def get_target_position(self):
        return self.target_position
    
    def set_target_position(self, position):
        self.target_position = max(self.slider_min_pos, min(self.slider_max_pos, position))
    
    def close(self):
        pygame.quit()

# For backward compatibility
# CartPoleVisualizer = RealtimeCartPoleVisualizer