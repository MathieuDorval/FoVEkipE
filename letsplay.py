#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    __         ______     ______   ______     ______   __         ______     __  __    
#   /\ \       /\  ___\   /\__  _\ /\  ___\   /\  == \ /\ \       /\  __ \   /\ \_\ \   
#   \ \ \____  \ \  __\   \/_/\ \/ \ \___  \  \ \  _-/ \ \ \____  \ \  __ \  \ \____ \  
#    \ \_____\  \ \_____\    \ \_\  \/\_____\  \ \_\    \ \_____\  \ \_\ \_\  \/\_____\ 
#     \/_____/   \/_____/     \/_/   \/_____/   \/_/     \/_____/   \/_/\/_/   \/_____/
#   (version 03/10)
#   -> Handles the main game loop

import pygame
import settings
import random
from commands import get_player_action
from ui import draw_game_info, draw_game_over_screen
from killcam import play_killcam
from ai import get_ai_inputs
from transitions import play_start_transition, play_round_reset_transition
import logs

def get_shortest_distance(p1, p2, map_width):
    """
    Calculate the shortest distance between two players, accounting for map wrapping.
    """
    dx = abs(p1.x - p2.x)
    dy = abs(p1.y - p2.y)
    
    if dx > map_width / 2:
        dx = map_width - dx
    if dy > map_width / 2:
        dy = map_width - dy
        
    return pygame.Vector2(dx, dy).length()

def handle_vibrations(players, gamepads, game_settings):
    """
    Calculate and apply controller vibrations based on player proximity and orientation.
    """
    if not game_settings.get('vibration_mode', False) or not gamepads:
        return

    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    max_vibration_dist = map_width * settings.VIBRATION_DISTANCE_RATIO
    if max_vibration_dist <= 0: return

    for i, gamepad in enumerate(gamepads):
        player_id = i + 1
        current_player = next((p for p in players if p.id == player_id), None)
        
        if not current_player or not current_player.is_active:
            gamepad.rumble(0, 0, 0)
            continue

        opponents = [p for p in players if p.is_active and p.role != current_player.role]
        if not opponents:
            gamepad.rumble(0, 0, 0)
            continue
            
        closest_opponent = min(opponents, key=lambda o: get_shortest_distance(current_player, o, map_width) if game_settings.get('infinity_map') else pygame.Vector2(current_player.x, current_player.y).distance_to((o.x, o.y)))
        
        if game_settings.get('infinity_map'):
            distance = get_shortest_distance(current_player, closest_opponent, map_width)
        else:
            distance = pygame.Vector2(current_player.x, current_player.y).distance_to((closest_opponent.x, closest_opponent.y))

        if distance < max_vibration_dist:
            intensity = 1.0 - (distance / max_vibration_dist)
            
            player_pos = pygame.Vector2(current_player.x, current_player.y)
            opponent_pos = pygame.Vector2(closest_opponent.x, closest_opponent.y)
            
            vec_to_opponent = opponent_pos - player_pos
            
            if game_settings.get('infinity_map'):
                if vec_to_opponent.x > map_width / 2: vec_to_opponent.x -= map_width
                if vec_to_opponent.x < -map_width / 2: vec_to_opponent.x += map_width
                if vec_to_opponent.y > map_width / 2: vec_to_opponent.y -= map_width
                if vec_to_opponent.y < -map_width / 2: vec_to_opponent.y += map_width

            angle_to_opponent = current_player.last_direction.angle_to(vec_to_opponent)

            left_motor, right_motor = 0.0, 0.0
            if -45 <= angle_to_opponent <= 45:
                left_motor = right_motor = intensity
            elif 45 < angle_to_opponent <= 135:
                left_motor = intensity
            elif -135 <= angle_to_opponent < -45:
                right_motor = intensity
            
            gamepad.rumble(left_motor, right_motor, 200)
        else:
            gamepad.rumble(0, 0, 0)

def reset_players_positions(players, game_settings):
    """
    Place the prey and predators on the map.
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

def check_collision(player1, player2, game_settings):
    """
    Check if the two players are touching.
    """
    distance = pygame.Vector2(player1.x, player1.y).distance_to(pygame.Vector2(player2.x, player2.y))
    collision_threshold = game_settings.get('map_width', settings.MAP_WIDTH_METERS) * settings.COLLISION_DISTANCE
    return distance < collision_threshold

def game_loop(screen, clock, players, map_renderer, game_data, gamepads, game_settings, initial_map_rotation, panel_rects):
    """
    Manage the entire game.
    """
    map_rotation_angle = initial_map_rotation
    surface_data = game_settings['surface_data']
    
    scores = {p.id: 0 for p in players}
    
    reset_players_positions(players, game_settings)
    play_start_transition(screen, clock, players, map_renderer, map_rotation_angle, game_settings, panel_rects)

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
                if event.type == pygame.QUIT: return False

            active_players_list = [p for p in players if p.is_active]
            for player in active_players_list:
                action = get_ai_inputs(player, active_players_list, game_settings) if player.is_ai else get_player_action(player.id, gamepads, map_rotation_angle)
                player.update(action['direction'], action['intensity'], dt, surface_data, game_settings)
            
            handle_vibrations(active_players_list, gamepads, game_settings)
            logs.add_frame_to_round(round_data, players, round_time, surface_data, game_settings)

            predators = [p for p in active_players_list if p.role == 'predator']
            if predators:
                remaining_prey = [p for p in active_players_list if p.role == 'prey']
                for prey in remaining_prey:
                    for predator in predators:
                        if check_collision(predator, prey, game_settings):
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

            screen.fill(settings.BLACK)
            map_renderer.draw_map(map_rotation_angle, game_settings)
            
            active_players_list = [p for p in players if p.is_active]
            for player in active_players_list:
                map_renderer.draw_point(player.x, player.y, player.color, map_rotation_angle)
            draw_game_info(screen, scores, round_time, players, game_settings['round_duration'])
            pygame.display.flip()

        active_at_end = [p for p in players if p.is_active]
        round_winner_role = 'predator' if not any(p.role == 'prey' for p in active_at_end) else ('prey' if round_time >= game_settings.get('round_duration', 30) else 'None')
        
        round_data['winner_role'] = round_winner_role
        round_data['duration'] = round_time
        
        if any(s >= game_settings.get('winning_score', 3) for s in scores.values()):
            game_over = True
            play_killcam(screen, clock, map_renderer, game_data, map_rotation_angle, round_winner_role, capture_events, game_settings)
        else:
            reset_players_positions(players, game_settings)
            
            last_world_positions = play_killcam(screen, clock, map_renderer, game_data, map_rotation_angle, round_winner_role, capture_events, game_settings)

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
    
    return True