#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______     __    
#   /\  __ \   /\ \   
#   \ \  __ \  \ \ \  
#    \ \_\ \_\  \ \_\ 
#     \/_/\/_/   \/_/
#   (version 14/09)
#   -> Manages AI

import pygame
import settings

def get_ai_inputs(player, all_players, game_settings):
    """
    Define the commands for an AI player.
    """
    if player.role == 'predator':
        return get_predator_inputs(player, all_players, game_settings)
    else:
        return get_prey_inputs(player, all_players, game_settings)

def get_predator_inputs(predator, all_players, game_settings):
    """
    AI Logic for the Predator.
    - HUNTING → approaches prey at 60% of max force
    - ATTACKING → rushes towards prey at 100% of max force
    - RECOVERING → recovers its wac
    """
    preys = [p for p in all_players if p.role == 'prey' and p.is_active]
    if not preys:
        return {'direction': pygame.Vector2(0, 0), 'intensity': 0.0}

    if not hasattr(predator, 'ai_state'):
        predator.ai_state = 'HUNTING'

    closest_prey = min(preys, key=lambda p: pygame.Vector2(predator.x, predator.y).distance_to((p.x, p.y)))
    distance_to_prey = pygame.Vector2(predator.x, predator.y).distance_to((closest_prey.x, closest_prey.y))
    
    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    attack_distance = map_width * 0.20
    wac_ratio = predator.Wac / predator.stats.get('WacMax', 1)

    if predator.ai_state == 'RECOVERING':
        if wac_ratio < 0.60: 
            predator.ai_state = 'HUNTING'
        direction_to_prey = (pygame.Vector2(closest_prey.x, closest_prey.y) - pygame.Vector2(predator.x, predator.y)).normalize()
        return {'direction': direction_to_prey, 'intensity': 0.0}

    if wac_ratio > 0.90:
        predator.ai_state = 'RECOVERING'
        direction_to_prey = (pygame.Vector2(closest_prey.x, closest_prey.y) - pygame.Vector2(predator.x, predator.y)).normalize()
        return {'direction': direction_to_prey, 'intensity': 0.0}

    if predator.ai_state == 'ATTACKING':
        if distance_to_prey > attack_distance * 1.2:
            predator.ai_state = 'HUNTING'
        direction_to_prey = (pygame.Vector2(closest_prey.x, closest_prey.y) - pygame.Vector2(predator.x, predator.y)).normalize()
        return {'direction': direction_to_prey, 'intensity': 1.0}

    if predator.ai_state == 'HUNTING':
        if distance_to_prey < attack_distance:
            predator.ai_state = 'ATTACKING'
        direction_to_prey = (pygame.Vector2(closest_prey.x, closest_prey.y) - pygame.Vector2(predator.x, predator.y)).normalize()
        return {'direction': direction_to_prey, 'intensity': 0.6}

    return {'direction': pygame.Vector2(0, 0), 'intensity': 0.0}


def get_prey_inputs(prey, all_players, game_settings):
    """
    AI Logic for the Prey.
    - IDLE → doesn't move if the predator is far away
    - CAUTIOUS → moves away slowly if the predator is at mid-range
    - FLEEING → flees at 100% of max force if the predator is close, while avoiding the edges
    """
    predators = [p for p in all_players if p.role == 'predator' and p.is_active]
    if not predators:
        return {'direction': pygame.Vector2(0, 0), 'intensity': 0.0}

    if not hasattr(prey, 'ai_state'):
        prey.ai_state = 'IDLE'

    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    closest_predator = min(predators, key=lambda p: pygame.Vector2(prey.x, prey.y).distance_to((p.x, p.y)))
    distance_to_predator = pygame.Vector2(prey.x, prey.y).distance_to((closest_predator.x, closest_predator.y))
    
    flee_distance = map_width * 0.15
    cautious_distance = map_width * 0.45

    if distance_to_predator <= flee_distance:
        prey.ai_state = 'FLEEING'
    elif distance_to_predator <= cautious_distance:
        prey.ai_state = 'CAUTIOUS'
    else:
        prey.ai_state = 'IDLE'

    if prey.ai_state == 'IDLE':
        return {'direction': pygame.Vector2(0, 0), 'intensity': 0.0}

    if prey.ai_state == 'CAUTIOUS':
        direction_away = (pygame.Vector2(prey.x, prey.y) - pygame.Vector2(closest_predator.x, closest_predator.y))
        if direction_away.length() > 0:
            return {'direction': direction_away.normalize(), 'intensity': 0.5}
        else:
            return {'direction': pygame.Vector2(0,0), 'intensity': 0.0}

    if prey.ai_state == 'FLEEING':
        best_direction = pygame.Vector2(0, 0)
        max_score = -float('inf')
        to_predator_vec = pygame.Vector2(closest_predator.x - prey.x, closest_predator.y - prey.y)

        if to_predator_vec.length_squared() == 0:
            return {'direction': pygame.Vector2(1, 0), 'intensity': 1.0}

        for i in range(8):
            angle = i * (360 / 8)
            direction = pygame.Vector2(1, 0).rotate(angle)
            
            score_pred = direction.dot(-to_predator_vec.normalize())
            
            future_pos = pygame.Vector2(prey.x, prey.y) + direction * (map_width * 0.2)
            norm_dist_from_center = max(abs(future_pos.x), abs(future_pos.y)) / (map_width / 2)
            score_border = 1.0 - norm_dist_from_center**4
            
            if norm_dist_from_center > 1.0: score_border -= 10
            total_score = (score_pred * 1.0) + (score_border * 1.5)
            
            angle_to_predator = abs(direction.angle_to(to_predator_vec.normalize()))
            if angle_to_predator < 22.5: total_score -= 1000
            if total_score > max_score:
                max_score = total_score
                best_direction = direction
        
        return {'direction': best_direction.normalize(), 'intensity': 1.0}
    
    return {'direction': pygame.Vector2(0, 0), 'intensity': 0.0}