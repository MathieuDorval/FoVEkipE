#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______   __         ______     __  __     ______     ______    
#   /\  == \ /\ \       /\  __ \   /\ \_\ \   /\  ___\   /\  == \   
#   \ \  _-/ \ \ \____  \ \  __ \  \ \____ \  \ \  __\   \ \  __<   
#    \ \_\    \ \_____\  \ \_\ \_\  \/\_____\  \ \_____\  \ \_\ \_\ 
#     \/_/     \/_____/   \/_/\/_/   \/_____/   \/_____/   \/_/ /_/
#   (version 14/09)
#   -> Sets the player's parameters and positions

import pygame
import settings
import math
from physics import calculate_physics_update

class Player:
    """
    Class pour un joueur.
    """
    def __init__(self, id, color, animal_data, role, is_ai):
        """
        Initialise le joueur et ses constantes.
        """
        self.id = id
        self.color = color
        self.x = 0.0
        self.y = 0.0
        self.animal = animal_data
        self.stats = self.animal['stats']
        self.role = role
        self.is_ai = is_ai
        self.is_active = True
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.Wac = 0.0
        self.slope = 0.0
        
    def get_current_slope(self, surface_data, game_settings):
        """
        Calcule la pente actuelle sous le joueur.
        """
        map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
        map_points = settings.MAP_POINTS
    
        if self.velocity.length_squared() < 1e-6:
            return 0.0

        delta_dist = map_width / (map_points - 1)
        if delta_dist == 0:
            return 0.0

        map_x = int(((self.x + map_width / 2) / map_width) * (map_points - 1))
        map_y = int(((self.y + map_width / 2) / map_width) * (map_points - 1))
    
        map_x = max(1, min(map_x, map_points - 2))
        map_y = max(1, min(map_y, map_points - 2))

        z_xp1 = surface_data[map_y, map_x + 1]
        z_xm1 = surface_data[map_y, map_x - 1]
        dz_dx = (z_xp1 - z_xm1) / (2 * delta_dist)

        z_yp1 = surface_data[map_y + 1, map_x]
        z_ym1 = surface_data[map_y - 1, map_x]
        dz_dy = (z_yp1 - z_ym1) / (2 * delta_dist)

        gradient_vector = pygame.Vector2(dz_dx, dz_dy)

        slope_magnitude = gradient_vector.dot(self.velocity.normalize())
    
        return math.atan(slope_magnitude)
    
    def get_current_z(self, surface_data, game_settings):
        """
        Calcule l'altitude (z) du joueur.
        """
        map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
        map_points = settings.MAP_POINTS
        
        map_x = int(((self.x + map_width / 2) / map_width) * (map_points - 1))
        map_y = int(((self.y + map_width / 2) / map_width) * (map_points - 1))
        
        map_x = max(0, min(map_x, map_points - 1))
        map_y = max(0, min(map_y, map_points - 1))
        
        return surface_data[map_y, map_x]
        
    def update(self, direction, intensity, dt, surface_data, game_settings):
        """
        Met à jour le joueur.
        """
        prev_x, prev_y = self.x, self.y

        slope = self.get_current_slope(surface_data, game_settings)
        self.slope = slope

        new_velocity, new_wac, self.acceleration = calculate_physics_update(self, direction, intensity, dt, slope, game_settings)
        
        self.velocity = new_velocity
        self.Wac = new_wac

        MAX_SPEED = 50.0
        if self.velocity.length_squared() > MAX_SPEED**2:
            self.velocity.scale_to_length(MAX_SPEED)
        
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt
        
        half_map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS) / 2
        if abs(self.x) > half_map_width or abs(self.y) > half_map_width:
            self.x, self.y = prev_x, prev_y
            self.velocity = pygame.Vector2(0, 0)