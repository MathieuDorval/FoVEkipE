#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __  __     __     __         __         ______     ______     __    __    
#   /\ \/ /    /\ \   /\ \       /\ \       /\  ___\   /\  __ \   /\ "-./  \   
#   \ \  _"-.  \ \ \  \ \ \____  \ \ \____  \ \ \____  \ \  __ \  \ \ \-./\ \  
#    \ \_\ \_\  \ \_\  \ \_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_\ \ \_\ 
#     \/_/\/_/   \/_/   \/_____/   \/_____/   \/_____/   \/_/\/_/   \/_/  \/_/
#   (version 03/10)
#   → Manages the display of the killcam at the end of the round

import pygame
import settings
import random
import math
import numpy as np
import copy

from ui import draw_killcam_hud
from language import get_text

class Particle:
    def __init__(self, x, y, z, color):
        """
        Creation of a particle, with its position, velocity, and color.
        """
        self.x, self.y, self.z = x, y, z
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.vz = random.uniform(-2, 2)
        self.lifespan = 1.0
        self.color = color

    def update(self, dt):
        """
        Update the particle's location based on its velocity.
        """
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.lifespan -= dt

def _find_closest_index(time_array, target_time):
    """
    Find the closest index in a NumPy array.
    """
    return np.argmin(np.abs(time_array - target_time))

def play_killcam(screen, clock, map_renderer, game_data, map_rotation_angle, round_winner_role, capture_events, game_settings):
    """
    Display the killcam.
    """
    if not round_winner_role or round_winner_role == 'None':
        if round_winner_role == 'predator' and not capture_events:
            return {}

    round_key = f"round_{len(game_data['rounds'])}"
    round_data = game_data['rounds'][round_key]
    
    frame_data = copy.deepcopy(round_data.get('frame_data', {}))
    
    for key, value in frame_data.items():
        if isinstance(value, list):
            frame_data[key] = np.array(value)
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    value[sub_key] = np.array(sub_value)
    
    time_data = frame_data.get('time', np.array([]))
    
    if time_data.size < 2:
        return {}

    if round_winner_role == 'predator' and capture_events:
        MAX_FAST_PART_REAL_TIME = 3.0
        SLOW_MO_DURATION_GAME_TIME = 0.5
        SLOW_MO_SPEED = 0.5
        TRAIL_LENGTH = 8
        last_kill_time = capture_events[-1]['time']
        first_kill_time = capture_events[0]['time']
        slow_mo_start_game_time = max(0, last_kill_time - SLOW_MO_DURATION_GAME_TIME)
        start_replay_time = max(0, first_kill_time - 1.0)
        game_time_in_fast_part = slow_mo_start_game_time - start_replay_time
        fast_part_speed = 1.0
        if game_time_in_fast_part > MAX_FAST_PART_REAL_TIME:
            fast_part_speed = game_time_in_fast_part / MAX_FAST_PART_REAL_TIME
        real_duration_fast_part = game_time_in_fast_part / fast_part_speed if fast_part_speed > 0 else 0
        real_duration_slow_part = (last_kill_time - slow_mo_start_game_time) / SLOW_MO_SPEED
        total_killcam_duration = real_duration_fast_part + real_duration_slow_part
        all_particles, triggered_kill_indices, real_time_elapsed, current_game_time_to_show = [], set(), 0, start_replay_time
        
        running = True
        while running:
            dt = clock.tick(settings.FPS) / 1000.0
            if dt == 0: continue
            real_time_elapsed += dt
            current_speed = fast_part_speed if current_game_time_to_show < slow_mo_start_game_time else SLOW_MO_SPEED
            current_game_time_to_show += dt * current_speed
            frame_index = _find_closest_index(time_data, current_game_time_to_show)

            for i, event in enumerate(capture_events):
                if i not in triggered_kill_indices and current_game_time_to_show >= event['time']:
                    triggered_kill_indices.add(i)
                    prey_key = f"player_{event['prey_id']}"
                    if prey_key in game_data['players']:
                        prey_data = game_data['players'][prey_key]
                        kill_frame_index = _find_closest_index(time_data, event['time'])
                        if frame_data[prey_key]['pos_x'].size > kill_frame_index:
                            kill_pos_x = frame_data[prey_key]['pos_x'][kill_frame_index]
                            kill_pos_y = frame_data[prey_key]['pos_y'][kill_frame_index]
                            kill_pos_z = (map_renderer.get_z(kill_pos_x, kill_pos_y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
                            all_particles.extend([Particle(kill_pos_x, kill_pos_y, kill_pos_z, prey_data['color']) for _ in range(settings.KILLCAM_N_PARTICLES)])

            screen.fill(settings.BLACK)
            map_renderer.draw_map(map_rotation_angle, game_settings)
            
            for key, p_data in game_data['players'].items():
                if not key.startswith('player_'): continue
                player_id = int(key.split('_')[-1])
                is_alive = all(event['prey_id'] != player_id or current_game_time_to_show < event['time'] for event in capture_events)
                if is_alive and frame_data[f'player_{player_id}']['pos_x'].size > frame_index:
                    pos_x, pos_y = frame_data[f'player_{player_id}']['pos_x'][frame_index], frame_data[f'player_{player_id}']['pos_y'][frame_index]
                    for i in range(1, TRAIL_LENGTH):
                        if (trail_index := frame_index - i * 2) >= 0:
                            trail_x, trail_y = frame_data[key]['pos_x'][trail_index], frame_data[key]['pos_y'][trail_index]
                            trail_z = (map_renderer.get_z(trail_x, trail_y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
                            map_renderer.draw_particle(trail_x, trail_y, trail_z, p_data['color'], 150 * (1 - i / TRAIL_LENGTH), map_rotation_angle)
                    map_renderer.draw_point(pos_x, pos_y, p_data['color'], map_rotation_angle)
            for p in all_particles:
                p.update(dt)
                if p.lifespan > 0: map_renderer.draw_particle(p.x, p.y, p.z, p.color, int(p.lifespan * 255), map_rotation_angle)
            all_particles = [p for p in all_particles if p.lifespan > 0]
            draw_killcam_hud(screen, get_text('killcam_label'), get_text('catch_label'), (255, 50, 50))
            pygame.display.flip()
            if real_time_elapsed >= total_killcam_duration and not all_particles: running = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return

    elif round_winner_role == 'prey':
        TRAIL_LENGTH = 8
        MAX_REPLAY_DURATION = 4.0
        
        round_end_time = time_data[-1]
        start_replay_time = 0
        if not capture_events:
            start_replay_time = max(0, round_end_time - 3.0)
        else:
            start_replay_time = max(0, capture_events[0]['time'] - 1.0)
        
        game_time_to_replay = round_end_time - start_replay_time
        replay_speed = max(1.0, game_time_to_replay / MAX_REPLAY_DURATION)
        total_replay_duration = game_time_to_replay / replay_speed

        all_particles, triggered_kill_indices, real_time_elapsed, current_game_time_to_show = [], set(), 0, start_replay_time
        
        running_replay = True
        while running_replay:
            dt = clock.tick(settings.FPS) / 1000.0
            if dt == 0: continue
            real_time_elapsed += dt
            current_game_time_to_show += dt * replay_speed
            frame_index = _find_closest_index(time_data, current_game_time_to_show)

            for i, event in enumerate(capture_events):
                if i not in triggered_kill_indices and current_game_time_to_show >= event['time']:
                    triggered_kill_indices.add(i)
                    prey_key = f"player_{event['prey_id']}"
                    if prey_key in game_data['players']:
                        prey_data = game_data['players'][prey_key]
                        kill_frame_index = _find_closest_index(time_data, event['time'])
                        if frame_data[prey_key]['pos_x'].size > kill_frame_index:
                            kill_pos_x, kill_pos_y = frame_data[prey_key]['pos_x'][kill_frame_index], frame_data[prey_key]['pos_y'][kill_frame_index]
                            kill_pos_z = (map_renderer.get_z(kill_pos_x, kill_pos_y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
                            all_particles.extend([Particle(kill_pos_x, kill_pos_y, kill_pos_z, prey_data['color']) for _ in range(settings.KILLCAM_N_PARTICLES)])

            screen.fill(settings.BLACK)
            map_renderer.draw_map(map_rotation_angle, game_settings)
            
            for key, p_data in game_data['players'].items():
                if not key.startswith('player_'): continue
                player_id = int(key.split('_')[-1])
                is_alive = all(event['prey_id'] != player_id or current_game_time_to_show < event['time'] for event in capture_events)
                if is_alive and frame_data[key]['pos_x'].size > frame_index:
                    pos_x, pos_y = frame_data[key]['pos_x'][frame_index], frame_data[key]['pos_y'][frame_index]
                    for i in range(1, TRAIL_LENGTH):
                        if (trail_index := frame_index - i * 2) >= 0:
                            trail_x, trail_y = frame_data[key]['pos_x'][trail_index], frame_data[key]['pos_y'][trail_index]
                            trail_z = (map_renderer.get_z(trail_x, trail_y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
                            map_renderer.draw_particle(trail_x, trail_y, trail_z, p_data['color'], 150 * (1 - i / TRAIL_LENGTH), map_rotation_angle)
                    map_renderer.draw_point(pos_x, pos_y, p_data['color'], map_rotation_angle)

            for p in all_particles:
                p.update(dt)
                if p.lifespan > 0: map_renderer.draw_particle(p.x, p.y, p.z, p.color, int(p.lifespan * 255), map_rotation_angle)
            all_particles = [p for p in all_particles if p.lifespan > 0]
            
            draw_killcam_hud(screen, get_text('killcam_label'), get_text('escape_label'), (50, 255, 50))
            pygame.display.flip()
            if real_time_elapsed >= total_replay_duration: running_replay = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return

        predators_data = {k: v for k, v in game_data['players'].items() if v['role'] == 'predator'}
        for key, p_data in predators_data.items():
            final_frame_index = -1
            pos_x, pos_y = frame_data[key]['pos_x'][final_frame_index], frame_data[key]['pos_y'][final_frame_index]
            pos_z = (map_renderer.get_z(pos_x, pos_y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
            all_particles.extend([Particle(pos_x, pos_y, pos_z, p_data['color']) for _ in range(settings.KILLCAM_N_PARTICLES)])
        
        explosion_time = 0
        while explosion_time < 1.5:
            dt = clock.tick(settings.FPS) / 1000.0
            explosion_time += dt
            screen.fill(settings.BLACK)
            map_renderer.draw_map(map_rotation_angle, game_settings)
            for key, p_data in game_data['players'].items():
                if p_data['role'] == 'prey' and all(event['prey_id'] != int(key.split('_')[-1]) for event in capture_events):
                    final_frame_index = -1
                    pos_x, pos_y = frame_data[key]['pos_x'][final_frame_index], frame_data[key]['pos_y'][final_frame_index]
                    map_renderer.draw_point(pos_x, pos_y, p_data['color'], map_rotation_angle)
            for p in all_particles:
                p.update(dt)
                if p.lifespan > 0: map_renderer.draw_particle(p.x, p.y, p.z, p.color, int(p.lifespan * 255), map_rotation_angle)
            all_particles = [p for p in all_particles if p.lifespan > 0]
            draw_killcam_hud(screen, get_text('killcam_label'), get_text('escape_label'), (50, 255, 50))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return

    final_positions = {}
    last_frame_index = time_data.size - 1
    if last_frame_index >= 0:
        for key, p_data in game_data['players'].items():
            if not key.startswith('player_'): continue
            player_id = int(key.split('_')[-1])
            player_frame_data = frame_data[key]
            
            is_captured = False
            for event in capture_events:
                if event['prey_id'] == player_id:
                    capture_frame_index = _find_closest_index(time_data, event['time'])
                    pos_x = player_frame_data['pos_x'][capture_frame_index]
                    pos_y = player_frame_data['pos_y'][capture_frame_index]
                    final_positions[player_id] = {'x': pos_x, 'y': pos_y}
                    is_captured = True
                    break
            
            if not is_captured:
                pos_x = player_frame_data['pos_x'][last_frame_index]
                pos_y = player_frame_data['pos_y'][last_frame_index]
                final_positions[player_id] = {'x': pos_x, 'y': pos_y}

    return final_positions