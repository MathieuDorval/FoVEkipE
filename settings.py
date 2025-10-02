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
FULLSCREEN              = True # Mettre à True pour lancer en plein écran
FPS                     = 60    # update par seconde de la physique

# --- COLOR ---
BLACK                   = (0, 0, 0)
WHITE                   = (255, 255, 255)
SURFACE_COLOR           = (120, 100, 150)
PLAYER_COLORS = {
    1: {'predator': (231, 76, 60),  'prey': (155, 89, 182)}, # P1: Red vs Purple
    2: {'predator': (241, 196, 15), 'prey': (52, 152, 219)},  # P2: Yellow vs Blue
    3: {'predator': (230, 126, 34), 'prey': (46, 204, 113)},  # P3: Orange vs Green
    4: {'predator': (192, 57, 43),  'prey': (26, 188, 156)}   # P4: Dark Red vs Teal
}
COLOR_PREDATOR          = (220, 40, 40)
COLOR_PREY              = (47, 173, 72)

# --- MAP ---
MAP_POINTS              = 100   # nombre de point dans la matrice
MAP_WIDTH_METERS        = 15
MAP_MAX_HEIGHT_RATIO    = 0.1   # hauteur max en % de longueur de map
AVAILABLE_MAPS          = ["Default", "Flat", "Hills", "Plain", "Mountain", "MatLab"]
SELECTED_MAP            = "Default"
ROTATION_SPEED          = 0.05
ISO_ANGLE               = math.radians(30)
Z_BOOST_FACTOR          = 6.0   # mutiplicateur de hauteur de map (visuel)
PLAYER_Z_OFFSET         = 0.05
MAX_SLOPE               = 30    # pente max (en %) d'une map
POINT_SCALE             = 8

# --- JOSYTICKS ---
JOYSTICK_DEADZONE = 0.15

# --- PHYSICS ---
GRAVITY = 9.81
SLOPE_CORRECTION        = True  # est ce qu'on applique la logique de pente optimale dans la physique ou non
BRAKE_CORRECTION        = True  # est ce qu'on applique la logique de freinage dans la physique ou non

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


