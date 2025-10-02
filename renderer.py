#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______     ______     __   __     _____     ______     ______     ______     ______    
#   /\  == \   /\  ___\   /\ "-.\ \   /\  __-.  /\  ___\   /\  == \   /\  ___\   /\  == \   
#   \ \  __<   \ \  __\   \ \ \-.  \  \ \ \/\ \ \ \  __\   \ \  __<   \ \  __\   \ \  __<   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \____-  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\ \_\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/____/   \/_____/   \/_/ /_/   \/_____/   \/_/ /_/
#   (version 14/09)
#   -> Manage the graphical rendering

import pygame
import math
import settings

class MapRenderer:
    def __init__(self, screen, rect, map_data, game_settings):
        """
        Initialise le rendu.
        """
        self.screen = screen
        self.rect = rect
        self.map_data = map_data
        self.game_settings = game_settings
        self.map_cache = None
        self.last_rendered_angle = None
        self._calculate_scale_and_offset()
        
    def _calculate_scale_and_offset(self):
        """
        Calcul l'échelle et l'offset pour centrer la map.
        """
        map_width = self.game_settings.get('map_width', settings.MAP_WIDTH_METERS)
        z_min, z_max = self.map_data.min(), self.map_data.max()
        z_range = z_max - z_min
        
        map_visual_width = map_width * math.sqrt(2) * math.cos(settings.ISO_ANGLE)
        map_visual_height = map_width * math.sqrt(2) * math.sin(settings.ISO_ANGLE) + (z_range * settings.Z_BOOST_FACTOR)
        
        if map_visual_width == 0 or map_visual_height == 0: self.scale = 1
        else:
            scale_width = self.rect.width * 0.75 / map_visual_width
            scale_height = self.rect.height * 0.75 / map_visual_height
            self.scale = min(scale_width, scale_height)
        
        self.x_offset = self.rect.centerx
        map_projected_height = (z_max * settings.Z_BOOST_FACTOR) * self.scale
        self.y_offset = self.rect.centery + (map_projected_height / 2)

    def update_map_data(self, new_map_data, game_settings):
        """
        Met à jour les données de la carte.
        """
        self.map_data = new_map_data
        self.game_settings = game_settings
        self.map_cache = None
        self.last_rendered_angle = None
        self._calculate_scale_and_offset()
        
    def _project_isometric(self, x, y, z, angle):
        """
        Projete un point 3d en 2d.
        """
        rotated_x = x * math.cos(angle) - y * math.sin(angle)
        rotated_y = x * math.sin(angle) + y * math.cos(angle)
        
        screen_x = (rotated_x - rotated_y) * math.cos(settings.ISO_ANGLE) * self.scale
        screen_y = (rotated_x + rotated_y) * math.sin(settings.ISO_ANGLE) * self.scale - z * self.scale
        
        return int(screen_x + self.x_offset), int(screen_y + self.y_offset)

    def draw_map(self, rotation_angle, game_settings):
        """
        Dessine la map à l'écran.
        """
        if self.map_cache is not None and self.last_rendered_angle == rotation_angle:
            self.screen.blit(self.map_cache, self.rect.topleft)
            return

        self.map_cache = pygame.Surface(self.rect.size)
        self.map_cache.fill(settings.BLACK)
        
        map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
        
        for y in range(settings.MAP_POINTS - 1):
            for x in range(settings.MAP_POINTS - 1):
                p1_x = (x / (settings.MAP_POINTS - 1) - 0.5) * map_width
                p1_y = (y / (settings.MAP_POINTS - 1) - 0.5) * map_width
                p1_z = self.map_data[y, x] * settings.Z_BOOST_FACTOR
                
                p2_x = (x / (settings.MAP_POINTS - 1) - 0.5) * map_width
                p2_y = ((y + 1) / (settings.MAP_POINTS - 1) - 0.5) * map_width
                p2_z = self.map_data[y+1, x] * settings.Z_BOOST_FACTOR
                
                p3_x = ((x + 1) / (settings.MAP_POINTS - 1) - 0.5) * map_width
                p3_y = (y / (settings.MAP_POINTS - 1) - 0.5) * map_width
                p3_z = self.map_data[y, x+1] * settings.Z_BOOST_FACTOR
                
                p1_screen = self._project_isometric(p1_x, p1_y, p1_z, rotation_angle)
                p2_screen = self._project_isometric(p2_x, p2_y, p2_z, rotation_angle)
                p3_screen = self._project_isometric(p3_x, p3_y, p3_z, rotation_angle)

                avg_z = (p1_z + p2_z + p3_z) / 3
                color_intensity = int(avg_z / (settings.Z_BOOST_FACTOR) * 255)
                color_intensity = max(50, min(255, color_intensity))
                color = (color_intensity, color_intensity, color_intensity)
                
                pygame.draw.line(self.map_cache, color, p1_screen, p2_screen)
                pygame.draw.line(self.map_cache, color, p1_screen, p3_screen)

        self.screen.blit(self.map_cache, self.rect.topleft)
        self.last_rendered_angle = rotation_angle

    def get_z(self, x, y):
        """
        Obtenir le z d'un point sur la map.
        """
        map_width = self.game_settings.get('map_width', settings.MAP_WIDTH_METERS)
        map_points = settings.MAP_POINTS
        
        map_x = int(((x + map_width / 2) / map_width) * (map_points - 1))
        map_y = int(((y + map_width / 2) / map_width) * (map_points - 1))
        map_x = max(0, min(map_x, map_points - 1))
        map_y = max(0, min(map_y, map_points - 1))
        return self.map_data[map_y, map_x]

    def draw_point(self, x, y, color, rotation_angle):
        """
        Dessine les joueurs.
        """
        z = self.get_z(x, y) + settings.PLAYER_Z_OFFSET
        screen_pos = self._project_isometric(x, y, z * settings.Z_BOOST_FACTOR, rotation_angle)
        pygame.draw.circle(self.screen, color, screen_pos, settings.POINT_SCALE)

    def draw_particle(self, x, y, z, color, alpha, rotation_angle):
        """
        Dessine une particule.
        """
        screen_pos = self._project_isometric(x, y, z, rotation_angle)
        temp_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, (*color, alpha), (5, 5), 3)
        self.screen.blit(temp_surface, (screen_pos[0] - 5, screen_pos[1] - 5))