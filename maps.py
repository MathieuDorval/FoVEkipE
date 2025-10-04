#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __    __     ______     ______   ______    
#   /\ "-./  \   /\  __ \   /\  == \ /\  ___\   
#   \ \ \-./\ \  \ \  __ \  \ \  _-/ \ \___  \  
#    \ \_\ \ \_\  \ \_\ \_\  \ \_\    \/\_____\ 
#     \/_/  \/_/   \/_/\/_/   \/_/     \/_____/
#   (version 14/09)
#   → Manages map generation and selection

import numpy as np
import settings
from perlin_noise import PerlinNoise

def _find_max_slope(terrain, game_settings):
    """
    Calculate the steepest slope of a map.
    """
    max_slope_found = 0
    width, height = terrain.shape
    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    delta_dist = map_width / (width - 1)
    if delta_dist == 0: return 0

    for y in range(height):
        for x in range(width):
            if x + 1 < width:
                dz = abs(terrain[y, x+1] - terrain[y, x])
                max_slope_found = max(max_slope_found, (dz / delta_dist) * 100)
            if y + 1 < height:
                dz = abs(terrain[y+1, x] - terrain[y, x])
                max_slope_found = max(max_slope_found, (dz / delta_dist) * 100)
    return max_slope_found

def _adjust_height_to_minimal(normalized_terrain):
    """
    Adjust the map's values to set its minimum height to 0.
    """
    current_min_height = np.min(normalized_terrain)
    adjusted_normalized_terrain = normalized_terrain - current_min_height
    return adjusted_normalized_terrain

def _adjust_height(normalized_terrain, game_settings):
    """
    Adjust the map's height to comply with the maximum height and slope limits.
    """
    map_width = game_settings.get('map_width', settings.MAP_WIDTH_METERS)
    current_max_height = map_width * settings.MAP_MAX_HEIGHT_RATIO
    
    for _ in range(10):
        scaled_terrain = normalized_terrain * current_max_height
        max_slope = _find_max_slope(scaled_terrain, game_settings)
        
        if max_slope > settings.MAX_SLOPE:
            current_max_height *= (settings.MAX_SLOPE / max_slope) * 0.99
        else:
            break

    adjusted_normalized_terrain = _adjust_height_to_minimal(normalized_terrain)
    return adjusted_normalized_terrain * current_max_height    

def generate_noise_terrain(width, height, scale, octaves, seed):
    """
    Generate a Perlin noise map based on the input parameters.
    """
    noise_gen = PerlinNoise(octaves=octaves, seed=seed)
    terrain = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            terrain[y][x] = noise_gen([x / scale, y / scale])
            
    min_val, max_val = np.min(terrain), np.max(terrain)
    return (terrain - min_val) / (max_val - min_val) if (max_val - min_val) > 0 else terrain


def generate_flat_terrain(width, height):
    """
    Create a perfectly flat map. (unique map)
    """
    return np.zeros((height, width))

def generate_mountain_terrain(width, height):
    """
    Generate a map with a high central peak. (unique map)
    """
    center_x, center_y = width // 2, height // 2
    x_vals, y_vals = np.meshgrid(np.arange(width), np.arange(height))
    dist = np.sqrt((x_vals - center_x)**2 + (y_vals - center_y)**2)
    mountain_shape = np.maximum(0, 1 - (dist / (width / 2))**2)
    
    noise_gen = PerlinNoise(octaves=3, seed=20)
    noise_vals = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            noise_vals[y,x] = noise_gen([x / 8, y / 8]) * 0.2

    terrain = mountain_shape + noise_vals
    min_val, max_val = np.min(terrain), np.max(terrain)
    return (terrain - min_val) / (max_val - min_val) if (max_val - min_val) > 0 else terrain

def generate_matlab_terrain(width, height):
    """
    Generate the initial MATLAB map. (unique map)
    """
    x = np.linspace(-3, 3, width)
    y = np.linspace(-3, 3, height)
    X, Y = np.meshgrid(x, y)
    Z = abs(3 * (1-X)**2 * np.exp(-(X**2) - (Y+1)**2) \
        - 10 * (X/5 - X**3 - Y**5) * np.exp(-X**2 - Y**2) \
        - 1/3 * np.exp(-(X+1)**2 - Y**2))
    min_val, max_val = np.min(Z), np.max(Z)
    return (Z - min_val) / (max_val - min_val) if (max_val-min_val) > 0 else Z

def generate_terrain(map_name, width, height, game_settings):
    """
    Generate the requested map based on the name.
    """
    normalized_terrain = np.zeros((width, height))
    # Allows adding maps with Perlin noise
    if map_name     == "Flat": normalized_terrain       = generate_flat_terrain(width, height)
    elif map_name   == "MatLab": normalized_terrain     = generate_matlab_terrain(width, height)
    elif map_name   == "Mountain": normalized_terrain   = generate_mountain_terrain(width, height)
    elif map_name   == "Default": normalized_terrain    = generate_noise_terrain(width, height, 100, 2, 50) * 0.3
    elif map_name   == "Hills": normalized_terrain      = generate_noise_terrain(width, height, 70, 4, 100) * 0.7
    elif map_name   == "Plain": normalized_terrain      = generate_noise_terrain(width, height, 200, 1, 73) * 0.15
    else: normalized_terrain                            = generate_noise_terrain(width, height, 100, 2, 50)

    return _adjust_height(normalized_terrain, game_settings)