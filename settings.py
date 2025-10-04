#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    ______     ______     ______   ______   __     __   __     ______     ______    
#   /\  ___\   /\  ___\   /\__  _\ /\__  _\ /\ \   /\ "-.\ \   /\  ___\   /\  ___\   
#   \ \___  \  \ \  __\   \/_/\ \/ \/_/\ \/ \ \ \  \ \ \-.  \  \ \ \__ \  \ \___  \  
#    \/\_____\  \ \_____\    \ \_\    \ \_\  \ \_\  \ \_\\"\_\  \ \_____\  \/\_____\ 
#     \/_____/   \/_____/     \/_/     \/_/   \/_/   \/_/ \/_/   \/_____/   \/_____/
#   (version 04/10)
#   → All game constants and default values

import math

# --- LANGUAGE ---
LANGUAGE                = "en" # "fr" or "en"

# --- SCREEN ---
SCREEN_WIDTH            = 1400
SCREEN_HEIGHT           = 900
FULLSCREEN              = True  # Display the game full-screen without borders
DISPLAY_SCREEN          = 0     # 0 for primary screen, 1 for secondary, etc.
FPS                     = 60    # Update per second

# --- COLOR ---
BLACK                   = (0, 0, 0)
WHITE                   = (255, 255, 255)
# Bright gradient for the main menu
GRADIENT_COLOR_TOP      = (4, 1, 32)
GRADIENT_COLOR_MIDDLE   = (31, 1, 60)
GRADIENT_COLOR_BOTTOM   = (68, 1, 93)
# Dark gradient for in-game, settings, etc.
GRADIENT_DARK_COLOR_TOP = (2, 0, 16)
GRADIENT_DARK_COLOR_MIDDLE= (15, 0, 30)
GRADIENT_DARK_COLOR_BOTTOM= (34, 0, 46)
# Time bar gradient
TIME_BAR_COLOR_START    = (46, 204, 113)
TIME_BAR_COLOR_MIDDLE   = (241, 196, 15)
TIME_BAR_COLOR_END      = (231, 76, 60)
# Player colors
PLAYER_COLORS = {
    1: {'predator': (231, 76, 60),  'prey': (155, 89, 182)},
    2: {'predator': (241, 196, 15), 'prey': (52, 152, 219)},
    3: {'predator': (230, 126, 34), 'prey': (46, 204, 113)},
    4: {'predator': (192, 57, 43),  'prey': (26, 188, 156)}
}
COLOR_PREDATOR          = (220, 40, 40)
COLOR_PREY              = (47, 173, 72)

# --- MAP ---
MAP_POINTS              = 100   # Map resolution (in number of points)
MAP_WIDTH_METERS        = 15    # Map width/height in meters
MAP_MAX_HEIGHT_RATIO    = 0.1   # Maximum map height (as a percentage)
AVAILABLE_MAPS          = ["Default", "Flat", "Hills", "Plain", "Mountain", "MatLab"]
SELECTED_MAP            = "Default"
ROTATION_SPEED          = 0.05  # Map rotation speed
ISO_ANGLE               = math.radians(30)  # Map viewing angle
Z_BOOST_FACTOR          = 6.0   # Visual amplification of map height
PLAYER_Z_OFFSET         = 0.05  # Visual increase of player position ()
MAX_SLOPE               = 30    # Maximum map slope, as a percentage
POINT_SCALE             = 8     # Player size

# --- JOSYTICKS ---
JOYSTICK_DEADZONE       = 0.15

# --- PHYSICS ---
GRAVITY                 = 9.81
SLOPE_CORRECTION        = True
BRAKE_CORRECTION        = True
VC_SPEED                = False
WAC_RATIO               = 1.0

# --- GAME RULES ---
ROUND_DURATION          = 30    # In seconds
WINNING_SCORE           = 3
TIME_KILLCAM            = 3.0   # In seconds
KILLCAM_N_PARTICLES     = 50
PREDATOR_PLAYER         = 1
MIN_DISTANCE_PREDATOR   = 0.4   # Distance between prey and predator at launch (as a percentage)
COLLISION_DISTANCE      = 0.04  # Distance between prey and predator to catch (as a percentage)
N_ANIMALS_TO_SELECT     = 9     # Number of animals to display
PLAYER1_ANIMAL          = "Wolf"
PLAYER2_ANIMAL          = "Deer"
PLAYER3_ANIMAL          = "Deer"
PLAYER4_ANIMAL          = "Deer"
AI_ENABLED              = False
INFINITY_MAP            = False
VIBRATION_MODE          = False
VIBRATION_DISTANCE_RATIO= 0.5   # Distance from which vibrations start (as a percentage)

