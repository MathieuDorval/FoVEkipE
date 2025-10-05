#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __   __   ______     ______     ______     ______   ______     __   __     ______     __    
#   /\ \ / /  /\  ___\   /\  == \   /\  __ \   /\  ___\   /\  __ \   /\ "-.\ \   /\  ___\   /\ \   
#   \ \ \'/   \ \ \__ \  \ \  __<   \ \ \/\ \  \ \  __\   \ \ \/\ \  \ \ \-.  \  \ \ \__ \  \ \ \  
#    \ \__|    \ \_____\  \ \_\ \_\  \ \_____\  \ \_____\  \ \_____\  \ \_\\"\_\  \ \_____\  \ \_\ 
#     \/_/      \/_____/   \/_/ /_/   \/_____/   \/_____/   \/_____/   \/_/ \/_/   \/_____/   \/_/ 
#   (version 05/10)
#   → Gère les vibrations des manettes

import pygame
import settings

def _get_shortest_vector(p1, p2, map_width):
    """
    (Interne) Calcule le vecteur le plus court entre deux points sur une carte toroïdale.
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    
    if dx > map_width / 2:
        dx -= map_width
    elif dx < -map_width / 2:
        dx += map_width
        
    if dy > map_width / 2:
        dy -= map_width
    elif dy < -map_width / 2:
        dy += map_width
        
    return pygame.Vector2(dx, dy)

def _get_player_gamepad_map(num_gamepads):
    """
    (Interne) Retourne un dictionnaire mappant les ID des joueurs à leur index de manette.
    Ce mode suppose un joueur par manette.
    """
    if num_gamepads == 1: return {1: 0}
    if num_gamepads == 2: return {1: 0, 2: 1}
    if num_gamepads == 3: return {1: 0, 2: 1, 3: 2}
    if num_gamepads >= 4: return {1: 0, 2: 1, 3: 2, 4: 3}
    return {}

def handle_vibrations(players, gamepads, game_settings):
    """
    Calcule et applique les vibrations des manettes en fonction de la proximité et de la direction des adversaires.
    """
    if not game_settings.get('vibration_mode', False) or not gamepads:
        for gamepad in gamepads:
            if gamepad.get_init():
                gamepad.rumble(0, 0, 0)
        return

    num_gamepads = len(gamepads)
    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    max_vibration_dist = map_width * settings.VIBRATION_DISTANCE_RATIO
    if max_vibration_dist <= 0: return

    gamepad_map = _get_player_gamepad_map(num_gamepads)
    gamepad_rumble = {i: {'left': 0.0, 'right': 0.0} for i in range(num_gamepads)}

    active_human_players = [p for p in players if p.is_active and not p.is_ai]

    for current_player in active_human_players:
        gamepad_index = gamepad_map.get(current_player.id)
        if gamepad_index is None or gamepad_index >= num_gamepads:
            continue

        opponents = [p for p in players if p.is_active and p.role != current_player.role]
        if not opponents:
            continue
            
        player_forward_vector = current_player.last_direction
        if player_forward_vector.length_squared() == 0:
            player_forward_vector = pygame.Vector2(1, 0)

        for opponent in opponents:
            if game_settings.get('infinity_map'):
                vec_to_opponent = _get_shortest_vector(current_player, opponent, map_width)
            else:
                vec_to_opponent = pygame.Vector2(opponent.x - current_player.x, opponent.y - current_player.y)
            
            distance = vec_to_opponent.length()

            if 0 < distance < max_vibration_dist:
                intensity = 1.0 - (distance / max_vibration_dist)
                
                angle = player_forward_vector.angle_to(vec_to_opponent)

                if -45 <= angle <= 45:
                    gamepad_rumble[gamepad_index]['left'] = max(gamepad_rumble[gamepad_index]['left'], intensity)
                    gamepad_rumble[gamepad_index]['right'] = max(gamepad_rumble[gamepad_index]['right'], intensity)
                elif -135 < angle < -45:
                    gamepad_rumble[gamepad_index]['left'] = max(gamepad_rumble[gamepad_index]['left'], intensity)
                elif 45 < angle < 135:
                    gamepad_rumble[gamepad_index]['right'] = max(gamepad_rumble[gamepad_index]['right'], intensity)
    
    for i, rumble_values in gamepad_rumble.items():
        if i < len(gamepads) and gamepads[i].get_init():
            gamepads[i].rumble(rumble_values['left'], rumble_values['right'], 250)