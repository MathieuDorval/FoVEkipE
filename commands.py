#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______     ______     __    __     __    __     ______     __   __     _____     ______    
#   /\  ___\   /\  __ \   /\ "-./  \   /\ "-./  \   /\  __ \   /\ "-.\ \   /\  __-.  /\  ___\   
#   \ \ \____  \ \ \/\ \  \ \ \-./\ \  \ \ \-./\ \  \ \  __ \  \ \ \-.  \  \ \ \/\ \ \ \___  \  
#    \ \_____\  \ \_____\  \ \_\ \ \_\  \ \_\ \ \_\  \ \_\ \_\  \ \_\\"\_\  \ \____-  \/\_____\ 
#     \/_____/   \/_____/   \/_/  \/_/   \/_/  \/_/   \/_/\/_/   \/_/ \/_/   \/____/   \/_____/
#   (version 14/09)
#   -> Manages keyboard and controller inputs

import pygame
import settings
import math

def init_joysticks():
    """
    Initialise toutes les manettes connectées.
    """
    pygame.joystick.init()
    gamepads = []
    for i in range(pygame.joystick.get_count()):
        gamepad = pygame.joystick.Joystick(i)
        gamepad.init()
        gamepads.append(gamepad)
    if not gamepads:
        print("FoVEkipE INFO: No gamepad connected. Using keyboard controls.")
    else:
        print(f"FoVEkipE INFO: {len(gamepads)} gamepad(s) connected.")
    return gamepads

def get_menu_inputs(gamepads):
    """
    Gère les commandes pour le menu.
    """
    actions = {
        'map_nav_y': 0,
        'map_rotate_x': 0,
        'open_settings': False,
        'p1_animal_nav': 0,
        'p2_animal_nav': 0,
        'p3_animal_nav': 0,
        'p4_animal_nav': 0,
        'p1_toggle_status': False,
        'p2_toggle_status': False,
        'p3_toggle_status': False,
        'p4_toggle_status': False,
        'p1_toggle_role': False,
        'p2_toggle_role': False,
        'p3_toggle_role': False,
        'p4_toggle_role': False,
        'p1_confirm': 0.0,
        'p2_confirm': 0.0,
        'p3_confirm': 0.0,
        'p4_confirm': 0.0,
    }
    
    keys = pygame.key.get_pressed()
    num_gamepads = len(gamepads)
    
    if num_gamepads > 0 and gamepads[0].get_numhats() > 0:
        hat_x, hat_y = gamepads[0].get_hat(0)
        actions['map_rotate_x']     = hat_x
        actions['map_nav_y']        = hat_y
    else:
        actions['map_nav_y']        = keys[pygame.K_y] - keys[pygame.K_h]
        actions['map_rotate_x']     = keys[pygame.K_j] - keys[pygame.K_g]

    if num_gamepads > 0 and gamepads[0].get_numbuttons() > 6:
        actions['open_settings']    = gamepads[0].get_button(6)
    else:
        actions['open_settings']    = keys[pygame.K_BACKSPACE]

    if num_gamepads == 0:
        actions['p1_animal_nav']    = keys[pygame.K_d] - keys[pygame.K_q]
        actions['p1_toggle_status'] = keys[pygame.K_z]
        actions['p1_toggle_role']   = keys[pygame.K_s]
        actions['p1_confirm']       = 1.0 if keys[pygame.K_SPACE] else 0.0
        
        actions['p2_animal_nav']    = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        actions['p2_toggle_status'] = keys[pygame.K_UP]
        actions['p2_toggle_role']   = keys[pygame.K_DOWN]
        actions['p2_confirm']       = 1.0 if keys[pygame.K_RETURN] else 0.0

    elif num_gamepads == 1:
        g1 = gamepads[0]
        axis_0 = g1.get_axis(0); actions['p1_animal_nav']       = 1 if axis_0 > 0.5 else -1 if axis_0 < -0.5 else 0
        if g1.get_numbuttons() > 8: actions['p1_toggle_status'] = g1.get_button(8)
        if g1.get_numbuttons() > 4: actions['p1_toggle_role']   = g1.get_button(4)
        if g1.get_numaxes() > 4: actions['p1_confirm']          = (g1.get_axis(4) + 1) / 2

        axis_2 = g1.get_axis(2); actions['p2_animal_nav']       = 1 if axis_2 > 0.5 else -1 if axis_2 < -0.5 else 0
        if g1.get_numbuttons() > 9: actions['p2_toggle_status'] = g1.get_button(9)
        if g1.get_numbuttons() > 5: actions['p2_toggle_role']   = g1.get_button(5)
        if g1.get_numaxes() > 5: actions['p2_confirm']          = (g1.get_axis(5) + 1) / 2
    
    elif num_gamepads >= 2:
        g1, g2 = gamepads[0], gamepads[1]
        axis_0_g1 = g1.get_axis(0); actions['p1_animal_nav']    = 1 if axis_0_g1 > 0.5 else -1 if axis_0_g1 < -0.5 else 0
        if g1.get_numbuttons() > 8: actions['p1_toggle_status'] = g1.get_button(8)
        if g1.get_numbuttons() > 4: actions['p1_toggle_role']   = g1.get_button(4)
        if g1.get_numaxes() > 4: actions['p1_confirm']          = (g1.get_axis(4) + 1) / 2
        
        axis_2_g1 = g1.get_axis(2); actions['p3_animal_nav']    = 1 if axis_2_g1 > 0.5 else -1 if axis_2_g1 < -0.5 else 0
        if g1.get_numbuttons() > 9: actions['p3_toggle_status'] = g1.get_button(9)
        if g1.get_numbuttons() > 5: actions['p3_toggle_role']   = g1.get_button(5)
        if g1.get_numaxes() > 5: actions['p3_confirm']          = (g1.get_axis(5) + 1) / 2

        axis_0_g2 = g2.get_axis(0); actions['p2_animal_nav']    = 1 if axis_0_g2 > 0.5 else -1 if axis_0_g2 < -0.5 else 0
        if g2.get_numbuttons() > 8: actions['p2_toggle_status'] = g2.get_button(8)
        if g2.get_numbuttons() > 4: actions['p2_toggle_role']   = g2.get_button(4)
        if g2.get_numaxes() > 4: actions['p2_confirm']          = (g2.get_axis(4) + 1) / 2

        axis_2_g2 = g2.get_axis(2); actions['p4_animal_nav']    = 1 if axis_2_g2 > 0.5 else -1 if axis_2_g2 < -0.5 else 0
        if g2.get_numbuttons() > 9: actions['p4_toggle_status'] = g2.get_button(9)
        if g2.get_numbuttons() > 5: actions['p4_toggle_role']   = g2.get_button(5)
        if g2.get_numaxes() > 5: actions['p4_confirm']          = (g2.get_axis(5) + 1) / 2

    return actions

def get_player_action(player_id, gamepads, rotation_angle):
    """
    Gère les commandes pendant le jeu.
    """
    vx, vy, intensity = 0, 0, 0
    num_gamepads = len(gamepads)

    def get_axis(pad, index, default=0.0): return pad.get_axis(index) if pad.get_numaxes() > index else default
    def get_trigger(pad, index): return (get_axis(pad, index, -1) + 1) / 2

    if num_gamepads == 0:
        keys = pygame.key.get_pressed()
        if player_id == 1:
            vy += keys[pygame.K_s] - keys[pygame.K_z]
            vx += keys[pygame.K_d] - keys[pygame.K_q]
            if keys[pygame.K_SPACE]: intensity = 1.0
        elif player_id == 2:
            vy += keys[pygame.K_DOWN] - keys[pygame.K_UP]
            vx += keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            if keys[pygame.K_RETURN]: intensity = 1.0
    else:
        if player_id == 1:
            vx, vy, intensity = get_axis(gamepads[0], 0), get_axis(gamepads[0], 1), get_trigger(gamepads[0], 4)
        elif player_id == 2:
            g = gamepads[1] if num_gamepads > 1 else gamepads[0]
            ax, ay, trig = (0, 1, 4) if num_gamepads > 1 else (2, 3, 5)
            vx, vy, intensity = get_axis(g, ax), get_axis(g, ay), get_trigger(g, trig)
        elif player_id == 3:
            vx, vy, intensity = get_axis(gamepads[0], 2), get_axis(gamepads[0], 3), get_trigger(gamepads[0], 5)
        elif player_id == 4 and num_gamepads > 1:
            vx, vy, intensity = get_axis(gamepads[1], 2), get_axis(gamepads[1], 3), get_trigger(gamepads[1], 5)

    if math.sqrt(vx**2 + vy**2) < settings.JOYSTICK_DEADZONE: vx, vy = 0, 0
    if vx == 0 and vy == 0: intensity = 0

    direction_vector = pygame.Vector2(vx, vy)
    if direction_vector.length_squared() > 0:
        direction_vector.normalize_ip()
        direction_vector.rotate_ip(-45)
        direction_vector = direction_vector.rotate_rad(-rotation_angle)

    return {'direction': direction_vector, 'intensity': intensity}

def get_camera_action(gamepads):
    """
    Gère les commandes de rotation de map.
    """
    rotation = 0
    if gamepads and gamepads[0].get_numhats() > 0:
        rotation = gamepads[0].get_hat(0)[0]
    else:
        keys = pygame.key.get_pressed()
        rotation = keys[pygame.K_j] - keys[pygame.K_g]
    return {'rotation': rotation}

def get_confirm_action(gamepads):
    """
    Détecte une action de confirmation.
    """
    if gamepads:
        for gamepad in gamepads:
            if gamepad.get_numaxes() > 4 and gamepad.get_axis(4) > 0.5:
                 return True
            if gamepad.get_numaxes() > 5 and gamepad.get_axis(5) > 0.5:
                 return True
    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            return True
    return False