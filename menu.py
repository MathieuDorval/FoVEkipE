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
    player_focus = {i: 0 for i in range(1, 5)}
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
        num_joysticks = len(gamepads)
        max_players = 4 if num_joysticks >= 2 else 2

        if menu_actions['map_nav_y'] != 0 and last_inputs.get('map_nav_y', 0) == 0:
            direction = menu_actions['map_nav_y']
            game_settings['map_index'] = (game_settings['map_index'] + direction) % len(settings.AVAILABLE_MAPS)
            game_settings['map_name'] = settings.AVAILABLE_MAPS[game_settings['map_index']]
        
        map_rotation_angle -= menu_actions['map_rotate_x'] * settings.ROTATION_SPEED * 2

        if menu_actions['open_settings'] and not last_inputs.get('open_settings', False):
            if not is_first_frame: menu_settings_loop(screen, clock, gamepads, game_settings)

        if num_joysticks >= 2:
            if menu_actions['p3_toggle_active'] and not last_inputs.get('p3_toggle_active', False):
                game_settings['p3_status'] = "PLAYER" if game_settings['p3_status'] == "INACTIVE" else "INACTIVE"
            if menu_actions['p4_toggle_active'] and not last_inputs.get('p4_toggle_active', False):
                game_settings['p4_status'] = "PLAYER" if game_settings['p4_status'] == "INACTIVE" else "INACTIVE"

        for i in range(1, max_players + 1):
            is_player_active = game_settings[f'p{i}_status'] != "INACTIVE"
            if not is_player_active: continue

            is_new_confirm_press = menu_actions[f'p{i}_confirm'] and not last_inputs.get(f'p{i}_confirm', False)

            if is_new_confirm_press and not is_first_frame:
                current_focus = player_focus.get(i, 0)
                
                if p_ready.get(i, False):
                    p_ready[i] = False
                elif current_focus == 2:
                    cursor_pos = player_cursors.get(i, 0)
                    game_settings[f'p{i}_animal_index'] = cursor_pos
                    game_settings[f'p{i}_animal_name'] = ANIMALS[cursor_pos]['name']
                    player_focus[i] = 1 
                else:
                    is_human_player = game_settings[f'p{i}_status'] == "PLAYER"
                    active_players_check = [p for p in range(1, max_players + 1) if game_settings[f'p{p}_status'] != "INACTIVE"]
                    human_players_check = [pid for pid in active_players_check if game_settings[f'p{pid}_status'] == "PLAYER"]
                    
                    if is_human_player:
                        temp_ready = p_ready.copy(); temp_ready[i] = True
                        is_last_human_to_ready = all(temp_ready.get(pid, False) for pid in human_players_check)

                        if is_last_human_to_ready:
                            roles = [game_settings[f'p{p}_role'] for p in active_players_check]
                            if roles.count('predator') == 0:
                                role_error_message = "Au moins un prédateur est requis !"; role_error_timer = 3.0
                                p_ready = {p: False for p in p_ready}
                            elif roles.count('prey') == 0:
                                role_error_message = "Au moins une proie est requise !"; role_error_timer = 3.0
                                p_ready = {p: False for p in p_ready}
                            else:
                                p_ready[i] = True
                        else:
                            p_ready[i] = True
                    elif len(human_players_check) == 0 and i == 1:
                           p_ready[1] = True

            is_human_player = game_settings[f'p{i}_status'] == "PLAYER"
            can_navigate = not (p_ready.get(i, False) and is_human_player)

            if can_navigate and is_player_active:
                nav_x = menu_actions[f'p{i}_nav_x']
                nav_y = menu_actions[f'p{i}_nav_y'] 
                current_focus = player_focus.get(i, 0)
                
                if nav_y != 0 and last_inputs.get(f'p{i}_nav_y', 0) == 0:
                    if current_focus == 2:
                        current_cursor_pos = player_cursors.get(i, 0)
                        icons_per_row = 5
                        current_row = current_cursor_pos // icons_per_row
                        num_rows = (len(ANIMALS) - 1) // icons_per_row + 1
                        
                        if nav_y < 0 and current_row == 0:
                            player_focus[i] = 1 
                            player_cursors[i] = game_settings[f'p{i}_animal_index']
                        elif nav_y > 0 and current_row < num_rows - 1:
                            new_cursor_pos = current_cursor_pos + icons_per_row
                            player_cursors[i] = min(len(ANIMALS) - 1, new_cursor_pos)
                        elif nav_y < 0 and current_row > 0:
                             player_cursors[i] -= icons_per_row
                    else:
                        new_focus = current_focus + nav_y
                        if 0 <= new_focus <= 2:
                            player_focus[i] = new_focus

                if nav_x != 0 and last_inputs.get(f'p{i}_nav_x', 0) == 0:
                    if current_focus == 0:
                        statuses = ["PLAYER", "AI"]
                        current_status = game_settings[f'p{i}_status']
                        current_idx = statuses.index(current_status) if current_status in statuses else 0
                        game_settings[f'p{i}_status'] = statuses[(current_idx + nav_x + len(statuses)) % len(statuses)]
                    elif current_focus == 1:
                        game_settings[f'p{i}_role'] = 'prey' if game_settings[f'p{i}_role'] == 'predator' else 'predator'
                    elif current_focus == 2:
                        current_cursor_pos = player_cursors.get(i, 0)
                        current_row = current_cursor_pos // 5
                        new_cursor_pos = current_cursor_pos + nav_x
                        if new_cursor_pos // 5 == current_row and 0 <= new_cursor_pos < len(ANIMALS):
                            player_cursors[i] = new_cursor_pos

        last_inputs = menu_actions.copy()
        is_first_frame = False

        active_players = [p for p in range(1, max_players + 1) if game_settings[f'p{p}_status'] != "INACTIVE"]
        human_players = [pid for pid in active_players if game_settings[f'p{pid}_status'] == "PLAYER"]
        
        should_launch = False
        if len(human_players) > 0 and all(p_ready.get(pid, False) for pid in human_players):
            should_launch = True
        elif len(human_players) == 0 and len(active_players) > 0 and p_ready.get(1, False):
            should_launch = True

        if should_launch:
            roles = [game_settings[f'p{p}_role'] for p in active_players]
            if roles.count('predator') == 0:
                role_error_message = "Au moins un prédateur est requis !"; role_error_timer = 3.0
                p_ready = {p: False for p in p_ready}
            elif roles.count('prey') == 0:
                role_error_message = "Au moins une proie est requise !"; role_error_timer = 3.0
                p_ready = {p: False for p in p_ready}
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