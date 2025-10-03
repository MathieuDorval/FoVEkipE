#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    __    __     ______     __   __     __  __        ______     ______     ______   ______   __     __   __     ______     ______    
#   /\ "-./  \   /\  ___\   /\ "-.\ \   /\ \/\ \      /\  ___\   /\  ___\   /\__  _\ /\__  _\ /\ \   /\ "-.\ \   /\  ___\   /\  ___\   
#   \ \ \-./\ \  \ \  __\   \ \ \-.  \  \ \ \_\ \     \ \___  \  \ \  __\   \/_/\ \/ \/_/\ \/ \ \ \  \ \ \-.  \  \ \ \__ \  \ \___  \  
#    \ \_\ \ \_\  \ \_____\  \ \_\\"\_\  \ \_____\     \/\_____\  \ \_____\    \ \_\    \ \_\  \ \_\  \ \_\\"\_\  \ \_____\  \/\_____\ 
#     \/_/  \/_/   \/_____/   \/_/ \/_/   \/_____/      \/_____/   \/_____/     \/_/     \/_/   \/_/   \/_/ \/_/   \/_____/   \/_____/
#   (version 03/10)
#   -> Manage the settings menu

import pygame
import settings
from commands import get_menu_inputs
from ui import draw_settings_menu
from language import get_text, set_language

def menu_settings_loop(screen, clock, gamepads, game_settings):
    """
    Handle the settings menu.
    """
    option_keys = [
        "language_label",
        "round_duration_label",
        "winning_score_label",
        "map_width_label",
        "wac_ratio_label",
        "slope_correction_label",
        "brake_correction_label",
        "vc_speed_label",
        "infinity_map_label",
        "vibration_mode_label",
        "ai_label",
        "quit_game_label"
    ]
    
    key_map = {
        "language_label": "language",
        "round_duration_label": "round_duration",
        "winning_score_label": "winning_score",
        "map_width_label": "map_width",
        "wac_ratio_label": "wac_ratio",
        "slope_correction_label": "slope_correction",
        "brake_correction_label": "brake_correction",
        "vc_speed_label": "vc_speed",
        "infinity_map_label": "infinity_map",
        "vibration_mode_label": "vibration_mode",
        "ai_label": "ai_enabled",
        "quit_game_label": "quit_game"
    }

    selected_index = 0
    
    last_nav_y = 0
    last_nav_x = 0
    last_select_button = True 

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"

        menu_actions = get_menu_inputs(gamepads)
        nav_x, nav_y = menu_actions['map_rotate_x'], menu_actions['map_nav_y']

        if nav_y != 0 and last_nav_y == 0:
            selected_index = (selected_index - nav_y + len(option_keys)) % len(option_keys)
        
        if nav_x != 0 and last_nav_x == 0:
            key_to_change = key_map[option_keys[selected_index]]
            
            if key_to_change == "language":
                current_lang = game_settings.get('language', 'fr')
                new_lang = 'en' if current_lang == 'fr' else 'fr'
                game_settings['language'] = new_lang
                set_language(new_lang)
            elif key_to_change == "round_duration":
                current_value = game_settings.get(key_to_change)
                new_value = current_value + nav_x * 5
                game_settings[key_to_change] = max(5, min(90, new_value))
            elif key_to_change == "winning_score":
                current_value = game_settings.get(key_to_change)
                new_value = current_value + nav_x
                game_settings[key_to_change] = max(1, min(10, new_value))
            elif key_to_change == "map_width":
                current_value = game_settings.get(key_to_change)
                new_value = current_value + nav_x
                game_settings[key_to_change] = max(5, min(100, new_value))
            elif key_to_change == "wac_ratio":
                current_value = game_settings.get(key_to_change, 1.0)
                new_value = round(current_value + nav_x * 0.2, 1)
                game_settings[key_to_change] = max(0.0, min(10.0, new_value))
            elif key_to_change in ["slope_correction", "brake_correction", "ai_enabled", "vc_speed", "infinity_map"]:
                current_value = game_settings.get(key_to_change)
                game_settings[key_to_change] = not current_value
            elif key_to_change == "vibration_mode":
                num_gamepads = len(gamepads)
                if num_gamepads >= 2:
                    current_value = game_settings.get(key_to_change)
                    game_settings[key_to_change] = not current_value


        if menu_actions['open_settings'] and not last_select_button:
            selected_action = key_map[option_keys[selected_index]]
            if selected_action == "quit_game":
                return "QUIT"
            else:
                running = False
        
        last_nav_y = nav_y
        last_nav_x = nav_x
        last_select_button = menu_actions['open_settings']
        
        screen.fill(settings.BLACK)
        draw_settings_menu(screen, game_settings, selected_index, option_keys, key_map, len(gamepads))
        pygame.display.flip()
        clock.tick(settings.FPS)
    
    return None