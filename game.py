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
#   (version 25/09)
#   -> Main game file

"""
le code à exécuter pour lancer le jeu.

quand on lance le jeu, on doit choisir pour chaque player son animal, rôle (prey/predator) et si c'est une IA ou un joueur. (les valeurs par défault sont dans settings.py)
de base 2 joueurs, si il y a 2 manettes de connectés on peut avoir 2, 3 ou 4 joueurs. (voir les commandes en dessous)

changement dans la physique du jeu : (que l'on peut activer / désactiver dans les paramètres si on veux garder la physique de base (voir les commandes en dessous))
dans la physique de base, le seul moyen de ralentir la vitesse était les forces de frottement et gravité, ça donnait des "glissades" interminable jusqu'à l'arrêt.
    -> j'ai ajouté une Fbrake pour chaque animal (qui dépend de F0i), qui permet, si aucune commande n'ai actionnée, d'ajouter une force de freinage en plus des forces de frottements pour aider à ralentir
    -> à voir si il faut faire autrement, mais il faut ajouter une manière pour ralentir car la logique d'avant partait du principe que les animaux étaient tous sur roulettes..

dans la physique de base, lorque l'on était en descente, la gravité aidait à l'accélération proportionnellement au niveau de pente, sauf que dans des pentes très importante, la gravité aidait beaucoup trop (vrai d'un point de vu mathématique mais faux d'un point de vue réel)
    -> j'ai ajouter une slopeOpt pour chaque animal, qui définit la pente (négative) jusqu'à laquelle il peut profiter à 100% de l'aide de g, et au dela, g aide de moins en moins, jusqu'à devenir délétaire pour des pentes < 2*slopeOpt
    -> la logique est : g aide normalement jusqu'à slopeOpt, puis au dela, aide de moins en moins : si slopeOpt est 15%, alors jusqu'à -15%, g aide normalement, puis pour -16%, g aide comme pour -14%, pour -20% comme pour -10% etc...
    -> donc au dela de 2* slopeOpt, par exemple -32%, g "aide" comme pour 2%, donc est délétaire.
    -> c'est la logique la plus proche de la réalité, car pareil, on est pas sur roulettes et on ne profite pas à fond de la gravité

============= COMMANDES ============|       0 MANETTE (clavier)     |           1 MANETTE           |           2 MANETTES          |
-=-=-=-=-=-=-=- MENU -=-=-=-=-=-=-=-|= = = = = = = = = = = = = = = =|= = = = = = = = = = = = = = = =|= = = = = = = = = = = = = = = =|
Changer de Map                      |   'Y' et 'H' (haut / bas)     | haut/bas croix directionnelle | haut/bas croix d. (manette 1) |
Rotation de la map                  |  'G' et 'J' (gauche/droite)   |   G/D croix directionnelle    |   G/D croix d. (manette 1)    |
Ouvrir/Fermer paramètres            |         'BACKSPACE'           |            select             |       select (manette 1)      |
Déplacer dans paramètres            |      'Y', 'G', 'H' et 'J'     |     croix directionnelle      |      croix d. (manette 1)     |
------------- PLAYER 1 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Naviguer entre les choix            |           'zqsd'              |        joystick gauche        |     joystick gauche (m.1)     |
Se mettre "Ready"                   |           'SPACE'             |              LT               |           LT (m.1)            |
------------- PLAYER 2 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Naviguer entre les choix            |    flèches directionnelles    |        joystick droit         |     joystick gauche (m.2)     |
Se mettre "Ready"                   |           'RETURN'            |              RT               |           LT (m.2)            |
------------- PLAYER 3 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Ajouter/Supprimer le player         |                               |                               |  clique joystick droit (m.1)  |
Naviguer entre les choix            |                               |                               |     joystick droit (m.1)      |
Se mettre "Ready"                   |                               |                               |           RT (m.1)            |
------------- PLAYER 4 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Ajouter/Supprimer le player         |                               |                               |  clique joystick droit (m.2)  |
Naviguer entre les choix            |                               |                               |     joystick droit (m.2)      |
Se mettre "Ready"                   |                               |                               |           RT (m.2)            |
-=-=-=-=-=-=-=- JEU -=-=-=-=-=-=-=- |= = = = = = = = = = = = = = = =|= = = = = = = = = = = = = = = =|= = = = = = = = = = = = = = = =|
------------- PLAYER 1 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Déplacements                        |           'zqsd'              |        joystick gauche        |     joystick gauche (m.1)     |
Avancer (dépenser du Wac)           |           'SPACE'             |              LT               |           LT (m.1)            |
------------- PLAYER 2 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Déplacements                        |    flèches directionnelles    |        joystick droit         |     joystick gauche (m.2)     |
Avancer (dépenser du Wac)           |           'RETURN'            |              RT               |           LT (m.2)            |
------------- PLAYER 3 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Déplacements                        |                               |                               |     joystick droit (m.1)      |
Avancer (dépenser du Wac)           |                               |                               |           RT (m.1)            |
------------- PLAYER 4 -------------|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|- - - - - - - - - - - - - - - -|
Déplacements                        |                               |                               |     joystick droit (m.2)      |
Avancer (dépenser du Wac)           |                               |                               |           RT (m.2)            |
"""

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