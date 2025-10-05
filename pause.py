#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __    __     ______     ______   ______     ______     ______   __         ______
#   /\ "-./  \   /\  __ \   /\  == \ /\  ___\   /\  == \   /\  __ \ /\ \       /\  ___\
#   \ \ \-./\ \  \ \  __ \  \ \  _-/ \ \___  \  \ \  __<   \ \  __ \\ \ \____  \ \___  \
#    \ \_\ \ \_\  \ \_\ \_\  \ \_\    \/\_____\  \ \_\ \_\  \ \_\ \_\\ \_____\  \/\_____\
#     \/_/  \/_/   \/_/\/_/   \/_/     \/_____/   \/_/ /_/   \/_/\/_/ \/_____/   \/_____/
#   (version 05/10)
#   → Gère le menu de pause

import pygame
import settings
from commands import get_menu_inputs
from ui import draw_pause_menu

def pause_menu_loop(screen, clock, gamepads):
    """
    Gère la logique du menu de pause. Retourne l'action choisie.
    """
    selected_index = 0
    last_nav_y = 0
    last_confirm_press = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"

        # --- ENTRÉES ---
        menu_actions = get_menu_inputs(gamepads)
        nav_y = - menu_actions['map_nav_y']
        confirm_pressed = menu_actions['open_settings']

        if nav_y != 0 and last_nav_y == 0:
            selected_index = (selected_index + nav_y + 3) % 3

        if confirm_pressed and not last_confirm_press:
            if selected_index == 0:
                return "RESUME"
            elif selected_index == 1:
                return "RETURN_TO_MENU"
            elif selected_index == 2:
                return "QUIT"

        last_nav_y = nav_y
        last_confirm_press = confirm_pressed
        
        # L'écran est déjà dessiné, nous dessinons simplement le menu par-dessus
        draw_pause_menu(screen, selected_index)
        pygame.display.flip()
        clock.tick(settings.FPS)