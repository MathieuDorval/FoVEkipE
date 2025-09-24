#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    __    __     ______     __   __     __  __    
#   /\ "-./  \   /\  ___\   /\ "-.\ \   /\ \/\ \   
#   \ \ \-./\ \  \ \  __\   \ \ \-.  \  \ \ \_\ \  
#    \ \_\ \ \_\  \ \_____\  \ \_\\"\_\  \ \_____\ 
#     \/_/  \/_/   \/_____/   \/_/ \/_/   \/_____/ 
#   (version 14/09)
#   -> Manage the main menu

import pygame
import settings
from maps import generate_terrain
from renderer import MapRenderer
from ui import draw_menu
from animals import ANIMALS
from commands import get_menu_inputs
from menu_settings import menu_settings_loop

def menu_loop(screen, clock, gamepads, game_settings):
    """
    Gère l'écran de menu principal.
    """
    animal_names = [animal['name'] for animal in ANIMALS]
    
    p_ready = {}
    last_inputs = {}
    map_rotation_angle = 0.0 
    role_error_message = ""
    role_error_timer = 0.0
    is_first_frame = True

    selected_map_name = game_settings['map_name']
    surface_data = generate_terrain(selected_map_name, settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
    map_renderer = MapRenderer(screen, screen.get_rect(), surface_data, game_settings)

    selecting = True
    while selecting:
        dt = clock.tick(settings.FPS) / 1000.0

        if role_error_timer > 0:
            role_error_timer -= dt
            if role_error_timer <= 0: role_error_message = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False, 0

        menu_actions = get_menu_inputs(gamepads)
        max_players = 4 if len(gamepads) > 1 else 2

        if menu_actions['map_nav_y'] != 0 and last_inputs.get('map_nav_y', 0) == 0:
            direction = menu_actions['map_nav_y']
            game_settings['map_index'] = (game_settings['map_index'] + direction) % len(settings.AVAILABLE_MAPS)
            game_settings['map_name'] = settings.AVAILABLE_MAPS[game_settings['map_index']]
        
        map_rotation_angle -= menu_actions['map_rotate_x'] * settings.ROTATION_SPEED * 2

        if menu_actions['open_settings'] and not last_inputs.get('open_settings', False):
            if not is_first_frame: menu_settings_loop(screen, clock, gamepads, game_settings)
        
        for i in range(1, max_players + 1):
            is_player_ready = p_ready.get(i, False)
            is_player_active = game_settings[f'p{i}_status'] != "INACTIVE"
            
            confirm_pressed = menu_actions[f'p{i}_confirm'] > 0.5
            is_new_press = confirm_pressed and not last_inputs.get(f'p{i}_confirm', False)

            if is_new_press and not is_first_frame:
                human_players = [pid for pid in range(1, max_players + 1) if game_settings[f'p{pid}_status'] == "PLAYER"]
                if len(human_players) > 0:
                    if game_settings[f'p{i}_status'] == "PLAYER":
                        ready_human_players = [pid for pid in human_players if p_ready.get(pid, False)]
                        is_last_one_to_ready = (len(human_players) - len(ready_human_players) == 1) and not is_player_ready
                        if is_last_one_to_ready:
                            active_players = [p for p in range(1, max_players + 1) if game_settings[f'p{p}_status'] != "INACTIVE"]
                            roles = [game_settings[f'p{p}_role'] for p in active_players]
                            if roles.count('predator') == 0:
                                role_error_message = "at least one predator is needed !"
                                role_error_timer = 3.0
                            elif roles.count('prey') == 0:
                                role_error_message = "at least one prey is needed !"
                                role_error_timer = 3.0
                            else: p_ready[i] = not p_ready.get(i, False)
                        else: p_ready[i] = not p_ready.get(i, False)
                else:
                    if i == 1:
                        active_players = [p for p in range(1, max_players + 1) if game_settings[f'p{p}_status'] != "INACTIVE"]
                        roles = [game_settings[f'p{p}_role'] for p in active_players]
                        if roles.count('predator') == 0:
                                role_error_message = "at least one predator is needed !"
                                role_error_timer = 3.0
                        elif roles.count('prey') == 0:
                                role_error_message = "at least one prey is needed !"
                                role_error_timer = 3.0
                        else: p_ready[1] = True

            if menu_actions[f'p{i}_toggle_status'] and not last_inputs.get(f'p{i}_toggle_status', False):
                if not is_player_ready:
                    statuses = ["PLAYER", "AI", "INACTIVE"] if i > 2 else ["PLAYER", "AI"]
                    current_status = game_settings[f'p{i}_status']
                    current_idx = statuses.index(current_status) if current_status in statuses else 0
                    new_status = statuses[(current_idx + 1) % len(statuses)]
                    game_settings[f'p{i}_status'] = new_status

            if not is_player_ready and is_player_active:
                animal_nav = menu_actions[f'p{i}_animal_nav']
                if animal_nav != 0 and last_inputs.get(f'p{i}_animal_nav', 0) == 0:
                    game_settings[f'p{i}_animal_index'] = (game_settings[f'p{i}_animal_index'] + animal_nav) % len(animal_names)
                    game_settings[f'p{i}_animal_name'] = animal_names[game_settings[f'p{i}_animal_index']]
                
                if menu_actions[f'p{i}_toggle_role'] and not last_inputs.get(f'p{i}_toggle_role', False):
                    current_role = game_settings[f'p{i}_role']
                    game_settings[f'p{i}_role'] = 'prey' if current_role == 'predator' else 'predator'

        last_inputs = {
            'map_nav_y': menu_actions['map_nav_y'],
            'open_settings': menu_actions['open_settings'],
            'p1_animal_nav': menu_actions['p1_animal_nav'],
            'p2_animal_nav': menu_actions['p2_animal_nav'],
            'p3_animal_nav': menu_actions['p3_animal_nav'],
            'p4_animal_nav': menu_actions['p4_animal_nav'],
            'p1_toggle_status': menu_actions['p1_toggle_status'],
            'p2_toggle_status': menu_actions['p2_toggle_status'],
            'p3_toggle_status': menu_actions['p3_toggle_status'],
            'p4_toggle_status': menu_actions['p4_toggle_status'],
            'p1_toggle_role': menu_actions['p1_toggle_role'],
            'p2_toggle_role': menu_actions['p2_toggle_role'],
            'p3_toggle_role': menu_actions['p3_toggle_role'],
            'p4_toggle_role': menu_actions['p4_toggle_role'],
            'p1_confirm': menu_actions['p1_confirm'] > 0.5,
            'p2_confirm': menu_actions['p2_confirm'] > 0.5,
            'p3_confirm': menu_actions['p3_confirm'] > 0.5,
            'p4_confirm': menu_actions['p4_confirm'] > 0.5,
        }
        
        is_first_frame = False

        human_players = [pid for pid in range(1, max_players + 1) if game_settings[f'p{pid}_status'] == "PLAYER"]
        if (len(human_players) > 0 and all(p_ready.get(pid, False) for pid in human_players)) or \
           (len(human_players) == 0 and p_ready.get(1, False)):
            return True, map_rotation_angle

        if game_settings['map_name'] != selected_map_name:
            selected_map_name = game_settings['map_name']
            surface_data = generate_terrain(selected_map_name, settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
            map_renderer.update_map_data(surface_data, game_settings)
        screen.fill(settings.BLACK)
        map_renderer.draw_map(map_rotation_angle, game_settings)
        draw_menu(screen, game_settings, p_ready, role_error_message)
        pygame.display.flip()

    return False, 0