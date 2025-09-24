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
#   (version 14/09)
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
import scipy.io
from datetime import datetime

def main():
    """
    Initialise le jeu, gère la boucle principale (menu, jeu) et la sauvegarde des données.
    """
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
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
    }
    for i in range(1, 5):
        game_settings[f'p{i}_role'] = 'predator' if i == settings.PREDATOR_PLAYER else 'prey'
    for i in range(1, 5):
        game_settings[f'p{i}_animal_name'] = getattr(settings, f'PLAYER{i}_ANIMAL')
        game_settings[f'p{i}_animal_index'] = animal_names.index(game_settings[f'p{i}_animal_name'])
        is_ai = False
        
        is_active = (i <= 2)
        
        if not is_active:
            status = "INACTIVE"
        else:
            status = "AI" if is_ai else "PLAYER"
        game_settings[f'p{i}_status'] = status

    session_data = { 'games': {} }
    game_count = 0
    
    running = True
    while running:
        menu_result, map_rotation_angle = menu_loop(screen, clock, gamepads, game_settings)

        if not menu_result:
            running = False
            continue

        game_count += 1
        game_key = f"game_{game_count}"
        
        surface_data = generate_terrain(game_settings['map_name'], settings.MAP_POINTS, settings.MAP_POINTS, game_settings)
        map_renderer = MapRenderer(screen, screen.get_rect(), surface_data, game_settings)
        
        players = []
        player_colors = [settings.COLOR_PLAYER1, settings.COLOR_PLAYER2, settings.COLOR_PLAYER3, settings.COLOR_PLAYER4]
        
        active_player_ids = [i for i in range(1, 5) if game_settings[f'p{i}_status'] != "INACTIVE"]

        for i in active_player_ids:
            player_id = i
            animal_name = game_settings[f'p{i}_animal_name']
            animal = next(a for a in ANIMALS if a["name"] == animal_name)
            role = game_settings[f'p{i}_role']
            is_ai = game_settings[f'p{i}_status'] == "AI"
            
            player = Player(
                id=player_id,
                color=player_colors[player_id - 1],
                animal_data=animal,
                role=role,
                is_ai=is_ai
            )
            players.append(player)

        game_data = {
            'launch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'settings': {
                'map_name': game_settings['map_name'],
                'map_data': surface_data,
                'map_width': game_settings['map_width'],
                'map_max_height_ratio': settings.MAP_MAX_HEIGHT_RATIO,
                'round_duration': game_settings['round_duration'],
                'winning_score': game_settings['winning_score']
            },
            'num_players': len(players),
            'players': {},
            'rounds': {}
        }

        for p in players:
            game_data['players'][f'player_{p.id}'] = {
                'animal': p.animal['name'], 'stats': p.stats,
                'role': p.role, 'is_ai': p.is_ai,
                'color': p.color
            }

        game_data_from_loop = game_loop(screen, clock, players, map_renderer, game_data, gamepads, game_settings, map_rotation_angle)

        if game_data_from_loop is None:
            running = False
        else:
            session_data['games'][game_key] = game_data_from_loop

    if game_count > 0:
        filename = "game_log.mat"
        scipy.io.savemat(filename, session_data)
        print(f"FoVEkipE INFO: Data saved in {filename}")

    pygame.quit()

if __name__ == '__main__':
    main()