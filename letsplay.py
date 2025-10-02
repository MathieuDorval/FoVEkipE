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
#   (version 24/09)
#   -> Handles the main game loop

import pygame
import settings
import random
from commands import get_player_action
from ui import draw_game_info, draw_game_over_screen
import numpy as np
from killcam import play_killcam
from ai import get_ai_inputs
from transitions import play_start_transition, play_round_reset_transition

def reset_players_positions(players, game_settings):
    """
    Place les proies et les prédateurs sur la map.
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
    Vérifie si les deux joueurs se touchent.
    """
    distance = pygame.Vector2(player1.x, player1.y).distance_to(pygame.Vector2(player2.x, player2.y))
    collision_threshold = game_settings.get('map_width', settings.MAP_WIDTH_METERS) * settings.COLLISION_DISTANCE
    return distance < collision_threshold

def game_loop(screen, clock, players, map_renderer, game_data, gamepads, game_settings, initial_map_rotation):
    """
    Gère la partie complète.
    """
    map_rotation_angle = initial_map_rotation
    surface_data = game_data['settings']['map_data']
    
    scores = {p.id: 0 for p in players}
    round_count = 0
    
    reset_players_positions(players, game_settings)
    play_start_transition(screen, clock, players, map_renderer, map_rotation_angle, game_settings)

    game_over = False
    while not game_over:
        round_count += 1
        round_key = f"round_{round_count}"
        
        active_players = list(players)
        
        round_data = { 'frame_data': { 'time': [] } }
        for p in players:
            round_data['frame_data'][f'player_{p.id}'] = {
                'pos_x': [], 'pos_y': [], 'pos_z': [], 'vel_x': [], 'vel_y': [], 
                'acc_x': [], 'acc_y': [], 'wac': [], 'slope': [], 'color': p.color
            }

        capture_events = []
        round_time = 0.0
        round_running = True
        while round_running:
            dt = clock.tick(settings.FPS) / 1000.0
            if dt == 0: continue
            round_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None

            for player in active_players:
                action = get_ai_inputs(player, active_players, game_settings) if player.is_ai else get_player_action(player.id, gamepads, map_rotation_angle)
                player.update(action['direction'], action['intensity'], dt, surface_data, game_settings)
            
            round_data['frame_data']['time'].append(round_time)
            for p in players:
                frame = round_data['frame_data'][f'player_{p.id}']
                frame['pos_x'].append(p.x)
                frame['pos_y'].append(p.y)
                frame['pos_z'].append(p.get_current_z(surface_data, game_settings))
                frame['vel_x'].append(p.velocity.x)
                frame['vel_y'].append(p.velocity.y)
                frame['acc_x'].append(p.acceleration.x)
                frame['acc_y'].append(p.acceleration.y)
                frame['wac'].append(p.Wac)
                frame['slope'].append(p.slope)

            predators = [p for p in active_players if p.role == 'predator']
            if predators:
                captured_in_frame = []
                remaining_prey = [p for p in active_players if p.role == 'prey']
                for prey in remaining_prey:
                    for predator in predators:
                        if check_collision(predator, prey, game_settings):
                            prey.is_active = False
                            captured_in_frame.append({'prey': prey, 'predator': predator})
                            break 
                if captured_in_frame:
                    for capture in captured_in_frame:
                        capture_events.append({'time': round_time, 'predator_id': capture['predator'].id, 'prey_id': capture['prey'].id})
                    active_players = [p for p in active_players if p.is_active]
                    
                    if not any(p.role == 'prey' for p in active_players):
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
            
            for player in active_players:
                map_renderer.draw_point(player.x, player.y, player.color, map_rotation_angle)
            draw_game_info(screen, scores, round_time, players, game_settings['round_duration'])
            pygame.display.flip()

        round_winner_role = 'predator' if not any(p.role == 'prey' for p in active_players) else ('prey' if round_time >= game_settings.get('round_duration', 30) else None)
        for key, value in round_data['frame_data'].items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items(): value[sub_key] = np.array(sub_value)
            else: round_data['frame_data'][key] = np.array(value)
        game_data['rounds'][round_key] = round_data
        
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
    
    draw_game_over_screen(screen, clock, gamepads, players, scores, game_settings)
    
    return game_data
