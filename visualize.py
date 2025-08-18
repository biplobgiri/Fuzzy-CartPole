import pygame
import numpy as np
import math
import time
import os
from collections import deque

class RealtimeCartPoleVisualizer:
    def __init__(self, width=800, height=600, pole_length_meters=2.0, cart_width_meters=1.0, cart_height_meters=0.5, background_path=None):
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
        self.ORANGE = (255, 165, 0)
        
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
        self.pole_width = 15
        
        self.ground_y = height - 100
        
        # Animation settings
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Load background images (including ground)
        self.background_images = self.load_background_images(background_path)
        
        # Sun/Moon settings
        self.celestial_x = self.width - 100
        self.celestial_y = 120
        self.celestial_radius = 35
        
        # Stars for night mode
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
        
        # Target position slider
        self.slider_min_pos = -3.0
        self.slider_max_pos = 3.0
        self.target_position = 0.0
        self.slider_dragging = False
        self.slider_knob_radius = 15
        
        # Calculate slider bounds
        self.slider_left_x = self.world_to_screen(self.slider_min_pos)
        self.slider_right_x = self.world_to_screen(self.slider_max_pos)
        
        self.slider_x = self.slider_left_x
        self.slider_y = self.ground_y + 35
        self.slider_width = self.slider_right_x - self.slider_left_x
        self.slider_height = 20
        
        # Top tabs for state variables
        self.tab_height = 80
        self.tab_font = pygame.font.Font(None, 24)
        self.tab_title_font = pygame.font.Font(None, 20)
    
    def load_background_images(self, background_path):
        """Load and scale background images including ground"""
        images = {
            'sky': None,
            'mountains': None,
            'trees_back': None,
            'trees_front': None,
            'ground': None  # New ground image layer
        }
        
        if background_path is None:
            # Use default path structure
            base_path = os.path.join(os.path.dirname(__file__), "Images", "background")
        else:
            base_path = background_path
        
        try:
            # Load each background layer
            sky_path = os.path.join(base_path, "sky_cloud.png")
            mountain_path = os.path.join(base_path, "mountain.png")
            trees_back_path = os.path.join(base_path, "pine1.png")
            trees_front_path = os.path.join(base_path, "pine2.png")
            ground_path = os.path.join(base_path, "ground.png")  # New ground image
            
            if os.path.exists(sky_path):
                images['sky'] = pygame.image.load(sky_path)
               
            
            if os.path.exists(mountain_path):
                images['mountains'] = pygame.image.load(mountain_path)
                original_size = images['mountains'].get_size()
                scale_factor = self.width / original_size[0]
                new_height = int(original_size[1] * scale_factor)
                images['mountains'] = pygame.transform.scale(images['mountains'], (self.width, new_height))
            
            if os.path.exists(trees_back_path):
                images['trees_back'] = pygame.image.load(trees_back_path)
                original_size = images['trees_back'].get_size()
                scale_factor = self.width / original_size[0]
                new_height = int(original_size[1] * scale_factor)
                images['trees_back'] = pygame.transform.scale(images['trees_back'], (self.width, new_height))
            
            if os.path.exists(trees_front_path):
                images['trees_front'] = pygame.image.load(trees_front_path)
                original_size = images['trees_front'].get_size()
                scale_factor = self.width / original_size[0]
                new_height = int(original_size[1] * scale_factor)
                images['trees_front'] = pygame.transform.scale(images['trees_front'], (self.width, new_height))
            
            # Load ground image
            if os.path.exists(ground_path):
                images['ground'] = pygame.image.load(ground_path)
                ground_height = self.height - self.ground_y + 50  # Extend below the ground line
                images['ground'] = pygame.transform.scale(images['ground'], (self.width, ground_height))
            else:
                print(f"Ground image not found at: {ground_path}")
                print("Available alternative names to try: terrain.png, soil.png, grass.png, earth.png")
                
        except pygame.error as e:
            print(f"Error loading background images: {e}")
            print("Falling back to programmatic backgrounds")
        
        return images
    
    def should_quit(self):
        return self.should_close
    
    def world_to_screen(self, x_pos):
        screen_x = self.width // 2 + x_pos * self.scale
        return screen_x
    
    def is_point_in_circle(self, point_x, point_y, circle_x, circle_y, radius):
        distance = math.sqrt((point_x - circle_x)**2 + (point_y - circle_y)**2)
        return distance <= radius
    
    def get_slider_knob_x(self):
        return self.world_to_screen(self.target_position)
    
    def set_target_from_mouse_x(self, mouse_x):
        target_world_pos = (mouse_x - self.width // 2) / self.scale
        self.target_position = max(self.slider_min_pos, min(self.slider_max_pos, target_world_pos))
    
    def is_point_in_slider(self, mouse_x, mouse_y):
        knob_x = self.get_slider_knob_x()
        knob_y = self.slider_y + self.slider_height // 2
        return (abs(mouse_x - knob_x) <= self.slider_knob_radius and 
                abs(mouse_y - knob_y) <= self.slider_knob_radius)
    
    def is_mouse_on_track(self, mouse_x, mouse_y):
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
            # Night mode - use darker overlay
            if self.background_images['sky']:
                # Create a darkened version of the sky
                night_sky = self.background_images['sky'].copy()
                dark_overlay = pygame.Surface((self.width, self.height))
                dark_overlay.fill((0, 0, 50))
                dark_overlay.set_alpha(180)
                night_sky.blit(dark_overlay, (0, 0))
                self.screen.blit(night_sky, (0, 0))
            else:
                self.screen.fill(self.NIGHT_SKY)
            
            # Draw stars
            self.draw_stars()
            
            # Draw background layers with night tint
            if self.background_images['mountains']:
                night_mountains = self.background_images['mountains'].copy()
                mountain_y = 240
                self.screen.blit(night_mountains, (0, mountain_y))
            
            if self.background_images['trees_back']:
                night_trees_back = self.background_images['trees_back'].copy()
                trees_back_y = 280
                self.screen.blit(night_trees_back, (0, trees_back_y))
            
            # Draw moon
            pygame.draw.circle(self.screen, self.MOON_COLOR, (self.celestial_x, self.celestial_y), self.celestial_radius)
            pygame.draw.circle(self.screen, (220, 220, 200), (self.celestial_x, self.celestial_y), self.celestial_radius - 8)
            
            # Moon craters
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x - 8, self.celestial_y - 5), 4)
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x + 6, self.celestial_y + 8), 3)
            pygame.draw.circle(self.screen, (200, 200, 180), (self.celestial_x + 3, self.celestial_y - 10), 2)
            
        else:
            # Day mode
            if self.background_images['sky']:
                self.screen.blit(self.background_images['sky'], (0, 0))
            else:
                self.screen.fill(self.LIGHT_BLUE)
            
            # Draw background layers
            if self.background_images['mountains']:
                mountain_y = 240
                self.screen.blit(self.background_images['mountains'], (0, mountain_y))
            
            if self.background_images['trees_back']:
                trees_back_y = 280
                self.screen.blit(self.background_images['trees_back'], (0, trees_back_y))
            
            # Draw sun
            pygame.draw.circle(self.screen, self.YELLOW, (self.celestial_x, self.celestial_y), self.celestial_radius)
            pygame.draw.circle(self.screen, (255, 255, 150), (self.celestial_x, self.celestial_y), 25)
            
            # Sun rays
            for i in range(8):
                angle = i * math.pi / 4
                ray_start_x = self.celestial_x + 45 * math.cos(angle)
                ray_start_y = self.celestial_y + 45 * math.sin(angle)
                ray_end_x = self.celestial_x + 60 * math.cos(angle)
                ray_end_y = self.celestial_y + 60 * math.sin(angle)
                pygame.draw.line(self.screen, self.YELLOW, 
                               (ray_start_x, ray_start_y), (ray_end_x, ray_end_y), 3)
        
        # Draw front trees last (closest to viewer)
        if self.background_images['trees_front']:
            if self.is_night:
                night_trees_front = self.background_images['trees_front'].copy()
                trees_front_y = self.ground_y - night_trees_front.get_height() + 40
                self.screen.blit(night_trees_front, (0, trees_front_y))
            else:
                trees_front_y = self.ground_y - self.background_images['trees_front'].get_height() + 40
                self.screen.blit(self.background_images['trees_front'], (0, trees_front_y))
    
    def draw_cart(self, x_pos):
        screen_x = self.world_to_screen(x_pos)
        cart_color = (255, 0, 255)  # Bright magenta/purple
        
        cart_rect = pygame.Rect(
            screen_x - self.cart_width // 2,
            self.ground_y - self.cart_height,
            self.cart_width,
            self.cart_height
        )
        pygame.draw.rect(self.screen, cart_color, cart_rect)
        pygame.draw.rect(self.screen, self.BLACK, cart_rect, 2)
        
        return screen_x, self.ground_y - self.cart_height // 2
    
    def draw_pole(self, cart_x, cart_y, angle):
        pole_end_x = cart_x + self.pole_length * math.sin(angle)
        pole_end_y = cart_y - self.pole_length * math.cos(angle)
        
        # Draw pole as a thick yellow line
        pole_color = (255, 255, 0)  # Bright yellow
        pygame.draw.line(self.screen, pole_color,
                        (cart_x, cart_y), (pole_end_x, pole_end_y), 
                        self.pole_width)
        
        # Draw black outline for the pole
        pygame.draw.line(self.screen, self.BLACK,
                        (cart_x, cart_y), (pole_end_x, pole_end_y), 2)
        
        # Draw joint at cart connection point
        joint_radius = 8
        pygame.draw.circle(self.screen, self.BLACK, (int(cart_x), int(cart_y)), joint_radius)
        pygame.draw.circle(self.screen, self.GRAY, (int(cart_x), int(cart_y)), joint_radius - 2)
    
    def draw_ground(self):
        # Draw ground image if available, otherwise fallback to simple ground
        if self.background_images['ground']:
            ground_y_pos = self.ground_y - 20  # Position ground image slightly above the ground line
            
            # Apply night mode tint if needed
            if self.is_night:
                night_ground = self.background_images['ground'].copy()
                dark_overlay = pygame.Surface(night_ground.get_size())
                dark_overlay.fill((0, 0, 30))
                dark_overlay.set_alpha(120)
                night_ground.blit(dark_overlay, (0, 0))
                self.screen.blit(night_ground, (0, ground_y_pos))
            else:
                self.screen.blit(self.background_images['ground'], (0, ground_y_pos))
        else:
            # Fallback to programmatic ground
            # Draw ground with grass texture
            ground_color = self.NIGHT_GRASS if self.is_night else self.DARK_GREEN
            ground_rect = pygame.Rect(0, self.ground_y, self.width, self.height - self.ground_y)
            pygame.draw.rect(self.screen, ground_color, ground_rect)
            
            # Add some underground brown layer
            underground_color = (80, 40, 20) if self.is_night else self.BROWN
            underground_rect = pygame.Rect(0, self.ground_y + 30, self.width, self.height - self.ground_y - 30)
            pygame.draw.rect(self.screen, underground_color, underground_rect)
            
            # Add some texture to the ground
            for i in range(0, self.width, 20):
                grass_height = np.random.randint(5, 15)
                grass_color = (0, max(0, 100 + np.random.randint(-20, 20)), 0) if self.is_night else (0, max(0, 150 + np.random.randint(-30, 30)), 0)
                pygame.draw.line(self.screen, grass_color,
                               (i, self.ground_y), (i, self.ground_y - grass_height), 2)
        
        # Always draw the track line on top of ground
        track_color = (100, 100, 100) if self.is_night else self.DARK_GRAY
        pygame.draw.line(self.screen, track_color, 
                        (0, self.ground_y), 
                        (self.width, self.ground_y), 4)
        
        # Draw center reference line
        center_x = self.width // 2
        center_color = (255, 255, 100) if self.is_night else (255, 255, 0)
        pygame.draw.line(self.screen, center_color, 
                        (center_x, self.ground_y - 8), (center_x, self.ground_y + 8), 3)
    
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
                label_color = self.ORANGE
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
            target_color = self.ORANGE
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
            target_rect.y = self.ground_y + 10
            
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
    
    def draw_top_tabs(self, current_time, cart_pos, pole_angle, cart_velocity=None, pole_velocity=None):
        # Background for tabs
        tab_bg_color = (0, 0, 50) if self.is_night else (240, 240, 240)
        tab_surface = pygame.Surface((self.width, self.tab_height))
        tab_surface.set_alpha(220)
        tab_surface.fill(tab_bg_color)
        self.screen.blit(tab_surface, (0, 0))
        
        # Text colors
        text_color = (200, 200, 255) if self.is_night else (50, 50, 50)
        label_color = (150, 150, 200) if self.is_night else (100, 100, 100)
        
        # Calculate tab positions
        num_tabs = 5 if cart_velocity is not None and pole_velocity is not None else 3
        tab_width = self.width // num_tabs
        
        # Tab data
        tabs = [
            ("Time", f"{current_time:.2f}s"),
            ("Position", f"{cart_pos:.3f}m"),
            ("Angle", f"{math.degrees(pole_angle):.1f}°"),
        ]
        
        if cart_velocity is not None:
            tabs.append(("Cart Vel", f"{cart_velocity:.3f}m/s"))
        
        if pole_velocity is not None:
            tabs.append(("Pole Vel", f"{math.degrees(pole_velocity):.1f}°/s"))
        
        # Draw tabs
        for i, (label, value) in enumerate(tabs):
            x_pos = i * tab_width
            
            # Tab border
            tab_rect = pygame.Rect(x_pos, 0, tab_width, self.tab_height)
            pygame.draw.rect(self.screen, text_color, tab_rect, 1)
            
            # Label
            label_surface = self.tab_title_font.render(label, True, label_color)
            label_rect = label_surface.get_rect()
            label_rect.centerx = x_pos + tab_width // 2
            label_rect.y = 10
            self.screen.blit(label_surface, label_rect)
            
            # Value
            value_surface = self.tab_font.render(value, True, text_color)
            value_rect = value_surface.get_rect()
            value_rect.centerx = x_pos + tab_width // 2
            value_rect.y = 35
            self.screen.blit(value_surface, value_rect)
    
    def update(self, cart_position, pole_angle, cart_velocity=None, pole_velocity=None, force_redraw=True):
        if not self.handle_events():
            return False
        
        self.position_history.append(cart_position)
        
        current_time = time.time() - self.start_time
        
        self.draw_background()
        self.draw_ground()  # This now includes ground image support
        self.draw_target_slider()
        self.draw_trajectory()
        
        cart_screen_x, cart_screen_y = self.draw_cart(cart_position)
        self.draw_pole(cart_screen_x, cart_screen_y, pole_angle)
        
        # Draw top tabs
        self.draw_top_tabs(current_time, cart_position, pole_angle, cart_velocity, pole_velocity)
        
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

