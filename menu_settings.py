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
#   (version 14/09)
#   -> Manage the settings menu

import pygame
import settings
from commands import get_menu_inputs
from ui import draw_settings_menu

def menu_settings_loop(screen, clock, gamepads, game_settings):
    """
    Gère le menu des paramètres.
    """
    options = {
        "Round Duration": "round_duration",
        "Winning Score": "winning_score",
        "Map Width": "map_width",
        "Slope Correction": "slope_correction",
        "Brake Correction": "brake_correction",
        "AI": "ai_enabled",
        "Quit Game": "quit_game"
    }
    option_keys = list(options.keys())
    selected_index = 0
    
    last_nav_y = 0
    last_nav_x = 0
    last_select_button = True 

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        menu_actions = get_menu_inputs(gamepads)
        nav_x, nav_y = menu_actions['map_rotate_x'], menu_actions['map_nav_y']

        if nav_y != 0 and last_nav_y == 0:
            selected_index = (selected_index - nav_y + len(option_keys)) % len(option_keys)
        
        # --- Handle value changes with horizontal navigation ---
        if nav_x != 0 and last_nav_x == 0:
            key_to_change = options[option_keys[selected_index]]
            
            if key_to_change == "round_duration":
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
            elif key_to_change in ["slope_correction", "brake_correction", "ai_enabled"]:
                current_value = game_settings.get(key_to_change)
                game_settings[key_to_change] = not current_value

        # --- Handle select button press ---
        if menu_actions['open_settings'] and not last_select_button:
            selected_action = options[option_keys[selected_index]]
            if selected_action == "quit_game":
                pygame.quit()
                exit()
            else:
                running = False # Close settings menu for any other option
        
        last_nav_y = nav_y
        last_nav_x = nav_x
        last_select_button = menu_actions['open_settings']
        
        screen.fill(settings.BLACK)
        draw_settings_menu(screen, game_settings, selected_index, option_keys)
        pygame.display.flip()
        clock.tick(settings.FPS)

