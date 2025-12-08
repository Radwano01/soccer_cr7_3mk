import pygame
import sys
import math
import os

# ------------------------------------------------
# SETUP
# ------------------------------------------------
# Don't initialize pygame at module level - will be initialized in run_penalty_shootout
SCREEN_W, SCREEN_H = 1000, 600
screen = None
clock = None
FPS = 60
font = None
title_font = None

def init_soccer_pygame():
    """Initialize pygame for soccer game"""
    global screen, clock, font, title_font
    
    # Initialize pygame if not already initialized
    if not pygame.get_init():
        pygame.init()
    
    # Initialize joysticks
    pygame.joystick.init()
    
    # Check if we already have a screen (from main game)
    # If not, create a new one
    if screen is None:
        # First, try to get existing surface (from main game)
        try:
            existing_surface = pygame.display.get_surface()
            if existing_surface is not None:
                print("Using existing pygame display surface")
                screen = existing_surface
                # Still try to switch to fullscreen for penalty game
                try:
                    fullscreen_info = pygame.display.get_desktop_sizes()[0]
                    new_screen = pygame.display.set_mode(fullscreen_info, pygame.FULLSCREEN)
                    if new_screen is not None:
                        screen = new_screen
                        print(f"Switched to fullscreen: {screen.get_size()}")
                except Exception as e:
                    print(f"Could not switch to fullscreen, using existing: {e}")
        except:
            pass
        
        # If we still don't have a screen, create a new one
        if screen is None:
            # Get fullscreen dimensions and create screen
            try:
                fullscreen_info = pygame.display.get_desktop_sizes()[0]
                new_screen = pygame.display.set_mode(fullscreen_info, pygame.FULLSCREEN)
                if new_screen is not None:
                    screen = new_screen
                    print(f"Created new fullscreen display: {screen.get_size()}")
                else:
                    raise RuntimeError("pygame.display.set_mode() returned None")
                pygame.display.set_caption("Penalty Shootout 3D - Shooter First")
            except Exception as e:
                # If fullscreen fails, try windowed mode
                print(f"Warning: Could not set fullscreen, trying windowed: {e}")
                try:
                    new_screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
                    if new_screen is not None:
                        screen = new_screen
                        print(f"Created windowed display: {screen.get_size()}")
                    else:
                        raise RuntimeError("pygame.display.set_mode() returned None for windowed")
                    pygame.display.set_caption("Penalty Shootout 3D - Shooter First")
                except Exception as e2:
                    print(f"Error: Could not create display: {e2}")
                    raise RuntimeError(f"Failed to initialize pygame display: {e2}")
    
    # Initialize other resources if needed
    if clock is None:
        clock = pygame.time.Clock()
    if font is None:
        font = pygame.font.SysFont("Arial", 32)
    if title_font is None:
        title_font = pygame.font.SysFont("Arial", 24, bold=True)
    
    # Ensure screen is not None
    if screen is None:
        raise RuntimeError("Failed to initialize pygame display - screen is None")
    
    # Load images AFTER display mode is set (pygame requires display mode for image loading)
    if fans_img_orig is None:
        load_all_images()

# ------------------------------------------------
# ASSET LOADING FUNCTIONS
# ------------------------------------------------
def load_image(path, scale=None, colorkey=None):
    try:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return None
            
        img = pygame.image.load(path)
        
        if path.lower().endswith('.png'):
            img = img.convert_alpha()
        else:
            img = img.convert()
            if colorkey is not None:
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
    try:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return None
            
        img = pygame.image.load(path)
        img = img.convert_alpha()
        
        if img.get_alpha() is None:
            img_with_alpha = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            for x in range(img.get_width()):
                for y in range(img.get_height()):
                    color = img.get_at((x, y))
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
    width, height = size
    ball_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 2 - 2
    
    pygame.draw.circle(ball_surface, (255, 255, 255), (center_x, center_y), radius)
    pygame.draw.circle(ball_surface, (0, 0, 0), (center_x, center_y), radius, 2)
    
    for i in range(5):
        angle = math.radians(i * 72)
        x = center_x + int(radius * 0.6 * math.cos(angle))
        y = center_y + int(radius * 0.6 * math.sin(angle))
        pygame.draw.circle(ball_surface, (0, 0, 0), (x, y), radius // 3)
        pygame.draw.circle(ball_surface, (255, 255, 255), (x, y), radius // 6)
    
    pygame.draw.circle(ball_surface, (0, 0, 0), (center_x, center_y), radius // 5)
    
    return ball_surface

def create_fallback_goal(size):
    width, height = size
    goal_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    pygame.draw.rect(goal_surface, (255, 255, 255), (0, 0, 20, height))
    pygame.draw.rect(goal_surface, (255, 255, 255), (width - 20, 0, 20, height))
    pygame.draw.rect(goal_surface, (255, 255, 255), (0, 0, width, 20))
    
    net_area = pygame.Surface((width - 40, height - 40), pygame.SRCALPHA)
    net_color = (255, 255, 255, 80)
    
    grid_size = 20
    for x in range(0, net_area.get_width(), grid_size):
        pygame.draw.line(net_area, net_color, (x, 0), (x, net_area.get_height()), 1)
    for y in range(0, net_area.get_height(), grid_size):
        pygame.draw.line(net_area, net_color, (0, y), (net_area.get_width(), y), 1)
    
    goal_surface.blit(net_area, (20, 20))
    
    return goal_surface

def create_fallback_keeper(size, holding_ball=False, crying=False):
    width, height = size
    keeper_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    pygame.draw.rect(keeper_surface, (200, 0, 0), (0, 0, width, height))
    pygame.draw.rect(keeper_surface, (0, 0, 0), (0, 0, width, height), 3)
    
    pygame.draw.circle(keeper_surface, (255, 200, 150), (width // 2, height // 4), 18)
    
    pygame.draw.rect(keeper_surface, (255, 255, 255), (25, 60, 50, 45))
    pygame.draw.rect(keeper_surface, (255, 200, 150), (10, 70, 15, 30))
    pygame.draw.rect(keeper_surface, (255, 200, 150), (75, 70, 15, 30))
    
    if holding_ball:
        pygame.draw.circle(keeper_surface, (255, 255, 255), (width // 2, 80), 15)
        pygame.draw.circle(keeper_surface, (0, 0, 0), (width // 2, 80), 15, 2)
    elif crying:
        pygame.draw.ellipse(keeper_surface, (0, 0, 0), (35, 28, 10, 5))
        pygame.draw.ellipse(keeper_surface, (0, 0, 0), (55, 28, 10, 5))
        pygame.draw.arc(keeper_surface, (0, 0, 0), (40, 45, 20, 10), math.pi, 2*math.pi, 2)
        pygame.draw.circle(keeper_surface, (100, 150, 255), (40, 50), 3)
        pygame.draw.circle(keeper_surface, (100, 150, 255), (60, 50), 3)
    
    return keeper_surface

def create_fallback_shooter(size, shooting=False, celebrating=False):
    width, height = size
    shooter_surface = pygame.Surface(size, pygame.SRCALPHA)
    
    color = (0, 150, 0)
    if shooting:
        color = (0, 200, 0)
    elif celebrating:
        color = (0, 255, 0)
    
    pygame.draw.rect(shooter_surface, color, (0, 0, width, height))
    pygame.draw.rect(shooter_surface, (0, 0, 0), (0, 0, width, height), 3)
    
    pygame.draw.circle(shooter_surface, (255, 200, 150), (width // 2, 50), 25)
    pygame.draw.rect(shooter_surface, (255, 255, 0), (35, 80, 70, 60))
    
    if shooting:
        pygame.draw.line(shooter_surface, (0, 0, 0), (70, 140), (100, 170), 3)
    elif celebrating:
        pygame.draw.line(shooter_surface, (255, 200, 150), (50, 80), (30, 40), 8)
        pygame.draw.line(shooter_surface, (255, 200, 150), (90, 80), (110, 40), 8)
    
    return shooter_surface

# Image paths and variables (will be loaded after pygame init)
BASE_PATH = None
GOAL_PATH = None
GRASS_PATH = None
FANS_PATH = None
BALL_PATH = None
SHOOTER_STAND_PATH = None
SHOOTER_SHOOT_PATH = None
SHOOTER_SUI_PATH = None
KEEPER_STAND_PATH = None
KEEPER_HOLDING_BALL_PATH = None
KEEPER_CRY_PATH = None
BALL_SIZE = (80, 80)

# Image variables (loaded after pygame init)
fans_img_orig = None
grass_img_orig = None
goal_img_orig = None
ball_img_orig = None
shooter_stand_img_orig = None
shooter_shoot_img_orig = None
shooter_sui_img_orig = None
keeper_stand_img_orig = None
keeper_holding_ball_img_orig = None
keeper_cry_img_orig = None

# Joysticks list (module-level)
joysticks = []

def load_all_images():
    """Load all images after pygame is initialized"""
    global BASE_PATH, GOAL_PATH, GRASS_PATH, FANS_PATH, BALL_PATH
    global SHOOTER_STAND_PATH, SHOOTER_SHOOT_PATH, SHOOTER_SUI_PATH
    global KEEPER_STAND_PATH, KEEPER_HOLDING_BALL_PATH, KEEPER_CRY_PATH
    global fans_img_orig, grass_img_orig, goal_img_orig, ball_img_orig
    global shooter_stand_img_orig, shooter_shoot_img_orig, shooter_sui_img_orig
    global keeper_stand_img_orig, keeper_holding_ball_img_orig, keeper_cry_img_orig
    
    # Get absolute path to images directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    BASE_PATH = os.path.join(script_dir, "images")
    
    # If images folder doesn't exist in script directory, try fallback
    if not os.path.exists(BASE_PATH):
        fallback_path = r"D:\coding\pythonuni\math project (2)\math_final-main\math_final-main\images"
        if os.path.exists(fallback_path):
            BASE_PATH = fallback_path
            print(f"Using fallback images path: {BASE_PATH}")
        else:
            print(f"Warning: Images directory not found at {BASE_PATH} or {fallback_path}")
    
    # Set up all image paths
    GOAL_PATH = os.path.join(BASE_PATH, "goal.png")
    GRASS_PATH = os.path.join(BASE_PATH, "grass.png")
    FANS_PATH = os.path.join(BASE_PATH, "fans.jpg")
    BALL_PATH = os.path.join(BASE_PATH, "ball.png")
    SHOOTER_STAND_PATH = os.path.join(BASE_PATH, "shooter_stand.png")
    SHOOTER_SHOOT_PATH = os.path.join(BASE_PATH, "shooter_time.png")
    SHOOTER_SUI_PATH = os.path.join(BASE_PATH, "shooter_sui.png")
    KEEPER_STAND_PATH = os.path.join(BASE_PATH, "keeper_stand.png")
    KEEPER_HOLDING_BALL_PATH = os.path.join(BASE_PATH, "keeper_holding_ball.png")
    KEEPER_CRY_PATH = os.path.join(BASE_PATH, "keeper_cry.gif")
    
    print(f"Loading images from: {BASE_PATH}")
    
    # Load fans and grass
    fans_img_orig = load_image(FANS_PATH, (SCREEN_W, 300))
    if fans_img_orig is None:
        fans_img_orig = pygame.Surface((SCREEN_W, 300))
        fans_img_orig.fill((50, 50, 50))
        print("Created fallback fans image")
    
    grass_img_orig = load_image(GRASS_PATH, (SCREEN_W, 300))
    if grass_img_orig is None:
        grass_img_orig = pygame.Surface((SCREEN_W, 300))
        grass_img_orig.fill((0, 120, 0))
        print("Created fallback grass image")
    
    # Load goal
    goal_img_orig = load_image_with_background_removal(GOAL_PATH, (500, 250))
    if goal_img_orig is None:
        goal_img_orig = load_image(GOAL_PATH, (500, 250), colorkey=(255, 255, 255))
        if goal_img_orig is None:
            goal_img_orig = create_fallback_goal((500, 250))
            print("Created fallback goal image")
    
    # Load ball
    ball_img_orig = load_image_with_background_removal(BALL_PATH, BALL_SIZE)
    if ball_img_orig is None:
        ball_img_orig = load_image(BALL_PATH, BALL_SIZE, colorkey=(255, 255, 255))
        if ball_img_orig is None:
            ball_img_orig = create_soccer_ball(BALL_SIZE)
            print("Created fallback ball image")
    
    # Load shooter images
    shooter_stand_img_orig = load_image_with_background_removal(SHOOTER_STAND_PATH, (140, 180))
    if shooter_stand_img_orig is None:
        shooter_stand_img_orig = create_fallback_shooter((140, 180))
        print("Created fallback shooter_stand image")
    
    shooter_shoot_img_orig = load_image_with_background_removal(SHOOTER_SHOOT_PATH, (140, 180))
    if shooter_shoot_img_orig is None:
        shooter_shoot_img_orig = create_fallback_shooter((140, 180), shooting=True)
        print("Created fallback shooter_shoot image")
    
    shooter_sui_img_orig = load_image_with_background_removal(SHOOTER_SUI_PATH, (140, 180))
    if shooter_sui_img_orig is None:
        shooter_sui_img_orig = create_fallback_shooter((140, 180), celebrating=True)
        print("Created fallback shooter_sui image")
    
    # Load keeper images
    keeper_stand_img_orig = load_image_with_background_removal(KEEPER_STAND_PATH, (100, 130))
    if keeper_stand_img_orig is None:
        keeper_stand_img_orig = create_fallback_keeper((100, 130))
        print("Created fallback keeper_stand image")
    
    keeper_holding_ball_img_orig = load_image_with_background_removal(KEEPER_HOLDING_BALL_PATH, (100, 130))
    if keeper_holding_ball_img_orig is None:
        keeper_holding_ball_img_orig = create_fallback_keeper((100, 130), holding_ball=True)
        print("Created fallback keeper_holding_ball image")
    
    # Load keeper cry image
    try:
        keeper_cry_img_orig = load_image(KEEPER_CRY_PATH, (100, 130))
    except Exception as e:
        print(f"Warning: Could not load keeper_cry image: {e}")
        keeper_cry_img_orig = None
    
    if keeper_cry_img_orig is None:
        keeper_cry_img_orig = create_fallback_keeper((100, 130), crying=True)
        print("Created fallback keeper_cry image")
    
    print("All images loaded successfully")

# ------------------------------------------------
# JOYSTICK INITIALIZATION
# ------------------------------------------------
def init_joysticks():
    """Bağlı joystick'leri başlatır, hatalı cihazları atlar."""
    global joysticks
    joysticks = []
    
    print(f"\n🔍 Joystick taraması başlatılıyor... (Algılanan: {pygame.joystick.get_count()})")
    
    # Kaç joystick varsa o kadar döngü kurar
    for i in range(pygame.joystick.get_count()): 
        try:
            joy = pygame.joystick.Joystick(i)
            joy.init()
            joysticks.append(joy)
            
            # Detaylı bilgi göster
            num_buttons = joy.get_numbuttons()
            num_axes = joy.get_numaxes()
            num_hats = joy.get_numhats()
            
            print(f"  ✅ Joystick {i}: {joy.get_name()}")
            print(f"     - Butonlar: {num_buttons}, Eksenler: {num_axes}, HAT (D-pad): {num_hats}")
            
        except pygame.error as e:
            # Eğer bir cihaz başlatılamazsa, onu atla
            print(f"  ❌ HATA: Joystick {i} başlatılamadı: {e}. Atlanıyor.")
            
    if joysticks:
        print(f"\n✅ Toplam {len(joysticks)} aktif joystick bağlandı.")
        print("💡 İPUCU: Butonları test etmek için herhangi bir butona basın (konsolda göreceksiniz)\n")
    else:
        print("\n⚠️ Hiçbir joystick algılanmadı.\n")

# ------------------------------------------------
# GAME STATE - SHOOTER FIRST
# ------------------------------------------------
class GameState:
    def __init__(self):
        self.fullscreen = True
        self.screen_w, self.screen_h = pygame.display.get_desktop_sizes()[0]
        
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
        
        # Current positions
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
        self.shot_processed = False
        
        self.ball_stopped = False
        self.ready_for_next_shot = False
        
        self.keeper_saved = False
        self.ball_saved = False
        
        # Initialize image states correctly
        self.current_keeper_image = "stand"
        self.show_keeper_reaction = False
        
        self.current_shooter_image = "stand"
        self.shooting_direction = None
        self.ball_target_zone = None
        self.keeper_zone = None
        
        # GAME FLOW VARIABLES
        self.game_phase = "instructions"  # "instructions", "shooter_turn", "keeper_turn", "executing", "result"
        self.shooter_decision = None  # Shooting direction
        self.keeper_decision = None  # "left", "middle", "right"
        self.shooter_choice_display = None
        self.keeper_choice_display = None
        
        # Track when result phase started (for delay before closing)
        self.result_start_time = None
        
        # Joystick state tracking
        self.shooter_selected_direction = None  # Currently selected direction for shooter
        self.keeper_selected_zone = None  # Currently selected zone for keeper
        
        # Player role mapping (which joystick controls which role)
        self.shooter_joystick_id = 0  # Default: joystick 0 is shooter
        self.keeper_joystick_id = 1   # Default: joystick 1 is keeper
        
        # Scaled images
        self.scale_images()
        self.update_keeper_zone()
    
    def update_keeper_zone(self):
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
        
        # Scale goal image (with fallback check)
        if goal_img_orig is not None:
            self.goal_img = pygame.transform.scale(goal_img_orig, 
                                                  (int(500 * self.scale_x), 
                                                   int(250 * self.scale_y)))
        else:
            self.goal_img = create_fallback_goal((int(500 * self.scale_x), int(250 * self.scale_y)))
        
        # Scale ball image (with fallback check)
        if ball_img_orig is not None:
            self.ball_img = pygame.transform.scale(ball_img_orig,
                                                  (int(BALL_SIZE[0] * self.scale_x),
                                                   int(BALL_SIZE[1] * self.scale_y)))
        else:
            self.ball_img = create_soccer_ball((int(BALL_SIZE[0] * self.scale_x), int(BALL_SIZE[1] * self.scale_y)))
        
        # Scale keeper images (with fallback checks)
        if keeper_stand_img_orig is not None:
            self.keeper_stand_img = pygame.transform.scale(keeper_stand_img_orig,
                                                          (int(100 * self.scale_x),
                                                           int(130 * self.scale_y)))
        else:
            self.keeper_stand_img = create_fallback_keeper((int(100 * self.scale_x), int(130 * self.scale_y)))
        
        if keeper_holding_ball_img_orig is not None:
            self.keeper_holding_ball_img = pygame.transform.scale(keeper_holding_ball_img_orig,
                                                                (int(100 * self.scale_x),
                                                                 int(130 * self.scale_y)))
        else:
            self.keeper_holding_ball_img = create_fallback_keeper((int(100 * self.scale_x), int(130 * self.scale_y)), holding_ball=True)
        
        if keeper_cry_img_orig is not None:
            self.keeper_cry_img = pygame.transform.scale(keeper_cry_img_orig,
                                                        (int(100 * self.scale_x),
                                                         int(130 * self.scale_y)))
        else:
            self.keeper_cry_img = create_fallback_keeper((int(100 * self.scale_x), int(130 * self.scale_y)), crying=True)
        
        # Scale shooter images (with fallback checks)
        if shooter_stand_img_orig is not None:
            self.shooter_stand_img = pygame.transform.scale(shooter_stand_img_orig,
                                                           (int(140 * self.scale_x),
                                                            int(180 * self.scale_y)))
        else:
            self.shooter_stand_img = create_fallback_shooter((int(140 * self.scale_x), int(180 * self.scale_y)))
        
        if shooter_shoot_img_orig is not None:
            self.shooter_shoot_img = pygame.transform.scale(shooter_shoot_img_orig,
                                                           (int(140 * self.scale_x),
                                                            int(180 * self.scale_y)))
        else:
            self.shooter_shoot_img = create_fallback_shooter((int(140 * self.scale_x), int(180 * self.scale_y)), shooting=True)
        
        if shooter_sui_img_orig is not None:
            self.shooter_sui_img = pygame.transform.scale(shooter_sui_img_orig,
                                                         (int(140 * self.scale_x),
                                                          int(180 * self.scale_y)))
        else:
            self.shooter_sui_img = create_fallback_shooter((int(140 * self.scale_x), int(180 * self.scale_y)), celebrating=True)
        
        self.update_images()
        
        self.fans_img = pygame.transform.scale(fans_img_orig,
                                              (self.screen_w, int(300 * self.scale_y)))
        self.grass_img = pygame.transform.scale(grass_img_orig,
                                               (self.screen_w, int(300 * self.scale_y)))
        
        self.update_positions()
    
    def update_images(self):
        """Update which images to display based on game state"""
        # Shooter images logic
        if not self.shot_processed:
            # During shot execution
            if self.ball_in_air:
                self.current_shooter_image = "shoot"
            else:
                self.current_shooter_image = "stand"
        else:
            # After shot is processed
            if self.goal_scored == True:
                self.current_shooter_image = "sui"
            else:
                self.current_shooter_image = "stand"
        
        # Keeper images logic
        if not self.shot_processed:
            self.current_keeper_image = "stand"
            self.show_keeper_reaction = False
        elif self.show_keeper_reaction:
            # Show reaction after shot is processed
            if self.keeper_saved:
                self.current_keeper_image = "holding"
            else:
                self.current_keeper_image = "cry"
        else:
            self.current_keeper_image = "stand"
    
    def get_keeper_image(self):
        """Return the correct keeper image based on current state"""
        if self.current_keeper_image == "stand":
            return self.keeper_stand_img
        elif self.current_keeper_image == "holding":
            return self.keeper_holding_ball_img
        elif self.current_keeper_image == "cry":
            return self.keeper_cry_img
        else:
            return self.keeper_stand_img
    
    def get_shooter_image(self):
        """Return the correct shooter image based on current state"""
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
        
        # Reset image states
        self.current_keeper_image = "stand"
        self.current_shooter_image = "stand"
        
        # Reset decisions
        self.game_phase = "shooter_turn"
        self.shooter_decision = None
        self.keeper_decision = None
        self.shooter_choice_display = None
        self.keeper_choice_display = None
        
        # Reset joystick state
        self.shooter_selected_direction = None
        self.keeper_selected_zone = None
        
        self.ball_pos = [self.original_positions['ball'][0] * self.scale_x,
                        self.original_positions['ball'][1] * self.scale_y]
        
        # Reset keeper to center
        goal_left = self.goal_pos[0] + self.goal_img.get_width() * 0.1
        goal_right = self.goal_pos[0] + self.goal_img.get_width() * 0.9 - self.keeper_stand_img.get_width()
        self.keeper_target_x = goal_left + (goal_right - goal_left) / 2
        self.keeper_pos[0] = self.keeper_target_x
        
        self.update_keeper_zone()
    
    def shooter_makes_decision(self, direction):
        """Shooter decides where to shoot (MUST GO FIRST)"""
        if self.game_phase != "shooter_turn" or self.shooter_decision is not None:
            return False
        
        # Map simplified directions to actual shooting directions
        direction_map = {
            "left": "top-left",
            "middle": "top",
            "right": "top-right",
            "top-left": "top-left",
            "top": "top",
            "top-right": "top-right",
            "bottom-left": "bottom-left",
            "bottom": "bottom",
            "bottom-right": "bottom-right"
        }
        
        actual_direction = direction_map.get(direction, "top")
        self.shooter_decision = actual_direction
        
        # Update display
        self.shooter_choice_display = direction.capitalize()
        
        # Move to keeper's turn
        self.game_phase = "keeper_turn"
        
        return True
    
    def keeper_makes_decision(self, zone):
        """Keeper decides where to dive (AFTER shooter)"""
        if self.game_phase != "keeper_turn" or self.keeper_decision is not None:
            return False
        
        self.keeper_decision = zone
        
        # Update display
        self.keeper_choice_display = zone.capitalize()
        
        # Move keeper to the chosen zone
        goal_left = self.goal_pos[0] + self.goal_img.get_width() * 0.1
        goal_right = self.goal_pos[0] + self.goal_img.get_width() * 0.9 - self.keeper_stand_img.get_width()
        
        if zone == "left":
            self.keeper_target_x = goal_left
            self.keeper_pos[0] = goal_left
        elif zone == "right":
            self.keeper_target_x = goal_right
            self.keeper_pos[0] = goal_right
        else:  # middle
            self.keeper_target_x = goal_left + (goal_right - goal_left) / 2
            self.keeper_pos[0] = self.keeper_target_x
        
        self.update_keeper_zone()
        
        # Both have decided, execute the shot
        self.game_phase = "executing"
        self.execute_shot()
        
        return True
    
    def execute_shot(self):
        """Execute the shot based on decisions"""
        if not (self.shooter_decision and self.keeper_decision):
            return
        
        # Determine ball target zone based on shooter decision
        if "left" in self.shooter_decision:
            self.ball_target_zone = "left"
        elif "right" in self.shooter_decision:
            self.ball_target_zone = "right"
        else:
            self.ball_target_zone = "middle"
        
        # Shoot the ball
        shoot_ball(self.shooter_decision)
        self.total_shots += 1

# Initialize game state (will be reinitialized in run_penalty_shootout)
game = None

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
# SIMPLE COLLISION DETECTION - FIXED
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
            # KEEPER SAVES THE BALL
            game.goal_scored = False
            game.shot_processed = True
            game.ball_saved = True
            game.ball_in_air = False
            game.ball_stopped = True
            game.ready_for_next_shot = True
            game.game_phase = "result"
            game.ball_velocity = [0, 0]
            game.keeper_saved = True
            game.show_keeper_reaction = True
            game.result_start_time = pygame.time.get_ticks()  # Track when result phase started
            
            # Set the correct image states
            game.current_keeper_image = "holding"
            game.current_shooter_image = "stand"  # Shooter should be standing when keeper saves
            
            # Position ball in keeper's hands
            keeper_center_x = game.keeper_pos[0] + game.keeper_stand_img.get_width() // 2
            keeper_center_y = game.keeper_pos[1] + game.keeper_stand_img.get_height() // 2
            game.ball_pos[0] = keeper_center_x - game.ball_img.get_width() // 2
            game.ball_pos[1] = keeper_center_y - game.ball_img.get_height() // 2
            return
        else:
            # GOAL SCORED
            game.goal_scored = True
            game.score += 1
            game.shot_processed = True
            game.keeper_saved = False
            game.show_keeper_reaction = True
            game.game_phase = "result"
            game.result_start_time = pygame.time.get_ticks()  # Track when result phase started
            
            # Set the correct image states
            game.current_keeper_image = "cry"
            game.current_shooter_image = "sui"  # Shooter celebrates
            
            game.ball_velocity = [game.ball_velocity[0] * 0.5, game.ball_velocity[1] * 0.5]
            return
    
    if (game.ball_pos[1] < -game.ball_img.get_height() or 
        game.ball_pos[0] < -game.ball_img.get_width() or 
        game.ball_pos[0] > game.screen_w or 
        game.ball_pos[1] > game.screen_h):
        # BALL MISSED THE GOAL
        game.goal_scored = False
        game.shot_processed = True
        game.ball_in_air = False
        game.ball_stopped = True
        game.ready_for_next_shot = True
        game.game_phase = "result"
        game.keeper_saved = False
        game.show_keeper_reaction = True
        game.result_start_time = pygame.time.get_ticks()  # Track when result phase started
        
        # Set the correct image states
        game.current_keeper_image = "cry"  # Keeper is sad even though ball missed
        game.current_shooter_image = "stand"  # Shooter stands
        
        game.ball_pos = [game.original_positions['ball'][0] * game.scale_x,
                        game.original_positions['ball'][1] * game.scale_y]

# ------------------------------------------------
# DRAW EVERYTHING
# ------------------------------------------------
def draw():
    global screen
    # Ensure screen is initialized
    if screen is None:
        print("WARNING: screen is None in draw(), initializing...")
        init_soccer_pygame()
        if screen is None:
            print("ERROR: screen is still None after init_soccer_pygame() in draw()")
            return  # Can't draw without a screen
    
    # Background
    try:
        screen.blit(game.fans_img, (0, 0))
    except Exception as e:
        print(f"Error in draw() blitting fans_img: {e}")
        return
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

    # Score
    score_text = font.render(f"Score: {game.score}/{game.total_shots}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    # Goal/miss feedback
    if game.goal_scored is not None:
        text = font.render("GOAL!" if game.goal_scored else "SAVED!", 
                          True, (0, 255, 0) if game.goal_scored else (255, 100, 100))
        text_width = text.get_width()
        screen.blit(text, (game.screen_w - text_width - 20, 20))
    
    # Display choices - HIDE SHOOTER'S CHOICE FROM KEEPER
    # Removed shooter choice display to prevent goalkeeper from seeing it
    
    if game.keeper_choice_display:
        keeper_text = font.render(f"Keeper: {game.keeper_choice_display}", True, (255, 100, 100))
        screen.blit(keeper_text, (game.screen_w - keeper_text.get_width() - 20, 100))
    
    # Phase indicator
    phase_colors = {
        "instructions": (255, 255, 100),
        "shooter_turn": (100, 255, 100),
        "keeper_turn": (255, 100, 100),
        "executing": (255, 255, 200),
        "result": (255, 200, 100)
    }
    
    phase_texts = {
        "instructions": "READY TO START",
        "shooter_turn": "SHOOTER'S TURN",
        "keeper_turn": "KEEPER'S TURN",
        "executing": "SHOT IN PROGRESS",
        "result": "RESULT"
    }
    
    if game.game_phase in phase_texts:
        phase_text = font.render(phase_texts[game.game_phase], True, phase_colors[game.game_phase])
        screen.blit(phase_text, (game.screen_w//2 - phase_text.get_width()//2, 20))
    
    # Instruction for next shot - REMOVED
    
    # Initial instructions
    if game.game_phase == "instructions":
        help_bg = pygame.Surface((500, 180), pygame.SRCALPHA)
        help_bg.fill((0, 0, 0, 180))
        screen.blit(help_bg, (game.screen_w//2 - 250, game.screen_h//2 - 90))
        
        help1 = font.render("PENALTY SHOOTOUT - SHOOTER FIRST", True, (255, 255, 200))
        help2 = title_font.render("SHOOTER MUST CHOOSE FIRST (Joystick 0)", True, (100, 255, 100))
        help3 = title_font.render("KEEPER CHOOSES AFTER (Joystick 1)", True, (255, 100, 100))
        help4 = title_font.render("Shooter: Joystick 0 - D-pad to choose, Left button to shoot", True, (200, 255, 200))
        help5 = title_font.render("Keeper: Joystick 1 - D-pad to choose, Left button to defend", True, (255, 200, 200))
        help6 = title_font.render("Press any key or joystick button to start", True, (255, 200, 100))
        
        screen.blit(help1, (game.screen_w//2 - help1.get_width()//2, game.screen_h//2 - 90))
        screen.blit(help2, (game.screen_w//2 - help2.get_width()//2, game.screen_h//2 - 50))
        screen.blit(help3, (game.screen_w//2 - help3.get_width()//2, game.screen_h//2 - 20))
        screen.blit(help4, (game.screen_w//2 - help4.get_width()//2, game.screen_h//2 + 10))
        screen.blit(help5, (game.screen_w//2 - help5.get_width()//2, game.screen_h//2 + 40))
        screen.blit(help6, (game.screen_w//2 - help6.get_width()//2, game.screen_h//2 + 70))
    
    # Current turn instructions
    elif game.game_phase == "shooter_turn":
        instr_bg = pygame.Surface((500, 80), pygame.SRCALPHA)
        instr_bg.fill((0, 50, 0, 180))
        screen.blit(instr_bg, (game.screen_w//2 - 250, game.screen_h - 100))
        
        if not game.shooter_decision:
            instr1 = title_font.render("SHOOTER'S TURN: Choose where to shoot", True, (200, 255, 200))
            instr2 = title_font.render("Joystick 0: D-pad to choose direction, Left button to shoot", True, (150, 255, 150))
            screen.blit(instr1, (game.screen_w//2 - instr1.get_width()//2, game.screen_h - 80))
            screen.blit(instr2, (game.screen_w//2 - instr2.get_width()//2, game.screen_h - 50))
        else:
            # Don't show shooter's choice to prevent goalkeeper from seeing it
            instr = title_font.render("Waiting for keeper to choose...", True, (200, 255, 200))
            screen.blit(instr, (game.screen_w//2 - instr.get_width()//2, game.screen_h - 65))
    
    elif game.game_phase == "keeper_turn":
        instr_bg = pygame.Surface((500, 80), pygame.SRCALPHA)
        instr_bg.fill((50, 0, 0, 180))
        screen.blit(instr_bg, (game.screen_w//2 - 250, game.screen_h - 100))
        
        if not game.keeper_decision:
            instr1 = title_font.render("KEEPER'S TURN: Choose where to dive", True, (255, 200, 200))
            instr2 = title_font.render("Joystick 1: D-pad Left=Left, Right=Right, Up/Down=Middle, Left button to defend", True, (255, 150, 150))
            screen.blit(instr1, (game.screen_w//2 - instr1.get_width()//2, game.screen_h - 80))
            screen.blit(instr2, (game.screen_w//2 - instr2.get_width()//2, game.screen_h - 50))
    
    elif game.game_phase == "executing":
        instr_bg = pygame.Surface((400, 40), pygame.SRCALPHA)
        instr_bg.fill((50, 50, 0, 180))
        screen.blit(instr_bg, (game.screen_w//2 - 200, game.screen_h - 60))
        
        instr = title_font.render("Shot in progress...", True, (255, 255, 150))
        screen.blit(instr, (game.screen_w//2 - instr.get_width()//2, game.screen_h - 50))
    
    elif game.game_phase == "result" and game.ready_for_next_shot:
        # Removed "Press 'R' for next penalty" message
        pass
    
    # CHANGED: Display fullscreen toggle control at bottom right
    controls_text = title_font.render("Press 'F' to toggle fullscreen", True, (200, 200, 200))
    screen.blit(controls_text, (game.screen_w - controls_text.get_width() - 20, game.screen_h - 40))

    pygame.display.update()

# ------------------------------------------------
# GAME LOOP
# ------------------------------------------------
def run_game(quit_pygame=True):
    """
    Run the game and return True if saved, False otherwise
    
    Args:
        quit_pygame: If True, quit pygame at the end. If False, keep pygame running.
    """
    global screen, clock
    # Ensure screen and clock are initialized
    if screen is None or clock is None:
        init_soccer_pygame()
    
    # Initialize joysticks using the same logic as math_quiz_final_last_edit.py
    # Make sure pygame.joystick is initialized
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    init_joysticks()
    
    # Print current joystick status
    print(f"📊 Joystick status: {len(joysticks)} joysticks initialized")
    for i, joy in enumerate(joysticks):
        if joy:
            print(f"   - Joystick {i}: {joy.get_name()}")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle joystick device connection/disconnection
            if event.type == pygame.JOYDEVICEADDED:
                print(f"🔌 Joystick device added: {event.device_index}")
                init_joysticks()  # Re-initialize all joysticks
            if event.type == pygame.JOYDEVICEREMOVED:
                print(f"🔌 Joystick device removed: {event.device_index}")
                init_joysticks()  # Re-initialize all joysticks
            
            # JOYSTICK AXIS MOTION - fallback for joysticks without D-pad
            if event.type == pygame.JOYAXISMOTION:
                joy_id = event.joy
                axis = event.axis
                value = event.value
                
                # Check if joystick exists
                if joy_id >= len(joysticks):
                    continue
                if joysticks[joy_id] is None:
                    continue
                
                # Only process if value is significant (dead zone)
                if abs(value) < 0.5:
                    continue
                
                # Skip instructions screen with any axis movement
                if game.game_phase == "instructions":
                    print("🚀 Starting game from instructions (axis) - skipping shot logic")
                    game.game_phase = "shooter_turn"
                    continue  # Skip the rest of axis handling - don't count this as a shot
                
                # Use left stick (axis 0 = X, axis 1 = Y) for direction selection
                if axis == 0:  # X axis
                    # SHOOTER CONTROLS (use mapped joystick)
                    if joy_id == game.shooter_joystick_id and game.game_phase == "shooter_turn" and not game.shooter_decision:
                        if value < -0.5:  # Left
                            game.shooter_selected_direction = "left"
                            print(f"📍 Shooter selected direction (axis): left")
                        elif value > 0.5:  # Right
                            game.shooter_selected_direction = "right"
                            print(f"📍 Shooter selected direction (axis): right")
                    
                    # KEEPER CONTROLS (use mapped joystick)
                    elif joy_id == game.keeper_joystick_id and game.game_phase == "keeper_turn" and not game.keeper_decision:
                        if value < -0.5:  # Left
                            game.keeper_selected_zone = "left"
                            print(f"📍 Keeper selected zone (axis): left")
                        elif value > 0.5:  # Right
                            game.keeper_selected_zone = "right"
                            print(f"📍 Keeper selected zone (axis): right")
                
                elif axis == 1:  # Y axis
                    # SHOOTER CONTROLS (use mapped joystick)
                    if joy_id == game.shooter_joystick_id and game.game_phase == "shooter_turn" and not game.shooter_decision:
                        if value < -0.5:  # Up
                            game.shooter_selected_direction = "top"
                            print(f"📍 Shooter selected direction (axis): top")
                        elif value > 0.5:  # Down
                            game.shooter_selected_direction = "bottom"
                            print(f"📍 Shooter selected direction (axis): bottom")
                    
                    # KEEPER CONTROLS (use mapped joystick)
                    elif joy_id == game.keeper_joystick_id and game.game_phase == "keeper_turn" and not game.keeper_decision:
                        if abs(value) > 0.5:  # Up or Down = Middle
                            game.keeper_selected_zone = "middle"
                            print(f"📍 Keeper selected zone (axis): middle")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    game.toggle_fullscreen()
                
                # Start the game from instructions
                if game.game_phase == "instructions":
                    if event.key not in [pygame.K_f, pygame.K_r]:
                        game.game_phase = "shooter_turn"
            
            # JOYSTICK HAT (D-PAD) MOTION - for direction selection and confirmation
            if event.type == pygame.JOYHATMOTION:
                joy_id = event.joy
                hat_value = event.value
                hat_x, hat_y = hat_value
                
                # Check if joystick exists
                if joy_id >= len(joysticks):
                    print(f"⚠️ Warning: Joystick {joy_id} not found in joysticks list (len={len(joysticks)})")
                    continue
                if joysticks[joy_id] is None:
                    print(f"⚠️ Warning: Joystick {joy_id} is None")
                    continue
                
                # Ignore neutral position (0, 0) - D-pad released
                if hat_x == 0 and hat_y == 0:
                    continue
                
                # Debug output
                print(f"🎮 Joystick {joy_id} HAT: ({hat_x}, {hat_y}) | Phase: {game.game_phase}")
                
                # Skip instructions screen with any D-pad movement
                if game.game_phase == "instructions":
                    print("🚀 Starting game from instructions (D-pad) - skipping shot logic")
                    game.game_phase = "shooter_turn"
                    continue  # Skip the rest of D-pad handling - don't count this as a shot
                
                # SHOOTER CONTROLS - D-pad for direction selection (use mapped joystick)
                if joy_id == game.shooter_joystick_id and game.game_phase == "shooter_turn" and not game.shooter_decision:
                    # If D-pad left is pressed and a direction is already selected, confirm
                    if hat_x == -1 and hat_y == 0 and game.shooter_selected_direction is not None:
                        print(f"✅ Shooter confirming direction: {game.shooter_selected_direction}")
                        game.shooter_makes_decision(game.shooter_selected_direction)
                    else:
                        # Otherwise, use D-pad for direction selection
                        shooter_direction = None
                        
                        # Determine direction based on D-pad
                        if hat_x == -1 and hat_y == 0:  # Left
                            shooter_direction = "left"
                        elif hat_x == 1 and hat_y == 0:  # Right
                            shooter_direction = "right"
                        elif hat_x == 0 and hat_y == -1:  # Up
                            shooter_direction = "top"
                        elif hat_x == 0 and hat_y == 1:  # Down
                            shooter_direction = "bottom"
                        elif hat_x == -1 and hat_y == -1:  # Up-Left
                            shooter_direction = "top-left"
                        elif hat_x == 1 and hat_y == -1:  # Up-Right
                            shooter_direction = "top-right"
                        elif hat_x == -1 and hat_y == 1:  # Down-Left
                            shooter_direction = "bottom-left"
                        elif hat_x == 1 and hat_y == 1:  # Down-Right
                            shooter_direction = "bottom-right"
                        
                        if shooter_direction:
                            game.shooter_selected_direction = shooter_direction
                            print(f"📍 Shooter selected direction: {shooter_direction}")
                
                # KEEPER CONTROLS - D-pad for zone selection (use mapped joystick)
                elif joy_id == game.keeper_joystick_id and game.game_phase == "keeper_turn" and not game.keeper_decision:
                    # If D-pad left is pressed and a zone is already selected, confirm
                    if hat_x == -1 and hat_y == 0 and game.keeper_selected_zone is not None:
                        print(f"✅ Keeper confirming zone: {game.keeper_selected_zone}")
                        game.keeper_makes_decision(game.keeper_selected_zone)
                    else:
                        # Otherwise, use D-pad for zone selection
                        keeper_zone = None
                        
                        if hat_x == -1:  # Left
                            keeper_zone = "left"
                        elif hat_x == 1:  # Right
                            keeper_zone = "right"
                        elif hat_y == -1 or hat_y == 1:  # Up or Down
                            keeper_zone = "middle"
                        
                        if keeper_zone:
                            game.keeper_selected_zone = keeper_zone
                            print(f"📍 Keeper selected zone: {keeper_zone}")
            
            # JOYSTICK BUTTON PRESS - left button to confirm action
            if event.type == pygame.JOYBUTTONDOWN:
                joy_id = event.joy
                button = event.button
                
                # Check if joystick exists
                if joy_id >= len(joysticks):
                    print(f"⚠️ Warning: Joystick {joy_id} not found in joysticks list (len={len(joysticks)})")
                    continue
                if joysticks[joy_id] is None:
                    print(f"⚠️ Warning: Joystick {joy_id} is None")
                    continue
                
                # Debug output
                joy_name = joysticks[joy_id].get_name() if joy_id < len(joysticks) else "Unknown"
                print(f"🎮 Joystick {joy_id} ({joy_name}): Button {button} pressed | Phase: {game.game_phase}")
                
                # Start the game from instructions (any joystick button)
                # IMPORTANT: Skip the rest of button handling if we're just starting from instructions
                if game.game_phase == "instructions":
                    print("🚀 Starting game from instructions - skipping shot logic")
                    game.game_phase = "shooter_turn"
                    continue  # Skip the rest of button handling - don't count this as a shot
                
                # SHOOTER CONTROLS - Any button to confirm/shoot (use mapped joystick)
                if joy_id == game.shooter_joystick_id and game.game_phase == "shooter_turn" and not game.shooter_decision:
                    # Accept button 0, 1, or 2 as confirm button (common gamepad buttons)
                    if button in [0, 1, 2]:
                        # Only confirm if a direction has been selected - NO AUTOMATIC DEFAULT
                        if game.shooter_selected_direction is not None:
                            print(f"✅ Shooter confirming with button {button}: {game.shooter_selected_direction}")
                            game.shooter_makes_decision(game.shooter_selected_direction)
                        else:
                            print(f"⚠️ Shooter must select a direction first before confirming!")
                
                # KEEPER CONTROLS - Any button to confirm/defend (use mapped joystick)
                elif joy_id == game.keeper_joystick_id and game.game_phase == "keeper_turn" and not game.keeper_decision:
                    # Accept button 0, 1, or 2 as confirm button (common gamepad buttons)
                    if button in [0, 1, 2]:
                        # Only confirm if a zone has been selected - NO AUTOMATIC DEFAULT
                        if game.keeper_selected_zone is not None:
                            print(f"✅ Keeper confirming with button {button}: {game.keeper_selected_zone}")
                            game.keeper_makes_decision(game.keeper_selected_zone)
                        else:
                            print(f"⚠️ Keeper must select a zone first before confirming!")

        # Ball movement (after shot is executed)
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

        # Check if shot is complete and ball has stopped
        if game.shot_processed and (game.ball_stopped or not game.ball_in_air):
            # Set result start time if not already set
            if game.result_start_time is None:
                game.result_start_time = pygame.time.get_ticks()
            
            # Wait 2.5 seconds to show the result images and reactions
            elapsed_time = pygame.time.get_ticks() - game.result_start_time
            if elapsed_time >= 2500:  # 2.5 seconds
                # Return True if saved, False otherwise
                result = game.keeper_saved
                if quit_pygame:
                    pygame.quit()
                return result

        # Update images every frame to ensure correct display
        game.update_images()
        
        draw()
        clock.tick(FPS)

def run_penalty_shootout(goalkeeper, attacker):
    """
    Wrapper function for penalty shootout game.
    
    Args:
        goalkeeper: Name/identifier of the goalkeeper player ("p1" or "p2")
        attacker: Name/identifier of the attacker/penalty taker ("p1" or "p2")
    
    Returns:
        True if goalkeeper saved (no goal), False if goal was scored
    """
    global game, screen, clock, font, title_font
    
    try:
        # Initialize pygame and game state if not already done
        print(f"Initializing penalty shootout for {goalkeeper} (GK) vs {attacker} (Attacker)")
        init_soccer_pygame()
        
        # Verify screen was initialized
        if screen is None:
            print("ERROR: screen is None after init_soccer_pygame()")
            raise RuntimeError("Failed to initialize screen in penalty shootout")
        
        print(f"Screen initialized: {screen}, size: {screen.get_size() if screen else 'N/A'}")
        
        # Initialize game state if needed
        if game is None:
            print("Creating new GameState")
            game = GameState()
        else:
            # Reset game state for new penalty
            print("Resetting GameState for new penalty")
            game.reset_for_next_shot()
            game.game_phase = "instructions"
        
        # Map joysticks to roles based on who is attacker and goalkeeper
        # In math quiz: p1 = joystick 0, p2 = joystick 1
        # This ensures each player only controls their assigned role
        if attacker == "p1":
            game.shooter_joystick_id = 0  # Player 1 (joystick 0) is shooter
        elif attacker == "p2":
            game.shooter_joystick_id = 1  # Player 2 (joystick 1) is shooter
        else:
            # Default fallback
            game.shooter_joystick_id = 0
            print(f"⚠️ Warning: Unknown attacker '{attacker}', defaulting to joystick 0")
        
        if goalkeeper == "p1":
            game.keeper_joystick_id = 0  # Player 1 (joystick 0) is keeper
        elif goalkeeper == "p2":
            game.keeper_joystick_id = 1  # Player 2 (joystick 1) is keeper
        else:
            # Default fallback
            game.keeper_joystick_id = 1
            print(f"⚠️ Warning: Unknown goalkeeper '{goalkeeper}', defaulting to joystick 1")
        
        # Safety check: Ensure attacker and goalkeeper are different players
        if attacker == goalkeeper:
            print(f"⚠️ ERROR: Attacker and goalkeeper are the same player ({attacker})! This should not happen.")
            # Force different joysticks to prevent one player controlling both roles
            if attacker == "p1":
                game.keeper_joystick_id = 1  # Force p2 to be keeper
            else:
                game.keeper_joystick_id = 0  # Force p1 to be keeper
        
        # Final safety check: Ensure joysticks are different
        if game.shooter_joystick_id == game.keeper_joystick_id:
            print(f"⚠️ ERROR: Shooter and keeper are using the same joystick ({game.shooter_joystick_id})! Preventing conflict.")
            # Swap keeper to different joystick
            game.keeper_joystick_id = 1 if game.shooter_joystick_id == 0 else 0
        
        print(f"🎮 Joystick mapping: Shooter = Joystick {game.shooter_joystick_id} ({attacker}), Keeper = Joystick {game.keeper_joystick_id} ({goalkeeper})")
        print(f"✅ Role separation: Each player controls only their assigned role")
        
        # Run the game and get result (don't quit pygame so main game continues)
        print("Starting penalty shootout game loop")
        result = run_game(quit_pygame=False)
        print(f"Penalty shootout result: {result} (True=saved, False=goal)")
        
        # Return True if saved (keeper won), False if goal scored (attacker won)
        return result
    except Exception as e:
        print(f"Error in run_penalty_shootout: {e}")
        import traceback
        traceback.print_exc()
        # Return False (goal scored) as default to not break the game flow
        return False

# Run the game and exit with return value
if __name__ == "__main__":
    import sys
    
    # Get player roles from command line arguments if provided
    goalkeeper = sys.argv[1] if len(sys.argv) > 1 else "p1"
    attacker = sys.argv[2] if len(sys.argv) > 2 else "p2"
    
    # Initialize pygame (this will also load images after display is set)
    init_soccer_pygame()
    
    # Run penalty shootout with player roles
    result = run_penalty_shootout(goalkeeper, attacker)
    print(result)  # Print the result (True or False)
    sys.exit(0 if result else 1)  # Exit code 0 for saved (True), 1 for not saved (False)
