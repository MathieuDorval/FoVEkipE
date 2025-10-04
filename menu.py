#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __    __     ______     __   __     __  __    
#   /\ "-./  \   /\  ___\   /\ "-.\ \   /\ \/\ \   
#   \ \ \-./\ \  \ \  __\   \ \ \-.  \  \ \ \_\ \  
#    \ \_\ \ \_\  \ \_____\  \ \_\\"\_\  \ \_____\ 
#     \/_/  \/_/   \/_____/   \/_/ \/_/   \/_____/ 
#   (version 04/10)
#   → Manage the main menu

import pygame
import settings
from maps import generate_terrain
from renderer import MapRenderer, draw_background
from ui import draw_menu
from animals import ANIMALS
from commands import get_menu_inputs
from menu_settings import menu_settings_loop
from language import get_text

def menu_loop(screen, clock, gamepads, game_settings):
    """
    Handle the main menu.
    """
    p_ready = {i: False for i in range(1, 5)}
    player_focus = {i: 1 for i in range(1, 5)}
    player_cursors = {i: game_settings.get(f'p{i}_animal_index', 0) for i in range(1, 5)}
    last_inputs = {}
    map_rotation_angle = 0.0 
    role_error_message = ""
    role_error_timer = 0.0
    is_first_frame = True
    panel_rects = {}

    selected_map_name = game_settings['map_name']
    surface_data = generate_terrain(selected_map_name, settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
    map_renderer = MapRenderer(screen, screen.get_rect(), surface_data, game_settings)

    selecting = True
    while selecting:
        dt = clock.tick(settings.FPS) / 1000.0
        should_launch = False

        if role_error_timer > 0:
            role_error_timer -= dt
            if role_error_timer <= 0: role_error_message = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False, 0, {}

        menu_actions = get_menu_inputs(gamepads)
        
        if menu_actions['map_nav_y'] != 0 and last_inputs.get('map_nav_y', 0) == 0:
            direction = menu_actions['map_nav_y']
            game_settings['map_index'] = (game_settings['map_index'] + direction) % len(settings.AVAILABLE_MAPS)
            game_settings['map_name'] = settings.AVAILABLE_MAPS[game_settings['map_index']]
        
        map_rotation_angle -= menu_actions['map_rotate_x'] * settings.ROTATION_SPEED * 2

        if menu_actions['open_settings'] and not last_inputs.get('open_settings', False):
            if not is_first_frame: 
                action = menu_settings_loop(screen, clock, gamepads, game_settings)
                if action == "QUIT":
                    return False, 0, {}

        for i in range(1, 5):
            if menu_actions[f'p{i}_toggle_active'] and not last_inputs.get(f'p{i}_toggle_active', False):
                current_status = game_settings[f'p{i}_status']
                if current_status == "INACTIVE":
                    game_settings[f'p{i}_status'] = "PLAYER"
                elif current_status == "PLAYER" and game_settings['ai_enabled']:
                    game_settings[f'p{i}_status'] = "AI"
                else:
                    game_settings[f'p{i}_status'] = "INACTIVE"
                p_ready[i] = False

            if game_settings[f'p{i}_status'] == "INACTIVE":
                continue

            is_human = game_settings[f'p{i}_status'] == "PLAYER"
            is_new_confirm = menu_actions[f'p{i}_confirm'] and not last_inputs.get(f'p{i}_confirm', False)
            focus = player_focus.get(i, 1)

            if is_human and p_ready.get(i, False):
                if is_new_confirm: p_ready[i] = False
                continue

            nav_x, nav_y = menu_actions[f'p{i}_nav_x'], menu_actions[f'p{i}_nav_y']
            last_nav_x, last_nav_y = last_inputs.get(f'p{i}_nav_x', 0), last_inputs.get(f'p{i}_nav_y', 0)
            
            if focus == 0:
                if nav_y > 0 and last_nav_y == 0: player_focus[i] = 1
                if nav_x != 0 and last_nav_x == 0:
                    if nav_x > 0:
                        game_settings[f'p{i}_role'] = 'prey'
                    elif nav_x < 0:
                        game_settings[f'p{i}_role'] = 'predator'

            elif focus == 1:
                if nav_y < 0 and last_nav_y == 0 and player_cursors[i] // 8 == 0: player_focus[i] = 0
                else:
                    icons_per_row = 8
                    cursor = player_cursors[i]
                    if nav_y != 0 and last_nav_y == 0:
                        new_cursor = cursor + (nav_y * icons_per_row)
                        if 0 <= new_cursor < len(ANIMALS): player_cursors[i] = new_cursor
                    if nav_x != 0 and last_nav_x == 0:
                        row = cursor // icons_per_row
                        new_cursor = cursor + nav_x
                        if 0 <= new_cursor < len(ANIMALS) and new_cursor // icons_per_row == row: player_cursors[i] = new_cursor

            if is_new_confirm:
                if is_human:
                    if focus == 1:
                        game_settings[f'p{i}_animal_index'] = player_cursors[i]
                        game_settings[f'p{i}_animal_name'] = ANIMALS[player_cursors[i]]['name']
                        player_focus[i] = 0
                    elif focus == 0:
                        p_ready[i] = True
                else:
                    if focus == 1:
                        game_settings[f'p{i}_animal_index'] = player_cursors[i]
                        game_settings[f'p{i}_animal_name'] = ANIMALS[player_cursors[i]]['name']
                        player_focus[i] = 0
                    elif focus == 0:
                        human_players = [p for p in range(1, 5) if game_settings[f'p{p}_status'] == "PLAYER"]
                        current_active_players = [p for p in range(1, 5) if game_settings[f'p{p}_status'] != "INACTIVE"]
                        if not human_players and current_active_players and i == min(current_active_players):
                            should_launch = True

        last_inputs = menu_actions.copy()
        is_first_frame = False

        human_players = [p for p in range(1, 5) if game_settings[f'p{p}_status'] == "PLAYER"]
        if human_players and all(p_ready.get(p, False) for p in human_players):
            should_launch = True

        if should_launch:
            final_active_players = [p for p in range(1, 5) if game_settings[f'p{p}_status'] != "INACTIVE"]
            for p_id in final_active_players:
                game_settings[f'p{p_id}_animal_index'] = player_cursors[p_id]
                game_settings[f'p{p_id}_animal_name'] = ANIMALS[player_cursors[p_id]]['name']

            roles = [game_settings[f'p{p}_role'] for p in final_active_players]
            
            error = False
            if len(final_active_players) < 2:
                role_error_message = get_text('error_min_2_players'); error = True
            elif 'predator' not in roles:
                role_error_message = get_text('error_min_1_predator'); error = True
            elif 'prey' not in roles:
                role_error_message = get_text('error_min_1_prey'); error = True
            elif game_settings['vibration_mode']:
                num_human_players = len([p for p in final_active_players if game_settings[f'p{p}_status'] == 'PLAYER'])
                if num_human_players > len(gamepads):
                    role_error_message = get_text('error_vibration_mode'); error = True

            if error:
                role_error_timer = 3.0
                p_ready = {p: False for p in range(1, 5)}
            else:
                 return True, map_rotation_angle, panel_rects

        if game_settings['map_name'] != selected_map_name:
            selected_map_name = game_settings['map_name']
            surface_data = generate_terrain(selected_map_name, settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
            map_renderer.update_map_data(surface_data, game_settings)
            
        draw_background(screen, dark=False)
        map_renderer.draw_map(map_rotation_angle, game_settings)
        panel_rects = draw_menu(screen, game_settings, p_ready, player_focus, player_cursors, role_error_message, len(gamepads))
        pygame.display.flip()

    return False, 0, {}