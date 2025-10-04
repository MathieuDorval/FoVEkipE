#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __         ______     __   __     ______     __  __     ______     ______     ______    
#   /\ \       /\  __ \   /\ "-.\ \   /\  ___\   /\ \/\ \   /\  __ \   /\  ___\   /\  ___\   
#   \ \ \____  \ \  __ \  \ \ \-.  \  \ \ \__ \  \ \ \_\ \  \ \  __ \  \ \ \__ \  \ \  __\   
#    \ \_____\  \ \_\ \_\  \ \_\\"\_\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_____\ 
#     \/_____/   \/_/\/_/   \/_/ \/_/   \/_____/   \/_____/   \/_/\/_/   \/_____/   \/_____/
#   (version 03/10)
#   -> Manages game languages

TEXTS = {
    'game_name': {'fr': 'FoVE qui Peut', 'en': 'Run FoVE your Life'},

    'player_label': {'fr': 'Joueur', 'en': 'Player'},
    'predators_label': {'fr': 'Prédateurs', 'en': 'Predators'},
    'preys_label': {'fr': 'Proies', 'en': 'Preys'},
    'ready_label': {'fr': 'Prêt', 'en': 'Ready'},
    'error_min_2_players': {'fr': 'Au moins 2 joueurs sont requis !', 'en': 'At least 2 players are required!'},
    'error_min_1_predator': {'fr': 'Au moins un prédateur est requis !', 'en': 'At least one predator is required!'},
    'error_min_1_prey': {'fr': 'Au moins une proie est requise !', 'en': 'At least one prey is required!'},
    'error_vibration_mode': {'fr': 'Moins de joueurs que de manettes requis !', 'en': 'Fewer players than controllers required!'},
    'p1_join_prompt': {'fr': 'Joueur 1 : pressez le joystick gauche (manette 1)', 'en': 'Player 1: press left joystick (controller 1)'},
    'p2_join_prompt_1pad': {'fr': 'Joueur 2 : pressez le joystick droit (manette 1)', 'en': 'Player 2: press right joystick (controller 1)'},
    'p2_join_prompt_2pads': {'fr': 'Joueur 2 : pressez le joystick gauche (manette 2)', 'en': 'Player 2: press left joystick (controller 2)'},
    'p3_join_prompt_2pads': {'fr': 'Joueur 3 : pressez le joystick droit (manette 1)', 'en': 'Player 3: press right joystick (controller 1)'},
    'p4_join_prompt_2pads': {'fr': 'Joueur 4 : pressez le joystick droit (manette 2)', 'en': 'Player 4: press right joystick (controller 2)'},
    'p3_join_prompt_3plus_pads': {'fr': 'Joueur 3 : pressez le joystick gauche (manette 3)', 'en': 'Player 3: press left joystick (controller 3)'},
    'p4_join_prompt_3pads': {'fr': 'Joueur 4 : pressez le joystick droit (manette 1)', 'en': 'Player 4: press right joystick (controller 1)'},
    'p4_join_prompt_4pads': {'fr': 'Joueur 4 : pressez le joystick gauche (manette 4)', 'en': 'Player 4: press left joystick (controller 4)'},

    'settings_title': {'fr': 'Paramètres du jeu', 'en': 'Game Settings'},
    'language_label': {'fr': 'Langue', 'en': 'Language'},
    'round_duration_label': {'fr': 'Durée de la manche', 'en': 'Round Duration'},
    'winning_score_label': {'fr': 'Score pour gagner', 'en': 'Winning Score'},
    'map_width_label': {'fr': 'Largeur de la carte', 'en': 'Map Width'},
    'wac_ratio_label': {'fr': 'Ratio de WAC', 'en': 'WAC Ratio'},
    'slope_correction_label': {'fr': 'Correction de pente', 'en': 'Slope Correction'},
    'brake_correction_label': {'fr': 'Correction de freinage', 'en': 'Brake Correction'},
    'vc_speed_label': {'fr': 'Vitesse critique', 'en': 'Critical Speed'},
    'infinity_map_label': {'fr': 'Carte infinie', 'en': 'Infinity Map'},
    'vibration_mode_label': {'fr': 'Vibrations', 'en': 'Vibrations'},
    'ai_label': {'fr': 'IA', 'en': 'AI'},
    'quit_game_label': {'fr': 'Quitter le jeu', 'en': 'Quit Game'},
    'on_label': {'fr': 'Activé', 'en': 'On'},
    'off_label': {'fr': 'Désactivé', 'en': 'Off'},
    'settings_close_prompt': {'fr': 'Appuyez sur Select pour fermer', 'en': 'Press Select to close'},

    'equality_label': {'fr': 'Égalité', 'en': 'Equality'},
    'predators_win_label': {'fr': 'Les prédateurs gagnent !', 'en': 'Predators win!'},
    'predator_wins_label': {'fr': 'Le prédateur gagne !', 'en': 'Predator wins!'},
    'preys_win_label': {'fr': 'Les proies gagnent !', 'en': 'Preys win!'},
    'prey_wins_label': {'fr': 'La proie gagne !', 'en': 'Prey wins!'},
    'return_to_menu_prompt_keyboard': {'fr': 'Appuyez sur ESPACE pour revenir au menu', 'en': 'Press SPACE to return to the menu'},
    'return_to_menu_prompt_gamepad': {'fr': 'Appuyez sur RT ou LT pour revenir au menu', 'en': 'Press RT or LT to return to the menu'},

    'killcam_label': {'fr': 'Killcam', 'en': 'Killcam'},
    'catch_label': {'fr': 'Attrapé !', 'en': 'Catch!'},
    'escape_label': {'fr': 'Échappé !', 'en': 'Escape!'},

    'Wolf': {'fr': 'Loup', 'en': 'Wolf'},
    'Deer': {'fr': 'Cerf', 'en': 'Deer'},
    'Giga Wolf': {'fr': 'Giga Loup', 'en': 'Giga Wolf'},
    'Cheetah': {'fr': 'Guépard', 'en': 'Cheetah'},
    'Bear': {'fr': 'Ours', 'en': 'Bear'},
    'Rabbit': {'fr': 'Lapin', 'en': 'Rabbit'},
    'Lion': {'fr': 'Lion', 'en': 'Lion'},
    'Gazelle': {'fr': 'Gazelle', 'en': 'Gazelle'},
    'Boar': {'fr': 'Sanglier', 'en': 'Boar'},
    'Fox': {'fr': 'Renard', 'en': 'Fox'},
    'Bison': {'fr': 'Bison', 'en': 'Bison'},
    'Horse': {'fr': 'Cheval', 'en': 'Horse'},
    'Panther': {'fr': 'Panthère', 'en': 'Panther'},
    'Goat': {'fr': 'Chèvre', 'en': 'Goat'},
    'Antelope': {'fr': 'Antilope', 'en': 'Antelope'},
}

CURRENT_LANGUAGE = 'fr'

def set_language(lang):
    """
    Sets the global language for the game.
    """
    global CURRENT_LANGUAGE
    if lang in ['fr', 'en']:
        CURRENT_LANGUAGE = lang

def get_text(key):
    """
    Retrieves a text string in the currently selected language.
    """
    return TEXTS.get(key, {}).get(CURRENT_LANGUAGE, key)