#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    ______     ______     __    __     ______    
#   /\  ___\   /\  __ \   /\ "-./  \   /\  ___\   
#   \ \ \__ \  \ \  __ \  \ \ \-./\ \  \ \  __\   
#    \ \_____\  \ \_\ \_\  \ \_\ \ \_\  \ \_____\ 
#     \/_____/   \/_/\/_/   \/_/  \/_/   \/_____/
#   (version 08/10)
#   → Fichier principal du jeu

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
from language import set_language

def main():
    """
    Initialise le jeu, gère la boucle principale (menu, jeu).
    """
    pygame.init()
    
    if settings.FULLSCREEN:
        screen_flags = pygame.NOFRAME
        desktop_sizes = pygame.display.get_desktop_sizes()
        
        screen_index = settings.DISPLAY_SCREEN
        if screen_index < 0 or screen_index >= len(desktop_sizes):
            print(f"Avertissement : L'écran {screen_index} n'est pas disponible. Utilisation de l'écran 0 par défaut.")
            screen_index = 0

        if desktop_sizes:
            screen_size = desktop_sizes[screen_index]
            screen = pygame.display.set_mode(screen_size, screen_flags, display=screen_index)
        else:
            screen_flags = pygame.FULLSCREEN
            screen = pygame.display.set_mode((0, 0), screen_flags)
    else:
        screen_flags = pygame.RESIZABLE
        screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), screen_flags, vsync=1)

    pygame.display.set_caption("RunFoVEyourLife")
    clock = pygame.time.Clock()
    gamepads = init_joysticks()

    animal_names = [animal['name'] for animal in ANIMALS]
    game_settings = {
        'map_name': settings.SELECTED_MAP,
        'map_index': animal_names.index(settings.SELECTED_MAP) if settings.SELECTED_MAP in animal_names else 0,
        'round_duration': settings.ROUND_DURATION,
        'winning_score': settings.WINNING_SCORE,
        'map_width': settings.MAP_WIDTH_METERS,
        'wac_ratio': settings.WAC_RATIO,
        'slope_correction': settings.SLOPE_CORRECTION,
        'brake_correction': settings.BRAKE_CORRECTION,
        'vc_speed': settings.VC_SPEED,
        'infinity_map': settings.INFINITY_MAP,
        'vibration_mode': settings.VIBRATION_MODE,
        'ai_enabled': settings.AI_ENABLED,
        'language': settings.LANGUAGE,
    }
    set_language(game_settings['language'])

    for i in range(1, 5):
        game_settings[f'p{i}_role'] = 'predator' if i == settings.PREDATOR_PLAYER else 'prey'
        game_settings[f'p{i}_animal_name'] = getattr(settings, f'PLAYER{i}_ANIMAL')
        game_settings[f'p{i}_animal_index'] = animal_names.index(game_settings[f'p{i}_animal_name'])
        is_active = (i <= 2)
        game_settings[f'p{i}_status'] = "PLAYER" if is_active else "INACTIVE"
    
    session_log = logs.init_session_log(len(gamepads))
    
    player_unlocked_all = {i: False for i in range(1, 5)}

    running = True
    while running:
        menu_result, map_rotation_angle, panel_rects = menu_loop(screen, clock, gamepads, game_settings, player_unlocked_all)

        if not menu_result:
            running = False
            continue
        
        set_language(game_settings['language'])
        
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

        game_return_value = game_loop(screen, clock, players, map_renderer, game_data, gamepads, game_settings, map_rotation_angle, panel_rects)
        game_result = game_return_value[0]
        scores = game_return_value[1]

        if game_result == 'QUIT':
            running = False

    if session_log['games']:
        logs.save_log_file(session_log)

    pygame.quit()

if __name__ == '__main__':
    main()

