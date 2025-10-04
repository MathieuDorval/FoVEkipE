#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __         ______     ______     ______    
#   /\ \       /\  __ \   /\  ___\   /\  ___\   
#   \ \ \____  \ \ \/\ \  \ \ \__ \  \ \___  \  
#    \ \_____\  \ \_____\  \ \_____\  \/\_____\ 
#     \/_____/   \/_____/   \/_____/   \/_____/ 
#   (version 03/10)
#   → Manages game data logging

import os
import scipy.io
import numpy as np
from datetime import datetime
import settings

def init_session_log(num_gamepads):
    """
    Initialize the main data structure for the game session.
    """
    session_data = {
        'settings': {
            'fps': settings.FPS,
            'map_points': settings.MAP_POINTS,
            'map_max_height_ratio': settings.MAP_MAX_HEIGHT_RATIO,
            'max_slope': settings.MAX_SLOPE,
            'gravity': settings.GRAVITY,
            'num_gamepads': num_gamepads,
            'session_start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'games': {}
    }
    return session_data

def add_game_to_log(session_data, game_settings, players):
    """
    Add a new game to the game session.
    """
    game_count = len(session_data['games']) + 1
    game_key = f"game_{game_count}"

    num_ai = sum(1 for p in players if p.is_ai)
    num_predators = sum(1 for p in players if p.role == 'predator')
    num_preys = sum(1 for p in players if p.role == 'prey')

    game_entry = {
        'launch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'settings': {
            'map_name': game_settings['map_name'],
            'map_data': game_settings['surface_data'],
            'map_width': game_settings['map_width'],
            'round_duration': game_settings['round_duration'],
            'winning_score': game_settings['winning_score'],
            'num_players': len(players),
            'num_ai': num_ai,
            'num_predators': num_predators,
            'num_preys': num_preys
        },
        'players': {},
        'rounds': {},
        'num_rounds': 0,
        'score_prey': 0,
        'score_predator': 0,
        'winner': 'None',
        'total_duration': 0.0
    }

    for p in players:
        game_entry['players'][f'player_{p.id}'] = {
            'animal': p.animal['name'],
            'stats': p.stats,
            'role': p.role,
            'is_ai': p.is_ai,
            'color': p.color
        }
    
    session_data['games'][game_key] = game_entry
    return game_entry

def add_round_to_game(game_data, players):
    """
    Add a new round to a match.
    """
    round_count = len(game_data['rounds']) + 1
    round_key = f"round_{round_count}"

    round_entry = {
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'winner_role': 'None',
        'duration': 0.0,
        'frame_data': {
            'time': []
        }
    }
    
    for p in players:
        round_entry['frame_data'][f'player_{p.id}'] = {
            'pos_x': [], 'pos_y': [], 'pos_z': [],
            'vel_x': [], 'vel_y': [], 'vel_total': [],
            'acc_x': [], 'acc_y': [], 'acc_total': [],
            'wac': [], 'slope': [], 'is_active': []
        }

    game_data['rounds'][round_key] = round_entry
    return round_entry

def add_frame_to_round(round_data, players, round_time, surface_data, game_settings):
    """
    Add a frame's data to a round.
    """
    frame_data = round_data['frame_data']
    frame_data['time'].append(round_time)

    for p in players:
        player_frame = frame_data[f'player_{p.id}']
        
        vel_total = p.velocity.length()
        acc_total = p.acceleration.length()
        
        player_frame['pos_x'].append(p.x)
        player_frame['pos_y'].append(p.y)
        player_frame['pos_z'].append(p.get_current_z(surface_data, game_settings))
        player_frame['vel_x'].append(p.velocity.x)
        player_frame['vel_y'].append(p.velocity.y)
        player_frame['vel_total'].append(vel_total)
        player_frame['acc_x'].append(p.acceleration.x)
        player_frame['acc_y'].append(p.acceleration.y)
        player_frame['acc_total'].append(acc_total)
        player_frame['wac'].append(p.Wac)
        player_frame['slope'].append(p.slope)
        player_frame['is_active'].append(1 if p.is_active else 0)

def finalize_game_data(game_data, scores, players, winning_score):
    """
    Update the match log with the final scores, the winner, and the durations.
    """
    predators = [p for p in players if p.role == 'predator']
    preys = [p for p in players if p.role == 'prey']

    predators_final_score = scores.get(predators[0].id, 0) if predators else 0
    preys_final_score = scores.get(preys[0].id, 0) if preys else 0

    game_data['num_rounds'] = len(game_data['rounds'])
    game_data['score_predator'] = predators_final_score
    game_data['score_prey'] = preys_final_score

    if predators_final_score >= winning_score:
        game_data['winner'] = 'predator'
    elif preys_final_score >= winning_score:
        game_data['winner'] = 'prey'
    else:
        game_data['winner'] = 'draw'

    total_duration = sum(r.get('duration', 0) for r in game_data['rounds'].values())
    game_data['total_duration'] = total_duration

def save_log_file(session_data):
    """
    Save the session data to a .mat file.
    """
    log_dir = "game_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created directory '{log_dir}' for game logs.")

    filename = datetime.now().strftime("%d_%m_%y_%H_%M.mat")
    filepath = os.path.join(log_dir, filename)

    for game_key, game_data in session_data['games'].items():
        for round_key, round_data in game_data['rounds'].items():
            for key, value in round_data['frame_data'].items():
                if isinstance(value, list):
                    round_data['frame_data'][key] = np.array(value)
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, list):
                             value[sub_key] = np.array(sub_value)
    
    try:
        scipy.io.savemat(filepath, {'session_data': session_data}, do_compression=True)
        print(f"Data saved in {filepath}")
    except Exception as e:
        print(f"Could not save data. {e}")