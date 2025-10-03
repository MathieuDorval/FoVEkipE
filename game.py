#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______     ______     __    __     ______    
#   /\  ___\   /\  __ \   /\ "-./  \   /\  ___\   
#   \ \ \__ \  \ \  __ \  \ \ \-./\ \  \ \  __\   
#    \ \_____\  \ \_\ \_\  \ \_\ \ \_\  \ \_____\ 
#     \/_____/   \/_/\/_/   \/_/  \/_/   \/_____/
#   (version 03/10)
#   -> Main game file

import pygame
import settings
from renderer import MapRenderer
from commands import init_joysticks
from player import Player
from animals import ANIMALS
from maps import generate_terrain
from letsplay import game_loop
from menu import menu_loop
import logs
from datetime import datetime

def main():
    """
    Initialize the game, manage the main loop (menu, game).
    """
    pygame.init()
    
    if settings.FULLSCREEN:
        screen_flags = pygame.FULLSCREEN
        screen = pygame.display.set_mode((0, 0), screen_flags)
    else:
        screen_flags = pygame.RESIZABLE
        screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), screen_flags, vsync=1)

    pygame.display.set_caption("FoVEkipE")
    clock = pygame.time.Clock()
    gamepads = init_joysticks()

    animal_names = [animal['name'] for animal in ANIMALS]
    game_settings = {
        'map_name': settings.SELECTED_MAP,
        'map_index': animal_names.index(settings.SELECTED_MAP) if settings.SELECTED_MAP in animal_names else 0,
        'round_duration': settings.ROUND_DURATION,
        'winning_score': settings.WINNING_SCORE,
        'map_width': settings.MAP_WIDTH_METERS,
        'slope_correction': settings.SLOPE_CORRECTION,
        'brake_correction': settings.BRAKE_CORRECTION,
        'ai_enabled': settings.AI_ENABLED,
        'wac_ratio': settings.WAC_RATIO,
        'vc_speed': settings.VC_SPEED,
        'infinity_map': settings.INFINITY_MAP,
        'vibration_mode': settings.VIBRATION_MODE,
    }
    for i in range(1, 5):
        game_settings[f'p{i}_role'] = 'predator' if i == settings.PREDATOR_PLAYER else 'prey'
        game_settings[f'p{i}_animal_name'] = getattr(settings, f'PLAYER{i}_ANIMAL')
        game_settings[f'p{i}_animal_index'] = animal_names.index(game_settings[f'p{i}_animal_name'])
        is_active = (i <= 2)
        game_settings[f'p{i}_status'] = "PLAYER" if is_active else "INACTIVE"
    
    session_log = logs.init_session_log(len(gamepads))
    
    running = True
    while running:
        menu_result, map_rotation_angle, panel_rects = menu_loop(screen, clock, gamepads, game_settings)

        if not menu_result:
            running = False
            continue
        
        surface_data = generate_terrain(game_settings['map_name'], settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
        game_settings['surface_data'] = surface_data
        
        players = []
        active_player_ids = [i for i in range(1, 5) if game_settings[f'p{i}_status'] != "INACTIVE"]

        for i in active_player_ids:
            player = Player(
                id=i,
                color=settings.PLAYER_COLORS[i][game_settings[f'p{i}_role']],
                animal_data=next(a for a in ANIMALS if a["name"] == game_settings[f'p{i}_animal_name']),
                role=game_settings[f'p{i}_role'],
                is_ai=game_settings[f'p{i}_status'] == "AI"
            )
            players.append(player)

        game_data = logs.add_game_to_log(session_log, game_settings, players)
        map_renderer = MapRenderer(screen, screen.get_rect(), surface_data, game_settings)

        continue_game = game_loop(screen, clock, players, map_renderer, game_data, gamepads, game_settings, map_rotation_angle, panel_rects)

        if not continue_game:
            running = False

    if session_log['games']:
        logs.save_log_file(session_log)

    pygame.quit()

if __name__ == '__main__':
    main()

