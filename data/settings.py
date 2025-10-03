#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______     ______     ______   ______   __     __   __     ______     ______    
#   /\  ___\   /\  ___\   /\__  _\ /\__  _\ /\ \   /\ "-.\ \   /\  ___\   /\  ___\   
#   \ \___  \  \ \  __\   \/_/\ \/ \/_/\ \/ \ \ \  \ \ \-.  \  \ \ \__ \  \ \___  \  
#    \/\_____\  \ \_____\    \ \_\    \ \_\  \ \_\  \ \_\\"\_\  \ \_____\  \/\_____\ 
#     \/_____/   \/_____/     \/_/     \/_/   \/_/   \/_/ \/_/   \/_____/   \/_____/
#   (version 14/09)
#   -> All game constants and default values

import math

# --- SCREEN ---
SCREEN_WIDTH            = 1400
SCREEN_HEIGHT           = 900
FULLSCREEN              = True
FPS                     = 60

# --- COLOR ---
BLACK                   = (0, 0, 0)
WHITE                   = (255, 255, 255)
SURFACE_COLOR           = (120, 100, 150)
PLAYER_COLORS = {
    1: {'predator': (231, 76, 60),  'prey': (155, 89, 182)},
    2: {'predator': (241, 196, 15), 'prey': (52, 152, 219)},
    3: {'predator': (230, 126, 34), 'prey': (46, 204, 113)},
    4: {'predator': (192, 57, 43),  'prey': (26, 188, 156)}
}
COLOR_PREDATOR          = (220, 40, 40)
COLOR_PREY              = (47, 173, 72)

# --- MAP ---
MAP_POINTS              = 100
MAP_WIDTH_METERS        = 15
MAP_MAX_HEIGHT_RATIO    = 0.1
AVAILABLE_MAPS          = ["Default", "Flat", "Hills", "Plain", "Mountain", "MatLab"]
SELECTED_MAP            = "Default"
ROTATION_SPEED          = 0.05
ISO_ANGLE               = math.radians(30)
Z_BOOST_FACTOR          = 6.0
PLAYER_Z_OFFSET         = 0.05
MAX_SLOPE               = 30
POINT_SCALE             = 8

# --- JOSYTICKS ---
JOYSTICK_DEADZONE       = 0.15
VIBRATION_DISTANCE_RATIO= 0.5

# --- PHYSICS ---
GRAVITY = 9.81
SLOPE_CORRECTION        = True
BRAKE_CORRECTION        = True
VC_SPEED                = False
INFINITY_MAP            = False
VIBRATION_MODE          = False

# --- GAME RULES ---
ROUND_DURATION          = 30
WINNING_SCORE           = 3
TIME_KILLCAM            = 3.0
KILLCAM_N_PARTICLES     = 50
PREDATOR_PLAYER         = 1
MIN_DISTANCE_PREDATOR   = 0.4
COLLISION_DISTANCE      = 0.04
N_ANIMALS_TO_SELECT     = 9
PLAYER1_ANIMAL          = "Wolf"
PLAYER2_ANIMAL          = "Deer"
PLAYER3_ANIMAL          = "Deer"
PLAYER4_ANIMAL          = "Deer"
AI_ENABLED              = False
WAC_RATIO               = 1.0

