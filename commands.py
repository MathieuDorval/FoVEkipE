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
        'map_nav_y': 0, 'map_rotate_x': 0, 'open_settings': False,
        'p1_nav_x': 0, 'p1_nav_y': 0, 'p1_confirm': False, 'p1_toggle_active': False,
        'p2_nav_x': 0, 'p2_nav_y': 0, 'p2_confirm': False, 'p2_toggle_active': False,
        'p3_nav_x': 0, 'p3_nav_y': 0, 'p3_confirm': False, 'p3_toggle_active': False,
        'p4_nav_x': 0, 'p4_nav_y': 0, 'p4_confirm': False, 'p4_toggle_active': False,
    }

    def get_axis(pad, index, deadzone=0.5):
        val = pad.get_axis(index) if pad.get_numaxes() > index else 0.0
        return 1 if val > deadzone else -1 if val < -deadzone else 0

    def get_trigger_confirm(pad, index):
        if pad.get_numaxes() > index:
            axis_val = pad.get_axis(index)
            # Les gâchettes sur certains contrôleurs (ex: Xbox) vont de -1 (relâché) à 1 (pressé)
            # D'autres de 0 à 1. On normalise.
            return (axis_val + 1) / 2 > 0.5
        return False
    
    def get_button(pad, index):
        return pad.get_button(index) if pad.get_numbuttons() > index else False

    keys = pygame.key.get_pressed()
    num_gamepads = len(gamepads)

    # --- Commandes générales du menu (map, settings) ---
    if num_gamepads > 0 and gamepads[0].get_numhats() > 0:
        hat_x, hat_y = gamepads[0].get_hat(0)
        actions['map_rotate_x'] = hat_x
        actions['map_nav_y'] = hat_y
    else:
        actions['map_nav_y'] = keys[pygame.K_y] - keys[pygame.K_h]
        actions['map_rotate_x'] = keys[pygame.K_j] - keys[pygame.K_g]

    if num_gamepads > 0:
        actions['open_settings'] = get_button(gamepads[0], 6) # Bouton "Select" / "View"
    else:
        actions['open_settings'] = keys[pygame.K_BACKSPACE]

    # --- Commandes des joueurs ---
    if num_gamepads == 0:
        actions['p1_nav_x'] = keys[pygame.K_d] - keys[pygame.K_q]
        actions['p1_nav_y'] = keys[pygame.K_s] - keys[pygame.K_z]
        actions['p1_confirm'] = keys[pygame.K_SPACE]
        actions['p2_nav_x'] = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        actions['p2_nav_y'] = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        actions['p2_confirm'] = keys[pygame.K_RETURN]

    elif num_gamepads == 1:
        g1 = gamepads[0]
        actions['p1_nav_x'] = get_axis(g1, 0)
        actions['p1_nav_y'] = get_axis(g1, 1)
        actions['p1_confirm'] = get_trigger_confirm(g1, 4) # LT
        actions['p2_nav_x'] = get_axis(g1, 2)
        actions['p2_nav_y'] = get_axis(g1, 3)
        actions['p2_confirm'] = get_trigger_confirm(g1, 5) # RT

    elif num_gamepads == 2:
        g1, g2 = gamepads[0], gamepads[1]
        actions['p1_nav_x'] = get_axis(g1, 0); actions['p1_nav_y'] = get_axis(g1, 1); actions['p1_confirm'] = get_trigger_confirm(g1, 4)
        actions['p2_nav_x'] = get_axis(g2, 0); actions['p2_nav_y'] = get_axis(g2, 1); actions['p2_confirm'] = get_trigger_confirm(g2, 4)
        actions['p3_nav_x'] = get_axis(g1, 2); actions['p3_nav_y'] = get_axis(g1, 3); actions['p3_confirm'] = get_trigger_confirm(g1, 5)
        actions['p4_nav_x'] = get_axis(g2, 2); actions['p4_nav_y'] = get_axis(g2, 3); actions['p4_confirm'] = get_trigger_confirm(g2, 5)
        
        actions['p3_toggle_active'] = get_button(g1, 9) # Click joystick droit M1
        actions['p4_toggle_active'] = get_button(g2, 9) # Click joystick droit M2

    elif num_gamepads == 3:
        g1, g2, g3 = gamepads[0], gamepads[1], gamepads[2]
        actions['p1_nav_x'] = get_axis(g1, 0); actions['p1_nav_y'] = get_axis(g1, 1); actions['p1_confirm'] = get_trigger_confirm(g1, 4) # P1: M1 Gauche
        actions['p2_nav_x'] = get_axis(g2, 0); actions['p2_nav_y'] = get_axis(g2, 1); actions['p2_confirm'] = get_trigger_confirm(g2, 4) # P2: M2 Gauche
        actions['p3_nav_x'] = get_axis(g3, 0); actions['p3_nav_y'] = get_axis(g3, 1); actions['p3_confirm'] = get_trigger_confirm(g3, 4) # P3: M3 Gauche
        actions['p4_nav_x'] = get_axis(g1, 2); actions['p4_nav_y'] = get_axis(g1, 3); actions['p4_confirm'] = get_trigger_confirm(g1, 5) # P4: M1 Droit
        
        actions['p3_toggle_active'] = get_button(g3, 8)  # Click joystick gauche M3
        actions['p4_toggle_active'] = get_button(g1, 9) # Click joystick droit M1

    elif num_gamepads >= 4:
        g1, g2, g3, g4 = gamepads[0], gamepads[1], gamepads[2], gamepads[3]
        actions['p1_nav_x'] = get_axis(g1, 0); actions['p1_nav_y'] = get_axis(g1, 1); actions['p1_confirm'] = get_trigger_confirm(g1, 4) # P1: M1 Gauche
        actions['p2_nav_x'] = get_axis(g2, 0); actions['p2_nav_y'] = get_axis(g2, 1); actions['p2_confirm'] = get_trigger_confirm(g2, 4) # P2: M2 Gauche
        actions['p3_nav_x'] = get_axis(g3, 0); actions['p3_nav_y'] = get_axis(g3, 1); actions['p3_confirm'] = get_trigger_confirm(g3, 4) # P3: M3 Gauche
        actions['p4_nav_x'] = get_axis(g4, 0); actions['p4_nav_y'] = get_axis(g4, 1); actions['p4_confirm'] = get_trigger_confirm(g4, 4) # P4: M4 Gauche
        
        actions['p3_toggle_active'] = get_button(g3, 8) # Click joystick gauche M3
        actions['p4_toggle_active'] = get_button(g4, 8) # Click joystick gauche M4

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
            
    elif num_gamepads == 1:
        g1 = gamepads[0]
        if player_id == 1:
            vx, vy, intensity = get_axis(g1, 0), get_axis(g1, 1), get_trigger(g1, 4) # Stick gauche, LT
        elif player_id == 2:
            vx, vy, intensity = get_axis(g1, 2), get_axis(g1, 3), get_trigger(g1, 5) # Stick droit, RT

    elif num_gamepads == 2:
        g1, g2 = gamepads[0], gamepads[1]
        if player_id == 1:
            vx, vy, intensity = get_axis(g1, 0), get_axis(g1, 1), get_trigger(g1, 4) # P1: M1 Gauche
        elif player_id == 2:
            vx, vy, intensity = get_axis(g2, 0), get_axis(g2, 1), get_trigger(g2, 4) # P2: M2 Gauche
        elif player_id == 3:
            vx, vy, intensity = get_axis(g1, 2), get_axis(g1, 3), get_trigger(g1, 5) # P3: M1 Droit
        elif player_id == 4:
            vx, vy, intensity = get_axis(g2, 2), get_axis(g2, 3), get_trigger(g2, 5) # P4: M2 Droit
            
    elif num_gamepads == 3:
        g1, g2, g3 = gamepads[0], gamepads[1], gamepads[2]
        if player_id == 1:
            vx, vy, intensity = get_axis(g1, 0), get_axis(g1, 1), get_trigger(g1, 4) # P1: M1 Gauche
        elif player_id == 2:
            vx, vy, intensity = get_axis(g2, 0), get_axis(g2, 1), get_trigger(g2, 4) # P2: M2 Gauche
        elif player_id == 3:
            vx, vy, intensity = get_axis(g3, 0), get_axis(g3, 1), get_trigger(g3, 4) # P3: M3 Gauche
        elif player_id == 4:
            vx, vy, intensity = get_axis(g1, 2), get_axis(g1, 3), get_trigger(g1, 5) # P4: M1 Droit

    elif num_gamepads >= 4:
        if player_id <= len(gamepads):
            g = gamepads[player_id - 1]
            vx, vy, intensity = get_axis(g, 0), get_axis(g, 1), get_trigger(g, 4) # Chaque joueur sur le stick gauche de sa manette

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
            if gamepad.get_numaxes() > 4 and (gamepad.get_axis(4) + 1) / 2 > 0.5: # LT
                 return True
            if gamepad.get_numaxes() > 5 and (gamepad.get_axis(5) + 1) / 2 > 0.5: # RT
                 return True
    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            return True
    return False
