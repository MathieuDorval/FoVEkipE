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
#   (version 08/10)
#   → Gère le menu principal

import pygame
import settings
import math
from maps import generate_terrain
from renderer import MapRenderer, draw_background
from ui import draw_menu
from animals import ANIMALS
from commands import get_menu_inputs
from menu_settings import menu_settings_loop
from language import get_text

def _get_player_gamepad_map(num_gamepads):
    """(Interne) Retourne un dictionnaire mappant les ID des joueurs à leur index de manette."""
    if num_gamepads == 0: return {}
    if num_gamepads == 1: return {1: 0, 2: 0, 3: -1, 4: -1}
    if num_gamepads == 2: return {1: 0, 2: 1, 3: 0, 4: 1}
    if num_gamepads == 3: return {1: 0, 2: 1, 3: 2, 4: 0}
    if num_gamepads >= 4: return {1: 0, 2: 1, 3: 2, 4: 3}
    return {}

def menu_loop(screen, clock, gamepads, game_settings, player_unlocked_all):
    """
    Gère le menu principal.
    """
    p_ready = {i: False for i in range(1, 5)}
    player_focus = {i: 1 for i in range(1, 5)}
    player_cursors = {i: game_settings.get(f'p{i}_animal_index', 0) for i in range(1, 5)}
    player_hold_timers = {i: {'right': 0.0, 'left': 0.0} for i in range(1, 5)}
    last_inputs = {}
    map_rotation_angle = 0.0 
    role_error_message = ""
    role_error_timer = 0.0
    is_first_frame = True
    panel_rects = {}

    selected_map_name = game_settings['map_name']
    surface_data = generate_terrain(selected_map_name, settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
    map_renderer = MapRenderer(screen, screen.get_rect(), surface_data, game_settings)
    
    gamepad_map = _get_player_gamepad_map(len(gamepads))

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
                    if game_settings['vibration_mode']:
                        target_gamepad = gamepad_map.get(i)
                        is_conflict = False
                        if target_gamepad is not None and target_gamepad != -1:
                            active_players = [p for p in range(1, 5) if game_settings[f'p{p}_status'] != "INACTIVE"]
                            for p_id in active_players:
                                if gamepad_map.get(p_id) == target_gamepad:
                                    is_conflict = True
                                    break
                        if is_conflict:
                            continue
                    
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
            
            num_selectable_animals = len(ANIMALS) if player_unlocked_all.get(i, False) else min(len(ANIMALS), settings.N_ANIMALS_TO_SELECT)

            if focus == 0: # Navigation for role selection
                if nav_y > 0 and last_nav_y == 0: player_focus[i] = 1
                if nav_x != 0 and last_nav_x == 0:
                    game_settings[f'p{i}_role'] = 'prey' if nav_x > 0 else 'predator'

            elif focus == 1: # Navigation for animal selection
                
                # Unlock logic
                is_on_last_animal = (player_cursors[i] == num_selectable_animals - 1)
                if is_on_last_animal and nav_x == 1 and not player_unlocked_all[i]:
                    player_hold_timers[i]['right'] += dt
                    if player_hold_timers[i]['right'] >= 5.0:
                        player_unlocked_all[i] = True
                        player_hold_timers[i]['right'] = 0.0
                else:
                    player_hold_timers[i]['right'] = 0.0

                # Relock logic
                is_on_first_animal = (player_cursors[i] == 0)
                if is_on_first_animal and nav_x == -1 and player_unlocked_all[i]:
                    player_hold_timers[i]['left'] += dt
                    if player_hold_timers[i]['left'] >= 5.0:
                        player_unlocked_all[i] = False
                        player_hold_timers[i]['left'] = 0.0
                else:
                    player_hold_timers[i]['left'] = 0.0

                # Cursor movement logic
                num_rows = 2
                icons_per_row = math.ceil(num_selectable_animals / num_rows)
                if icons_per_row == 0: icons_per_row = 1
                
                if nav_y < 0 and last_nav_y == 0 and player_cursors[i] < icons_per_row: player_focus[i] = 0
                else:
                    cursor = player_cursors[i]
                    if nav_y != 0 and last_nav_y == 0:
                        new_cursor = cursor + (nav_y * icons_per_row)
                        if 0 <= new_cursor < num_selectable_animals: player_cursors[i] = new_cursor
                    if nav_x != 0 and last_nav_x == 0:
                        row = cursor // icons_per_row
                        new_cursor = cursor + nav_x
                        if 0 <= new_cursor < num_selectable_animals and new_cursor // icons_per_row == row: player_cursors[i] = new_cursor
                
                # Ensure cursor is within bounds after list change
                if player_cursors[i] >= num_selectable_animals:
                    player_cursors[i] = num_selectable_animals - 1

            if is_new_confirm:
                if is_human:
                    if focus == 1:
                        game_settings[f'p{i}_animal_index'] = player_cursors[i]
                        game_settings[f'p{i}_animal_name'] = ANIMALS[player_cursors[i]]['name']
                        player_focus[i] = 0
                    elif focus == 0:
                        p_ready[i] = True
                else: # AI logic
                    if focus == 1:
                        game_settings[f'p{i}_animal_index'] = player_cursors[i]
                        game_settings[f'p{i}_animal_name'] = ANIMALS[player_cursors[i]]['name']
                        player_focus[i] = 0
                    elif focus == 0:
                        # Auto-launch if only AIs are present and one confirms
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
            
            if error:
                role_error_timer = 3.0
                p_ready = {p: False for p in range(1, 5)}
            else:
                 return True, map_rotation_angle, panel_rects

        if game_settings['map_name'] != selected_map_name:
            selected_map_name = game_settings['map_name']
            surface_data = generate_terrain(selected_map_name, settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
            map_renderer.update_map_data(surface_data, game_settings)
            
        draw_background(screen)
        map_renderer.draw_map(map_rotation_angle, game_settings)
        panel_rects = draw_menu(screen, game_settings, p_ready, player_focus, player_cursors, role_error_message, len(gamepads), player_unlocked_all)
        pygame.display.flip()

    return False, 0, {}

