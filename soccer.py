import pygame
import sys
import random
import math
import os

# ------------------------------------------------
# SETUP
# ------------------------------------------------
pygame.init()
SCREEN_W, SCREEN_H = 1000, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Penalty Shootout 3D")

clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("Arial", 32)
title_font = pygame.font.SysFont("Arial", 24, bold=True)  # For better looking instructions

# ------------------------------------------------
# ASSET LOADING WITH SIMPLE BACKGROUND REMOVAL
# ------------------------------------------------
def load_image(path, scale=None, colorkey=None):
    """Load image with optional scaling and background removal"""
    try:
        # Check if file exists
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return None
            
        # Load image
        img = pygame.image.load(path)
        
        # Convert to appropriate format
        if path.lower().endswith('.png'):
            img = img.convert_alpha()
        else:
            img = img.convert()
            if colorkey is not None:
                # Set colorkey for background removal
                if colorkey == -1:
                    colorkey = img.get_at((0, 0))
                img.set_colorkey(colorkey)
        
        if scale:
            img = pygame.transform.scale(img, scale)
            
        return img
        
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def load_image_with_background_removal(path, scale=None):
    """Load image and try to remove white background"""
    try:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return None
            
        img = pygame.image.load(path)
        
        # Convert to surface with alpha
        img = img.convert_alpha()
        
        # If image doesn't have alpha channel, create one and remove white background
        if img.get_alpha() is None:
            # Create a new surface with alpha
            img_with_alpha = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            
            # Copy pixels, making white pixels transparent
            for x in range(img.get_width()):
                for y in range(img.get_height()):
                    color = img.get_at((x, y))
                    # If pixel is white or near white, make it transparent
                    if color[0] > 200 and color[1] > 200 and color[2] > 200:
                        img_with_alpha.set_at((x, y), (255, 255, 255, 0))
                    else:
                        img_with_alpha.set_at((x, y), (*color[:3], 255))
            img = img_with_alpha
        
        if scale:
            img = pygame.transform.scale(img, scale)
            
        return img
        
    except Exception as e:
        print(f"Error loading {path} with background removal: {e}")
        return None

def create_soccer_ball(size):
    """Create a nice soccer ball as fallback"""
    width, height = size
    ball_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 2 - 2
    
    # Main white circle
    pygame.draw.circle(ball_surface, (255, 255, 255), (center_x, center_y), radius)
    
    # Black outline
    pygame.draw.circle(ball_surface, (0, 0, 0), (center_x, center_y), radius, 2)
    
    # Draw soccer ball pattern
    for i in range(5):
        angle = math.radians(i * 72)
        x = center_x + int(radius * 0.6 * math.cos(angle))
        y = center_y + int(radius * 0.6 * math.sin(angle))
        
        # Black pentagon
        pygame.draw.circle(ball_surface, (0, 0, 0), (x, y), radius // 3)
        
        # White inner circle
        pygame.draw.circle(ball_surface, (255, 255, 255), (x, y), radius // 6)
    
    # Center black circle
    pygame.draw.circle(ball_surface, (0, 0, 0), (center_x, center_y), radius // 5)
    
    return ball_surface

def create_fallback_goal(size):
    """Create a fallback goal with net"""
    width, height = size
    goal_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Goal posts (white)
    pygame.draw.rect(goal_surface, (255, 255, 255), (0, 0, 20, height))  # Left post
    pygame.draw.rect(goal_surface, (255, 255, 255), (width - 20, 0, 20, height))  # Right post
    pygame.draw.rect(goal_surface, (255, 255, 255), (0, 0, width, 20))  # Top bar
    
    # Semi-transparent net area
    net_area = pygame.Surface((width - 40, height - 40), pygame.SRCALPHA)
    net_color = (255, 255, 255, 80)  # White with low alpha
    
    # Draw net grid
    grid_size = 20
    for x in range(0, net_area.get_width(), grid_size):
        pygame.draw.line(net_area, net_color, (x, 0), (x, net_area.get_height()), 1)
    for y in range(0, net_area.get_height(), grid_size):
        pygame.draw.line(net_area, net_color, (0, y), (net_area.get_width(), y), 1)
    
    goal_surface.blit(net_area, (20, 20))
    
    return goal_surface

def create_fallback_keeper(size, holding_ball=False, crying=False):
    """Create a fallback goalkeeper"""
    width, height = size
    keeper_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Body (red jersey)
    pygame.draw.rect(keeper_surface, (200, 0, 0), (0, 0, width, height))
    pygame.draw.rect(keeper_surface, (0, 0, 0), (0, 0, width, height), 3)
    
    # Head
    pygame.draw.circle(keeper_surface, (255, 200, 150), (width // 2, height // 4), 18)
    
    # Jersey
    pygame.draw.rect(keeper_surface, (255, 255, 255), (25, 60, 50, 45))
    
    # Arms
    pygame.draw.rect(keeper_surface, (255, 200, 150), (10, 70, 15, 30))
    pygame.draw.rect(keeper_surface, (255, 200, 150), (75, 70, 15, 30))
    
    if holding_ball:
        # Ball in hands
        pygame.draw.circle(keeper_surface, (255, 255, 255), (width // 2, 80), 15)
        pygame.draw.circle(keeper_surface, (0, 0, 0), (width // 2, 80), 15, 2)
    elif crying:
        # Crying face
        # Eyes
        pygame.draw.ellipse(keeper_surface, (0, 0, 0), (35, 28, 10, 5))
        pygame.draw.ellipse(keeper_surface, (0, 0, 0), (55, 28, 10, 5))
        # Sad mouth
        pygame.draw.arc(keeper_surface, (0, 0, 0), (40, 45, 20, 10), math.pi, 2*math.pi, 2)
        # Tears
        pygame.draw.circle(keeper_surface, (100, 150, 255), (40, 50), 3)
        pygame.draw.circle(keeper_surface, (100, 150, 255), (60, 50), 3)
    
    return keeper_surface

def create_fallback_shooter(size, shooting=False, celebrating=False):
    """Create a fallback shooter"""
    width, height = size
    shooter_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    # Body (green)
    color = (0, 150, 0)
    if shooting:
        color = (0, 200, 0)
    elif celebrating:
        color = (0, 255, 0)
    
    pygame.draw.rect(shooter_surface, color, (0, 0, width, height))
    pygame.draw.rect(shooter_surface, (0, 0, 0), (0, 0, width, height), 3)
    
    # Head
    pygame.draw.circle(shooter_surface, (255, 200, 150), (width // 2, 50), 25)
    
    # Jersey (yellow)
    pygame.draw.rect(shooter_surface, (255, 255, 0), (35, 80, 70, 60))
    
    if shooting:
        # Kicking leg
        pygame.draw.line(shooter_surface, (0, 0, 0), (70, 140), (100, 170), 3)
    elif celebrating:
        # Raised arms
        pygame.draw.line(shooter_surface, (255, 200, 150), (50, 80), (30, 40), 8)
        pygame.draw.line(shooter_surface, (255, 200, 150), (90, 80), (110, 40), 8)
    
    return shooter_surface

BASE_PATH = os.path.join(os.path.dirname(__file__), "images")

GOAL_PATH = os.path.join(BASE_PATH, "goal.png")
GRASS_PATH = os.path.join(BASE_PATH, "grass.png")
FANS_PATH  = os.path.join(BASE_PATH, "fans.jpg")
BALL_PATH  = os.path.join(BASE_PATH, "ball.png")

SHOOTER_STAND_PATH = os.path.join(BASE_PATH, "shooter_stand.png")
SHOOTER_SHOOT_PATH = os.path.join(BASE_PATH, "shooter_time.png")
SHOOTER_SUI_PATH   = os.path.join(BASE_PATH, "shooter_sui.png")

KEEPER_STAND_PATH = os.path.join(BASE_PATH, "keeper_stand.png")
KEEPER_HOLDING_BALL_PATH = os.path.join(BASE_PATH, "keeper_holding_ball.png")
KEEPER_CRY_PATH = os.path.join(BASE_PATH, "keeper_cry.gif")

# Load images - using simple loading without PIL/rembg
fans_img_orig = load_image(FANS_PATH, (SCREEN_W, 300))
grass_img_orig = load_image(GRASS_PATH, (SCREEN_W, 300))

# Try to load goal with simple background removal
goal_img_orig = load_image_with_background_removal(GOAL_PATH, (500, 250))
if not goal_img_orig:
    print("Goal background removal failed, trying regular load...")
    goal_img_orig = load_image(GOAL_PATH, (500, 250), colorkey=(255, 255, 255))
    if not goal_img_orig:
        print("Creating fallback goal...")
        goal_img_orig = create_fallback_goal((500, 250))

# CHANGED: Bigger ball size
BALL_SIZE = (80, 80)

# Load ball with simple background removal
ball_img_orig = load_image_with_background_removal(BALL_PATH, BALL_SIZE)
if not ball_img_orig:
    print("Ball background removal failed, trying regular load...")
    ball_img_orig = load_image(BALL_PATH, BALL_SIZE, colorkey=(255, 255, 255))
    if not ball_img_orig:
        print("Creating fallback soccer ball...")
        ball_img_orig = create_soccer_ball(BALL_SIZE)

# LOAD SHOOTER IMAGES
shooter_stand_img_orig = load_image_with_background_removal(SHOOTER_STAND_PATH, (140, 180))
if not shooter_stand_img_orig:
    shooter_stand_img_orig = load_image(SHOOTER_STAND_PATH, (140, 180), colorkey=(255, 255, 255))
    if not shooter_stand_img_orig:
        shooter_stand_img_orig = create_fallback_shooter((140, 180))

shooter_shoot_img_orig = load_image_with_background_removal(SHOOTER_SHOOT_PATH, (140, 180))
if not shooter_shoot_img_orig:
    shooter_shoot_img_orig = load_image(SHOOTER_SHOOT_PATH, (140, 180), colorkey=(255, 255, 255))
    if not shooter_shoot_img_orig:
        shooter_shoot_img_orig = create_fallback_shooter((140, 180), shooting=True)

shooter_sui_img_orig = load_image_with_background_removal(SHOOTER_SUI_PATH, (140, 180))
if not shooter_sui_img_orig:
    shooter_sui_img_orig = load_image(SHOOTER_SUI_PATH, (140, 180), colorkey=(255, 255, 255))
    if not shooter_sui_img_orig:
        shooter_sui_img_orig = create_fallback_shooter((140, 180), celebrating=True)

# LOAD KEEPER IMAGES
keeper_stand_img_orig = load_image_with_background_removal(KEEPER_STAND_PATH, (100, 130))
if not keeper_stand_img_orig:
    keeper_stand_img_orig = load_image(KEEPER_STAND_PATH, (100, 130), colorkey=(255, 255, 255))
    if not keeper_stand_img_orig:
        keeper_stand_img_orig = create_fallback_keeper((100, 130))

keeper_holding_ball_img_orig = load_image_with_background_removal(KEEPER_HOLDING_BALL_PATH, (100, 130))
if not keeper_holding_ball_img_orig:
    keeper_holding_ball_img_orig = load_image(KEEPER_HOLDING_BALL_PATH, (100, 130), colorkey=(255, 255, 255))
    if not keeper_holding_ball_img_orig:
        keeper_holding_ball_img_orig = create_fallback_keeper((100, 130), holding_ball=True)

# For GIF, we need to handle it differently
keeper_cry_img_orig = None
try:
    # Try to load the GIF as a static image (first frame)
    keeper_cry_img_orig = load_image(KEEPER_CRY_PATH, (100, 130))
    print("Loaded keeper_cry.gif as static image")
except:
    print("Could not load keeper_cry.gif, will use fallback")
    # Create fallback crying keeper
    keeper_cry_img_orig = create_fallback_keeper((100, 130), crying=True)

# Fallback surfaces
if not fans_img_orig:
    fans_img_orig = pygame.Surface((SCREEN_W, 300))
    fans_img_orig.fill((50, 50, 50))
if not grass_img_orig:
    grass_img_orig = pygame.Surface((SCREEN_W, 300))
    grass_img_orig.fill((0, 120, 0))

# ------------------------------------------------
# GAME STATE - ADJUSTED POSITIONS
# ------------------------------------------------
class GameState:
    def __init__(self):
        self.fullscreen = False
        self.screen_w, self.screen_h = SCREEN_W, SCREEN_H
        
        # Store original positions
        self.original_goal_pos = (SCREEN_W//2 - 250, 150)
        
        keeper_width = 100
        keeper_height = 130
        
        goal_bottom_y = self.original_goal_pos[1] + 250
        keeper_y = goal_bottom_y - keeper_height + 10
        keeper_x = SCREEN_W//2 - keeper_width//2
        
        player_width = 140
        player_x = SCREEN_W//2 - player_width//2 - 50
        player_y = SCREEN_H - 200
        
        ball_width = BALL_SIZE[0]
        ball_x = player_x + player_width - 40
        ball_y = player_y + player_width - 60
        
        self.original_positions = {
            'goal': self.original_goal_pos,
            'keeper': [keeper_x, keeper_y],
            'player': [player_x, player_y],
            'ball': [ball_x, ball_y]
        }
        
        # Scale factor for fullscreen
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # Current positions (will be scaled)
        self.goal_pos = list(self.original_positions['goal'])
        self.keeper_pos = list(self.original_positions['keeper'])
        self.player_pos = list(self.original_positions['player'])
        self.ball_pos = list(self.original_positions['ball'])
        
        self.ball_velocity = [0, 0]
        self.ball_in_air = False
        self.keeper_target_x = self.keeper_pos[0]
        
        self.score = 0
        self.total_shots = 0
        self.goal_scored = None
        self.key_pressed_once = set()
        self.shot_processed = False
        
        self.ball_stopped = False
        self.ready_for_next_shot = False
        
        self.keeper_saved = False
        self.ball_saved = False
        
        self.current_keeper_image = "stand"
        self.show_keeper_reaction = False
        
        self.current_shooter_image = "stand"
        self.shooting_direction = None
        self.ball_target_zone = None
        self.keeper_zone = None
        
        self.show_shooting_instructions = True  # NEW: Show shooting instructions
        
        # Scaled images
        self.scale_images()
        self.update_keeper_zone()
    
    def update_keeper_zone(self):
        """Update which zone the keeper is in"""
        keeper_center_x = self.keeper_pos[0] + self.keeper_stand_img.get_width() // 2
        goal_left = self.goal_pos[0] + self.goal_img.get_width() * 0.1
        goal_right = self.goal_pos[0] + self.goal_img.get_width() * 0.9
        goal_width = goal_right - goal_left
        
        keeper_relative_pos = (keeper_center_x - goal_left) / goal_width
        
        if keeper_relative_pos < 0.33:
            self.keeper_zone = "left"
        elif keeper_relative_pos > 0.66:
            self.keeper_zone = "right"
        else:
            self.keeper_zone = "middle"
    
    def scale_images(self):
        self.scale_x = self.screen_w / SCREEN_W
        self.scale_y = self.screen_h / SCREEN_H
        
        self.goal_img = pygame.transform.scale(goal_img_orig, 
                                              (int(500 * self.scale_x), 
                                               int(250 * self.scale_y)))
        
        self.ball_img = pygame.transform.scale(ball_img_orig,
                                              (int(BALL_SIZE[0] * self.scale_x),
                                               int(BALL_SIZE[1] * self.scale_y)))
        
        self.keeper_stand_img = pygame.transform.scale(keeper_stand_img_orig,
                                                      (int(100 * self.scale_x),
                                                       int(130 * self.scale_y)))
        self.keeper_holding_ball_img = pygame.transform.scale(keeper_holding_ball_img_orig,
                                                            (int(100 * self.scale_x),
                                                             int(130 * self.scale_y)))
        self.keeper_cry_img = pygame.transform.scale(keeper_cry_img_orig,
                                                    (int(100 * self.scale_x),
                                                     int(130 * self.scale_y)))
        
        self.shooter_stand_img = pygame.transform.scale(shooter_stand_img_orig,
                                                       (int(140 * self.scale_x),
                                                        int(180 * self.scale_y)))
        self.shooter_shoot_img = pygame.transform.scale(shooter_shoot_img_orig,
                                                       (int(140 * self.scale_x),
                                                        int(180 * self.scale_y)))
        self.shooter_sui_img = pygame.transform.scale(shooter_sui_img_orig,
                                                     (int(140 * self.scale_x),
                                                      int(180 * self.scale_y)))
        
        self.update_images()
        
        self.fans_img = pygame.transform.scale(fans_img_orig,
                                              (self.screen_w, int(300 * self.scale_y)))
        self.grass_img = pygame.transform.scale(grass_img_orig,
                                               (self.screen_w, int(300 * self.scale_y)))
        
        self.update_positions()
    
    def update_images(self):
        """Update which images to display based on game state"""
        if not self.shot_processed:
            self.current_keeper_image = "stand"
            self.show_keeper_reaction = False
        elif self.show_keeper_reaction:
            if self.keeper_saved:
                self.current_keeper_image = "holding"
            else:
                self.current_keeper_image = "cry"
        else:
            self.current_keeper_image = "stand"
        
        if not self.shot_processed and self.ball_in_air:
            self.current_shooter_image = "shoot"
        elif self.shot_processed and self.goal_scored == True:
            self.current_shooter_image = "sui"
        else:
            self.current_shooter_image = "stand"
    
    def get_keeper_image(self):
        if self.current_keeper_image == "stand":
            return self.keeper_stand_img
        elif self.current_keeper_image == "holding":
            return self.keeper_holding_ball_img
        elif self.current_keeper_image == "cry":
            return self.keeper_cry_img
        else:
            return self.keeper_stand_img
    
    def get_shooter_image(self):
        if self.current_shooter_image == "stand":
            return self.shooter_stand_img
        elif self.current_shooter_image == "shoot":
            return self.shooter_shoot_img
        elif self.current_shooter_image == "sui":
            return self.shooter_sui_img
        else:
            return self.shooter_stand_img
    
    def update_positions(self):
        self.goal_pos = [self.original_positions['goal'][0] * self.scale_x,
                         self.original_positions['goal'][1] * self.scale_y]
        
        self.keeper_pos = [self.original_positions['keeper'][0] * self.scale_x,
                           self.original_positions['keeper'][1] * self.scale_y]
        
        self.player_pos = [self.original_positions['player'][0] * self.scale_x,
                           self.original_positions['player'][1] * self.scale_y]
        
        self.ball_pos = [self.original_positions['ball'][0] * self.scale_x,
                         self.original_positions['ball'][1] * self.scale_y]
        
        if hasattr(self, 'keeper_target_x'):
            self.keeper_target_x = self.original_positions['keeper'][0] * self.scale_x
        
        self.update_keeper_zone()
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen_w, self.screen_h = pygame.display.get_desktop_sizes()[0]
            screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.FULLSCREEN)
        else:
            self.screen_w, self.screen_h = SCREEN_W, SCREEN_H
            screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        
        self.scale_images()
        return screen
    
    def reset_for_next_shot(self):
        """Reset the game state for the next shot"""
        self.ball_in_air = False
        self.ball_stopped = False
        self.ready_for_next_shot = False
        self.ball_velocity = [0, 0]
        self.shot_processed = False
        self.goal_scored = None
        self.ball_saved = False
        self.keeper_saved = False
        self.show_keeper_reaction = False
        self.shooting_direction = None
        self.ball_target_zone = None
        
        self.current_keeper_image = "stand"
        self.current_shooter_image = "stand"
        
        # Hide shooting instructions after first shot
        if self.total_shots > 0:
            self.show_shooting_instructions = False
        
        self.ball_pos = [self.original_positions['ball'][0] * self.scale_x,
                        self.original_positions['ball'][1] * self.scale_y]
        
        goal_left = self.goal_pos[0] + self.goal_img.get_width() * 0.1
        goal_right = self.goal_pos[0] + self.goal_img.get_width() * 0.9 - self.keeper_stand_img.get_width()
        choice = random.choice(["left", "center", "right"])
        if choice == "left":
            self.keeper_target_x = goal_left
        elif choice == "right":
            self.keeper_target_x = goal_right
        else:
            self.keeper_target_x = goal_left + (goal_right - goal_left) / 2
        
        self.update_keeper_zone()
    
    def update_all_positions_after_scale(self):
        self.update_positions()
        
        goal_left = self.goal_pos[0] + self.goal_img.get_width() * 0.1
        goal_right = self.goal_pos[0] + self.goal_img.get_width() * 0.9 - self.keeper_stand_img.get_width()
        
        keeper_rel_pos = (self.keeper_pos[0] - goal_left) / (goal_right - goal_left) if goal_right > goal_left else 0.5
        self.keeper_target_x = goal_left + keeper_rel_pos * (goal_right - goal_left)
        
        self.update_keeper_zone()

# Initialize game state
game = GameState()

# ------------------------------------------------
# SIMPLE SHOOTING FUNCTION
# ------------------------------------------------
def shoot_ball(direction):
    if game.ball_in_air or game.ball_stopped:
        return

    game.current_shooter_image = "shoot"
    game.shooting_direction = direction
    
    if "left" in direction:
        game.ball_target_zone = "left"
    elif "right" in direction:
        game.ball_target_zone = "right"
    else:
        game.ball_target_zone = "middle"

    speed = 12
    dx, dy = 0, 0
    
    goal_area = {
        "left": game.goal_pos[0] + game.goal_img.get_width() * 0.2,
        "right": game.goal_pos[0] + game.goal_img.get_width() * 0.8,
        "top": game.goal_pos[1] + game.goal_img.get_height() * 0.3,
        "bottom": game.goal_pos[1] + game.goal_img.get_height() * 0.7
    }

    ball_center_x = game.ball_pos[0] + game.ball_img.get_width() // 2
    ball_center_y = game.ball_pos[1] + game.ball_img.get_height() // 2

    if direction == "top-left":
        dx = goal_area["left"] - ball_center_x
        dy = goal_area["top"] - ball_center_y
    elif direction == "top-right":
        dx = goal_area["right"] - ball_center_x
        dy = goal_area["top"] - ball_center_y
    elif direction == "bottom-left":
        dx = goal_area["left"] - ball_center_x
        dy = goal_area["bottom"] - ball_center_y
    elif direction == "bottom-right":
        dx = goal_area["right"] - ball_center_x
        dy = goal_area["bottom"] - ball_center_y
    elif direction == "top":
        dx = (goal_area["left"] + goal_area["right"])//2 - ball_center_x
        dy = goal_area["top"] - ball_center_y
    elif direction == "bottom":
        dx = (goal_area["left"] + goal_area["right"])//2 - ball_center_x
        dy = goal_area["bottom"] - ball_center_y
    elif direction == "left":
        dx = goal_area["left"] - ball_center_x
        dy = (goal_area["top"] + goal_area["bottom"])//2 - ball_center_y
    elif direction == "right":
        dx = goal_area["right"] - ball_center_x
        dy = (goal_area["top"] + goal_area["bottom"])//2 - ball_center_y

    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    dx /= length
    dy /= length
    game.ball_velocity = [dx * speed, dy * speed]
    game.ball_in_air = True
    game.ball_stopped = False
    game.ready_for_next_shot = False
    game.ball_saved = False
    game.keeper_saved = False

# ------------------------------------------------
# KEEPER AI - SIMPLE MOVEMENT
# ------------------------------------------------
def update_keeper():
    game.update_images()
    
    goal_left = game.goal_pos[0] + game.goal_img.get_width() * 0.1
    goal_right = game.goal_pos[0] + game.goal_img.get_width() * 0.9 - game.keeper_stand_img.get_width()
    
    if not game.show_keeper_reaction and not game.ball_in_air and not game.ball_stopped:
        if random.random() < 0.01:
            choice = random.choice(["left", "center", "right"])
            if choice == "left":
                game.keeper_target_x = goal_left
            elif choice == "right":
                game.keeper_target_x = goal_right
            else:
                game.keeper_target_x = goal_left + (goal_right - goal_left) / 2

        if game.keeper_pos[0] < game.keeper_target_x:
            game.keeper_pos[0] = min(game.keeper_pos[0] + 5 * game.scale_x, game.keeper_target_x)
        elif game.keeper_pos[0] > game.keeper_target_x:
            game.keeper_pos[0] = max(game.keeper_pos[0] - 5 * game.scale_x, game.keeper_target_x)
        
        game.update_keeper_zone()

# ------------------------------------------------
# SIMPLE COLLISION DETECTION - FIXED VERSION
# ------------------------------------------------
def check_collisions():
    if not game.ball_in_air or game.ball_stopped or game.shot_processed:
        return
    
    ball_rect = pygame.Rect(game.ball_pos[0], game.ball_pos[1],
                           game.ball_img.get_width(), game.ball_img.get_height())
    
    goal_rect = pygame.Rect(
        game.goal_pos[0] + game.goal_img.get_width() * 0.1,
        game.goal_pos[1] + game.goal_img.get_height() * 0.1,
        game.goal_img.get_width() * 0.8,
        game.goal_img.get_height() * 0.8
    )
    
    if ball_rect.colliderect(goal_rect):
        if game.ball_target_zone == game.keeper_zone:
            game.goal_scored = False
            game.shot_processed = True
            game.ball_saved = True
            game.ball_in_air = False
            game.ball_stopped = True
            game.ready_for_next_shot = True
            game.ball_velocity = [0, 0]
            game.keeper_saved = True
            game.show_keeper_reaction = True
            
            keeper_center_x = game.keeper_pos[0] + game.keeper_stand_img.get_width() // 2
            keeper_center_y = game.keeper_pos[1] + game.keeper_stand_img.get_height() // 2
            game.ball_pos[0] = keeper_center_x - game.ball_img.get_width() // 2
            game.ball_pos[1] = keeper_center_y - game.ball_img.get_height() // 2
            return
        else:
            game.goal_scored = True
            game.score += 1
            game.shot_processed = True
            game.keeper_saved = False
            game.show_keeper_reaction = True
            game.ball_velocity = [game.ball_velocity[0] * 0.5, game.ball_velocity[1] * 0.5]
            return
    
    if (game.ball_pos[1] < -game.ball_img.get_height() or 
        game.ball_pos[0] < -game.ball_img.get_width() or 
        game.ball_pos[0] > game.screen_w or 
        game.ball_pos[1] > game.screen_h):
        game.goal_scored = False
        game.shot_processed = True
        game.ball_in_air = False
        game.ball_stopped = False
        game.ready_for_next_shot = True
        game.keeper_saved = False
        game.show_keeper_reaction = True
        game.ball_pos = [game.original_positions['ball'][0] * game.scale_x,
                        game.original_positions['ball'][1] * game.scale_y]

# ------------------------------------------------
# DRAW EVERYTHING
# ------------------------------------------------
def draw():
    # Background
    screen.blit(game.fans_img, (0, 0))
    screen.blit(game.grass_img, (0, game.screen_h - game.grass_img.get_height()))

    # Draw goal
    screen.blit(game.goal_img, game.goal_pos)
    
    # Draw keeper
    keeper_img = game.get_keeper_image()
    screen.blit(keeper_img, game.keeper_pos)
    
    # Draw player
    shooter_img = game.get_shooter_image()
    screen.blit(shooter_img, game.player_pos)
    
    # Draw ball (unless it's being held by the keeper)
    if not (game.keeper_saved and game.current_keeper_image == "holding"):
        screen.blit(game.ball_img, game.ball_pos)

    # Score - FIXED: Use scaled position consistently
    score_text = font.render(f"Score: {game.score}/{game.total_shots}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    # Goal/miss feedback
    if game.goal_scored is not None:
        text = font.render("GOAL!" if game.goal_scored else "SAVED!", 
                          True, (0, 255, 0) if game.goal_scored else (255, 100, 100))
        text_width = text.get_width()
        screen.blit(text, (game.screen_w - text_width - 20, 20))
    
    # FIXED: Display instruction for next shot - PROPERLY CENTERED
    if game.ready_for_next_shot:
        instruction_text = title_font.render("Press 'R' for next shot", True, (255, 255, 0))
        text_width = instruction_text.get_width()
        text_height = instruction_text.get_height()
        # Center horizontally, position at top with nice spacing
        screen.blit(instruction_text, (game.screen_w//2 - text_width//2, 20))
    
    # NEW: Show shooting instructions before first shot
    if game.show_shooting_instructions and game.total_shots == 0:
        # Background for better readability
        help_bg = pygame.Surface((400, 120), pygame.SRCALPHA)
        help_bg.fill((0, 0, 0, 180))
        screen.blit(help_bg, (game.screen_w//2 - 200, game.screen_h//2 - 60))
        
        help1 = font.render("Shoot with arrow keys:", True, (255, 255, 200))
        help2 = font.render("UP/DOWN/LEFT/RIGHT or W/A/S/D", True, (255, 255, 200))
        help3 = font.render("Press any key to start", True, (255, 200, 100))
        
        screen.blit(help1, (game.screen_w//2 - help1.get_width()//2, game.screen_h//2 - 40))
        screen.blit(help2, (game.screen_w//2 - help2.get_width()//2, game.screen_h//2))
        screen.blit(help3, (game.screen_w//2 - help3.get_width()//2, game.screen_h//2 + 40))
    
    # Display controls at bottom
    controls_text = title_font.render("Press 'F' to toggle fullscreen", True, (200, 200, 200))
    controls_width = controls_text.get_width()
    screen.blit(controls_text, (game.screen_w//2 - controls_width//2, game.screen_h - 40))

    pygame.display.update()

# ------------------------------------------------
# GAME LOOP
# ------------------------------------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                screen = game.toggle_fullscreen()
            
            # Hide instructions when any key is pressed
            if game.show_shooting_instructions and game.total_shots == 0:
                if event.key not in [pygame.K_f, pygame.K_r]:
                    game.show_shooting_instructions = False
            
            if event.key == pygame.K_r:
                if game.ready_for_next_shot:
                    game.reset_for_next_shot()

            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                             pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                if event.key not in game.key_pressed_once:
                    game.key_pressed_once.add(event.key)

        if event.type == pygame.KEYUP:
            if event.key in game.key_pressed_once:
                game.key_pressed_once.remove(event.key)

    # Determine shooting direction
    direction = None
    keys = game.key_pressed_once
    
    if not game.ball_in_air and not game.ball_stopped:
        if pygame.K_w in keys or pygame.K_UP in keys:
            if pygame.K_a in keys or pygame.K_LEFT in keys:
                direction = "top-left"
            elif pygame.K_d in keys or pygame.K_RIGHT in keys:
                direction = "top-right"
            else:
                direction = "top"
        elif pygame.K_s in keys or pygame.K_DOWN in keys:
            if pygame.K_a in keys or pygame.K_LEFT in keys:
                direction = "bottom-left"
            elif pygame.K_d in keys or pygame.K_RIGHT in keys:
                direction = "bottom-right"
            else:
                direction = "bottom"
        elif pygame.K_a in keys or pygame.K_LEFT in keys:
            direction = "left"
        elif pygame.K_d in keys or pygame.K_RIGHT in keys:
            direction = "right"

    if direction and not game.ball_in_air and not game.ball_stopped:
        shoot_ball(direction)
        game.goal_scored = None
        game.total_shots += 1
        game.shot_processed = False

    update_keeper()

    # Ball movement
    if game.ball_in_air and not game.ball_stopped:
        game.ball_pos[0] += game.ball_velocity[0] * game.scale_x
        game.ball_pos[1] += game.ball_velocity[1] * game.scale_y

        check_collisions()

        if game.goal_scored == True and game.ball_in_air:
            game.ball_velocity[0] *= 0.95
            game.ball_velocity[1] *= 0.95
            
            if abs(game.ball_velocity[0]) < 0.5 and abs(game.ball_velocity[1]) < 0.5:
                game.ball_in_air = False
                game.ball_stopped = True
                game.ready_for_next_shot = True
                game.ball_velocity = [0, 0]

    draw()
    clock.tick(FPS)