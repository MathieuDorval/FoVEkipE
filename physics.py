#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______   __  __     __  __     ______     __     ______     ______    
#   /\  == \ /\ \_\ \   /\ \_\ \   /\  ___\   /\ \   /\  ___\   /\  ___\   
#   \ \  _-/ \ \  __ \  \ \____ \  \ \___  \  \ \ \  \ \ \____  \ \___  \  
#    \ \_\    \ \_\ \_\  \/\_____\  \/\_____\  \ \_\  \ \_____\  \/\_____\ 
#     \/_/     \/_/\/_/   \/_____/   \/_____/   \/_/   \/_____/   \/_____/ 
#   (version 14/09)
#   -> Manages game physics, based on the FoVE model

import pygame
import settings
import math

def calculate_physics_update(player, direction_vector, intensity, dt, slope_angle, game_settings):
    """
    Determine the player's new velocity and state.
    Based on the FoVE model.
    """
    current_velocity = player.velocity
    current_speed = current_velocity.length()
    current_wac = player.Wac

    stats = player.stats
    m           = max(1e-6, abs(stats.get('mass', 1)))
    k           = stats.get('k', 0)
    Ff          = stats.get('Ff', 0)
    g           = settings.GRAVITY
    slopeOpt    = stats.get('slopeOpt', 0) if game_settings.get('slope_correction', True) else 100
    F0i         = stats.get('F0i', 0)
    V0i         = stats.get('V0i', 1) 
    F0c         = stats.get('F0c', 0)
    V0c         = stats.get('V0c', 1) 
    WacMax      = stats.get('WacMax', 1)
    Fbrake      = stats.get('Fbrake', 0) if game_settings.get('brake_correction', True) else 0
    wac_ratio_setting = game_settings.get('wac_ratio', 1.0)
    
    use_vc_speed = game_settings.get('vc_speed', False) and intensity == 0 and direction_vector.length_squared() > 0

    Fi = F0i * (1 - current_speed / V0i) if V0i > 0 else 0
    Fc = F0c * (1 - current_speed / V0c) if V0c > 0 else 0
    
    wac_ratio = (current_wac / WacMax) if WacMax > 0 else 0
    Fmax = Fi - (Fi - Fc) * wac_ratio
    
    Fr = 0
    if use_vc_speed:
        Fr = Fc
    else:
        Fr = Fmax * intensity

    propulsion_force = pygame.Vector2(0, 0)
    if direction_vector.length_squared() > 0:
        propulsion_force = direction_vector.normalize() * Fr

    total_force = propulsion_force

    if current_speed > 0:
        velocity_direction = current_velocity.normalize()

        adjusted_slope_angle = slope_angle
        if slope_angle < -slopeOpt:
            adjusted_slope_angle = -2 * slopeOpt - slope_angle
        
        Fg_magnitude = m * g * math.sin(adjusted_slope_angle)
        gravity_force = -velocity_direction * Fg_magnitude
        total_force += gravity_force

        drag_magnitude = k * (current_speed ** 2)

        if intensity == 0 and not use_vc_speed:
            braking_force_magnitude = Fbrake + Ff + drag_magnitude
            if braking_force_magnitude * dt > current_speed * m:
                new_velocity = pygame.Vector2(0, 0)
                acceleration = -current_velocity / dt if dt > 0 else pygame.Vector2(0,0)
                Vc = V0c * (1 - Fr / F0c) if F0c > 0 else 0
                dWac = (new_velocity.length() - Vc) * dt
                if dWac < 0: dWac *= wac_ratio_setting
                new_wac = min(WacMax, max(0, current_wac + dWac))
                return new_velocity, new_wac, acceleration

            braking_force = -velocity_direction * Fbrake
            total_force += braking_force
            
        drag_force = -velocity_direction * drag_magnitude
        total_force += drag_force

        friction_force = -velocity_direction * Ff
        total_force += friction_force

    acceleration = total_force / m
    
    MAX_ACCELERATION = 100.0
    if acceleration.length_squared() > MAX_ACCELERATION**2:
        acceleration.scale_to_length(MAX_ACCELERATION)

    new_velocity = current_velocity + acceleration * dt
    
    Vc = V0c * (1 - Fr / F0c) if F0c > 0 else 0
    
    dWac = 0
    if use_vc_speed:
        dWac = 0
    else:
        dWac = (new_velocity.length() - Vc) * dt

    if dWac > 0 :
        dWac *= wac_ratio_setting
    elif dWac < 0:
        dWac /= wac_ratio_setting if wac_ratio_setting > 0 else 1

    new_wac = min(WacMax, max(0, current_wac + dWac))
    
    return new_velocity, new_wac, acceleration