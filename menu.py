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
    p_ready = {i: False for i in range(1, 5)}
    player_focus = {i: 1 for i in range(1, 5)} # 0: role/status, 1: animal grid
    player_cursors = {i: game_settings.get(f'p{i}_animal_index', 0) for i in range(1, 5)}
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
        
        # --- Handle General Menu Actions ---
        if menu_actions['map_nav_y'] != 0 and last_inputs.get('map_nav_y', 0) == 0:
            direction = menu_actions['map_nav_y']
            game_settings['map_index'] = (game_settings['map_index'] + direction) % len(settings.AVAILABLE_MAPS)
            game_settings['map_name'] = settings.AVAILABLE_MAPS[game_settings['map_index']]
        
        map_rotation_angle -= menu_actions['map_rotate_x'] * settings.ROTATION_SPEED * 2

        if menu_actions['open_settings'] and not last_inputs.get('open_settings', False):
            if not is_first_frame: 
                menu_settings_loop(screen, clock, gamepads, game_settings)

        # --- Handle Player-Specific Actions ---
        for i in range(1, 5):
            # Status cycling (INACTIVE -> PLAYER -> AI)
            if menu_actions[f'p{i}_toggle_active'] and not last_inputs.get(f'p{i}_toggle_active', False):
                current_status = game_settings[f'p{i}_status']
                if current_status == "INACTIVE":
                    game_settings[f'p{i}_status'] = "PLAYER"
                    player_focus[i] = 1 
                elif current_status == "PLAYER" and game_settings['ai_enabled']:
                    game_settings[f'p{i}_status'] = "AI"
                else:
                    game_settings[f'p{i}_status'] = "INACTIVE"
                p_ready[i] = False # Reset ready state on change

            if game_settings[f'p{i}_status'] == "INACTIVE": continue

            is_human = game_settings[f'p{i}_status'] == "PLAYER"
            is_new_confirm = menu_actions[f'p{i}_confirm'] and not last_inputs.get(f'p{i}_confirm', False)
            focus = player_focus.get(i, 1)
            is_ready = p_ready.get(i, False)

            if is_human and is_new_confirm:
                if is_ready:
                    p_ready[i] = False
                elif focus == 1: 
                    game_settings[f'p{i}_animal_index'] = player_cursors[i]
                    game_settings[f'p{i}_animal_name'] = ANIMALS[player_cursors[i]]['name']
                    player_focus[i] = 0 
                elif focus == 0: 
                    p_ready[i] = True
            
            # Navigation for non-ready humans and all AIs
            if not (is_ready and is_human):
                nav_x = menu_actions[f'p{i}_nav_x']
                nav_y = menu_actions[f'p{i}_nav_y']
                last_nav_x = last_inputs.get(f'p{i}_nav_x', 0)
                last_nav_y = last_inputs.get(f'p{i}_nav_y', 0)

                if focus == 0: # Role selection
                    current_role = game_settings[f'p{i}_role']
                    if nav_x > 0 and last_nav_x == 0 and current_role == 'predator':
                        game_settings[f'p{i}_role'] = 'prey'
                    elif nav_x < 0 and last_nav_x == 0 and current_role == 'prey':
                        game_settings[f'p{i}_role'] = 'predator'
                        
                    if nav_y > 0 and last_nav_y == 0:
                        player_focus[i] = 1 
                
                elif focus == 1: # Animal selection
                    icons_per_row = 8
                    cursor = player_cursors[i]

                    if nav_y != 0 and last_nav_y == 0:
                        if nav_y < 0: # Up
                            if cursor // icons_per_row == 0: # If on the top row
                                player_focus[i] = 0
                            else:
                                player_cursors[i] -= icons_per_row
                        else: # Down
                            new_cursor = cursor + icons_per_row
                            if new_cursor < len(ANIMALS):
                                player_cursors[i] = new_cursor
                    
                    if nav_x != 0 and last_nav_x == 0:
                        row = cursor // icons_per_row
                        new_cursor = cursor + nav_x
                        if 0 <= new_cursor < len(ANIMALS) and new_cursor // icons_per_row == row:
                             player_cursors[i] = new_cursor
                            
        last_inputs = menu_actions.copy()
        is_first_frame = False

        # --- Game Launch Logic ---
        active_players = [p for p in range(1, 5) if game_settings[f'p{p}_status'] != "INACTIVE"]
        should_launch = False
        
        if active_players:
            human_players = [p for p in active_players if game_settings[f'p{p}_status'] == "PLAYER"]
            
            if human_players: # If there are human players
                if all(p_ready.get(p, False) for p in human_players):
                    should_launch = True
            else: # If only AIs
                first_active_ai_id = min(active_players)
                if menu_actions[f'p{first_active_ai_id}_confirm'] and not last_inputs.get(f'p{first_active_ai_id}_confirm', False):
                    should_launch = True

        if should_launch:
            roles = [game_settings[f'p{p}_role'] for p in active_players]
            if len(active_players) < 2:
                role_error_message = "Au moins 2 joueurs sont requis !"; role_error_timer = 3.0
                p_ready = {p: False for p in range(1, 5)} # Un-ready everyone
            elif roles.count('predator') == 0:
                role_error_message = "Au moins un prédateur est requis !"; role_error_timer = 3.0
                p_ready = {p: False for p in range(1, 5)}
            elif roles.count('prey') == 0:
                role_error_message = "Au moins une proie est requise !"; role_error_timer = 3.0
                p_ready = {p: False for p in range(1, 5)}
            else:
                 return True, map_rotation_angle

        if game_settings['map_name'] != selected_map_name:
            selected_map_name = game_settings['map_name']
            surface_data = generate_terrain(selected_map_name, settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
            map_renderer.update_map_data(surface_data, game_settings)
            
        screen.fill(settings.BLACK)
        map_renderer.draw_map(map_rotation_angle, game_settings)
        draw_menu(screen, game_settings, p_ready, player_focus, player_cursors, role_error_message)
        pygame.display.flip()

    return False, 0

