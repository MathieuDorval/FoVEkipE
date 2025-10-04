#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __         ______     ______   ______     ______   __         ______     __  __    
#   /\ \       /\  ___\   /\__  _\ /\  ___\   /\  == \ /\ \       /\  __ \   /\ \_\ \   
#   \ \ \____  \ \  __\   \/_/\ \/ \ \___  \  \ \  _-/ \ \ \____  \ \  __ \  \ \____ \  
#    \ \_____\  \ \_____\    \ \_\  \/\_____\  \ \_\    \ \_____\  \ \_\ \_\  \/\_____\ 
#     \/_____/   \/_____/     \/_/   \/_____/   \/_/     \/_____/   \/_/\/_/   \/_____/
#   (version 03/10)
#   → Handles the main game loop

import pygame
import settings
import random
from commands import get_menu_inputs, get_player_action, get_pause_action
from ui import draw_game_info, draw_game_over_screen, draw_pause_menu
from killcam import play_killcam
from ai import get_ai_inputs
from transitions import play_start_transition, play_round_reset_transition
import logs
from renderer import draw_background

def _get_shortest_distance(p1, p2, map_width):
    """
    (Internal) Calculate the shortest distance between two players, wrapping around the map if infinite.
    """
    dx = abs(p1.x - p2.x)
    dy = abs(p1.y - p2.y)
    
    if dx > map_width / 2:
        dx = map_width - dx
    if dy > map_width / 2:
        dy = map_width - dy
        
    return pygame.Vector2(dx, dy).length()

def _handle_vibrations(players, gamepads, game_settings):
    """
    (Internal) Calculate and apply controller vibrations based on player proximity.
    This function only runs if 'vibration_mode' is ON.
    """
    # If vibration mode is globally disabled, do nothing.
    if not game_settings.get('vibration_mode', False) or not gamepads:
        # Stop any lingering vibrations
        for gamepad in gamepads:
            gamepad.rumble(0, 0, 0)
        return

    num_gamepads = len(gamepads)
    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    max_vibration_dist = map_width * settings.VIBRATION_DISTANCE_RATIO
    if max_vibration_dist <= 0: return

    # Helper to map player ID to a gamepad and motor side ('left' or 'right')
    def get_player_gamepad_and_motor(player_id):
        if num_gamepads == 1:
            if player_id == 1: return 0, 'left'
            if player_id == 2: return 0, 'right'
        elif num_gamepads == 2:
            if player_id == 1: return 0, 'left'
            if player_id == 2: return 1, 'left'
            if player_id == 3: return 0, 'right'
            if player_id == 4: return 1, 'right'
        elif num_gamepads == 3:
            if player_id == 1: return 0, 'left'
            if player_id == 2: return 1, 'left'
            if player_id == 3: return 2, 'left'
            if player_id == 4: return 0, 'right'
        elif num_gamepads >= 4:
            if player_id <= num_gamepads:
                return player_id - 1, 'left' # Assume left stick for all
        return None, None

    # Initialize rumble values for each gamepad
    gamepad_rumble = {i: {'left': 0.0, 'right': 0.0} for i in range(num_gamepads)}

    active_human_players = [p for p in players if p.is_active and not p.is_ai]

    for current_player in active_human_players:
        opponents = [p for p in players if p.is_active and p.role != current_player.role]
        if not opponents:
            continue

        # Find the closest opponent
        closest_opponent = min(opponents, key=lambda o: _get_shortest_distance(current_player, o, map_width) if game_settings.get('infinity_map') else pygame.Vector2(current_player.x, current_player.y).distance_to((o.x, o.y)))
        
        distance = _get_shortest_distance(current_player, closest_opponent, map_width) if game_settings.get('infinity_map') else pygame.Vector2(current_player.x, current_player.y).distance_to((closest_opponent.x, closest_opponent.y))

        # If opponent is close, calculate intensity and apply rumble
        if distance < max_vibration_dist:
            intensity = 1.0 - (distance / max_vibration_dist)
            gamepad_index, _ = get_player_gamepad_and_motor(current_player.id)

            if gamepad_index is not None:
                # In vibration mode, both motors always rumble for proximity
                gamepad_rumble[gamepad_index]['left'] = max(gamepad_rumble[gamepad_index]['left'], intensity)
                gamepad_rumble[gamepad_index]['right'] = max(gamepad_rumble[gamepad_index]['right'], intensity)

    # Apply the calculated rumble values to each gamepad
    for i, rumble_values in gamepad_rumble.items():
        if rumble_values['left'] > 0 or rumble_values['right'] > 0:
            gamepads[i].rumble(rumble_values['left'], rumble_values['right'], 200)
        else:
            gamepads[i].rumble(0, 0, 0)

def _reset_players_positions(players, game_settings):
    """
    (Internal) Place the prey and predators on the map randomly.
    """
    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    half_map_width = map_width / 2
    min_spawn_distance = settings.MIN_DISTANCE_PREDATOR * map_width

    prey_players = [p for p in players if p.role == 'prey']
    predator_players = [p for p in players if p.role == 'predator']

    for prey in prey_players:
        prey.x = random.uniform(-half_map_width, half_map_width)
        prey.y = random.uniform(-half_map_width, half_map_width)

    for predator in predator_players:
        valid_position = False
        while not valid_position:
            predator.x = random.uniform(-half_map_width, half_map_width)
            predator.y = random.uniform(-half_map_width, half_map_width)
            
            if not prey_players:
                valid_position = True
                continue

            is_far_enough = all(
                pygame.Vector2(predator.x, predator.y).distance_to(pygame.Vector2(prey.x, prey.y)) >= min_spawn_distance
                for prey in prey_players
            )
            if is_far_enough:
                valid_position = True

    for player in players:
        player.velocity = pygame.Vector2(0, 0)
        player.Wac = 0.0
        player.acceleration = pygame.Vector2(0, 0)
        player.is_active = True

def _check_collision(player1, player2, game_settings):
    """
    (Internal) Check if the two players are touching.
    """
    distance = pygame.Vector2(player1.x, player1.y).distance_to(pygame.Vector2(player2.x, player2.y))
    collision_threshold = game_settings.get('map_width', settings.MAP_WIDTH_METERS) * settings.COLLISION_DISTANCE
    return distance < collision_threshold

def _pause_menu_loop(screen, clock, gamepads):
    """
    (Internal) Handles the pause menu logic. Returns the chosen action.
    """
    selected_index = 0
    last_nav_y = 0
    last_confirm_press = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
        
        # --- INPUTS ---
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
        
        draw_pause_menu(screen, selected_index)
        pygame.display.flip()
        clock.tick(settings.FPS)


def game_loop(screen, clock, players, map_renderer, game_data, gamepads, game_settings, initial_map_rotation, panel_rects):
    """
    Manage the entire game.
    """
    map_rotation_angle = initial_map_rotation
    surface_data = game_settings['surface_data']
    
    scores = {p.id: 0 for p in players}
    
    _reset_players_positions(players, game_settings)
    play_start_transition(screen, clock, players, map_renderer, map_rotation_angle, panel_rects)

    last_pause_press = True

    game_over = False
    while not game_over:
        
        round_data = logs.add_round_to_game(game_data, players)
        capture_events = []

        round_time = 0.0
        round_running = True
        while round_running:
            dt = clock.tick(settings.FPS) / 1000.0
            if dt == 0: continue
            round_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT", None

            pause_pressed = get_pause_action(gamepads)
            if pause_pressed and not last_pause_press:
                action = _pause_menu_loop(screen, clock, gamepads)
                if action == "RETURN_TO_MENU":
                    return "RETURN_TO_MENU", None
                elif action == "QUIT":
                    return "QUIT", None
            last_pause_press = pause_pressed

            active_players_list = [p for p in players if p.is_active]
            for player in active_players_list:
                action = get_ai_inputs(player, active_players_list, game_settings) if player.is_ai else get_player_action(player.id, gamepads, map_rotation_angle)
                player.update(action['direction'], action['intensity'], dt, surface_data, game_settings)
            
            _handle_vibrations(active_players_list, gamepads, game_settings)
            logs.add_frame_to_round(round_data, players, round_time, surface_data, game_settings)

            predators = [p for p in active_players_list if p.role == 'predator']
            if predators:
                remaining_prey = [p for p in active_players_list if p.role == 'prey']
                for prey in remaining_prey:
                    for predator in predators:
                        if _check_collision(predator, prey, game_settings):
                            prey.is_active = False
                            capture_events.append({'time': round_time, 'predator_id': predator.id, 'prey_id': prey.id})
                            break
                
                active_players_list = [p for p in players if p.is_active]
                if not any(p.role == 'prey' for p in active_players_list):
                    all_predators = [p for p in players if p.role == 'predator']
                    for p in all_predators: 
                        scores[p.id] += 1
                    round_running = False

            if round_time >= game_settings.get('round_duration', 30) and round_running:
                all_preys = [p for p in players if p.role == 'prey']
                for p in all_preys:
                    scores[p.id] += 1
                round_running = False

            draw_background(screen, dark=True)
            map_renderer.draw_map(map_rotation_angle, game_settings)
            
            active_players_list = [p for p in players if p.is_active]
            for player in active_players_list:
                map_renderer.draw_point(player.x, player.y, player.color, map_rotation_angle)
            draw_game_info(screen, scores, round_time, players, game_settings)
            pygame.display.flip()

        active_at_end = [p for p in players if p.is_active]
        round_winner_role = 'predator' if not any(p.role == 'prey' for p in active_at_end) else ('prey' if round_time >= game_settings.get('round_duration', 30) else 'None')
        
        round_data['winner_role'] = round_winner_role
        round_data['duration'] = round_time
        
        if any(s >= game_settings.get('winning_score', 3) for s in scores.values()):
            game_over = True
            play_killcam(screen, clock, map_renderer, game_data, map_rotation_angle, round_winner_role, capture_events, game_settings)
        else:
            last_world_positions = play_killcam(screen, clock, map_renderer, game_data, map_rotation_angle, round_winner_role, capture_events, game_settings)
            _reset_players_positions(players, game_settings)
            
            if last_world_positions:
                last_screen_positions = {}
                for pid, pos_data in last_world_positions.items():
                    z = (map_renderer.get_z(pos_data['x'], pos_data['y']) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
                    last_screen_positions[pid] = map_renderer._project_isometric(pos_data['x'], pos_data['y'], z, map_rotation_angle)

                new_screen_positions = {}
                for p in players:
                    z = (map_renderer.get_z(p.x, p.y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
                    new_screen_positions[p.id] = map_renderer._project_isometric(p.x, p.y, z, map_rotation_angle)

                play_round_reset_transition(screen, clock, players, map_renderer, map_rotation_angle, last_screen_positions, new_screen_positions)
    
    logs.finalize_game_data(game_data, scores, players, game_settings.get('winning_score', 3))
    draw_game_over_screen(screen, clock, gamepads, players, scores, game_settings)
    
    return "RETURN_TO_MENU", scores