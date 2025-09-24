#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/
#    __    __     ______     ______   ______    
#   /\ "-./  \   /\  __ \   /\  == \ /\  ___\   
#   \ \ \-./\ \  \ \  __ \  \ \  _-/ \ \___  \  
#    \ \_\ \ \_\  \ \_\ \_\  \ \_\    \/\_____\ 
#     \/_/  \/_/   \/_/\/_/   \/_/     \/_____/
#   (version 14/09)
#   -> Manages map generation and selection

import numpy as np
import noise
import settings

def _find_max_slope(terrain, game_settings):
    """
    Calcule la pente la plus raide d'une map.
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
    Ajuste les valeurs d'une map pour ramener la hauteur minimal d'une map à 0.
    """
    current_min_height = np.min(normalized_terrain)
    adjusted_normalized_terrain = normalized_terrain - current_min_height
    return adjusted_normalized_terrain

def _adjust_height(normalized_terrain, game_settings):
    """
    Modifie la hauteur d'une map pour respecter la hauteur et pente maxi.
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

def generate_noise_terrain(width, height, scale, octaves, persistence, lacunarity, seed):
    """
    Génère une map avec du bruit de perlin, via les paramètres renseignés.
    """
    terrain = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            nx, ny = x / width - 0.5, y / height - 0.5
            noise_value = noise.pnoise2(nx * scale, ny * scale,
                octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                repeatx=1024, repeaty=1024, base=seed)
            terrain[y, x] = noise_value
    
    min_val, max_val = np.min(terrain), np.max(terrain)
    return (terrain - min_val) / (max_val - min_val) if (max_val - min_val) > 0 else terrain

def generate_flat_terrain(width, height):
    """
    Génère une map entièrement plate. (map unique)
    """
    return np.zeros((height, width))

def generate_mountain_terrain(width, height):
    """
    Génère une map avec une grosse montagne centrale. (map unique)
    """
    center_x, center_y = width // 2, height // 2
    x_vals, y_vals = np.meshgrid(np.arange(width), np.arange(height))
    dist = np.sqrt((x_vals - center_x)**2 + (y_vals - center_y)**2)
    mountain_shape = np.maximum(0, 1 - (dist / (width / 2))**2)
    noise_vals = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            noise_vals[y,x] = noise.pnoise2((x/width-0.5)*8, (y/height-0.5)*8, octaves=3, base=20) * 0.2
    terrain = mountain_shape + noise_vals
    min_val, max_val = np.min(terrain), np.max(terrain)
    return (terrain - min_val) / (max_val - min_val) if (max_val - min_val) > 0 else terrain

def generate_matlab_terrain(width, height):
    """
    Génère la même map que celle Matlab initiale. (map unique)
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
    Génère la map demandé en fonction du nom.
    pour ajouter une map, utiliser la fonction "generate_noise_terrain" en lui donnant les paramètres que l'on veut :
    - largeur
    - hauteur
    - scale         (les détails, plus c'est petit plus c'est smooth)
    - octave        (le nombre de fois que l'on repasse dessus, plus c'est grand plus c'est "anarchique")
    - persistance   (la diff entre 2 octaves, plus c'est petit plus c'est smooth)
    - lacunarity    (fréquence entre 2 octaves)
    - seed          (gère l'aléatoire)
    - facteur       (gère la hauteur max de la map par rapport à celle des settings)
    """
    normalized_terrain = np.zeros((width, height))

    
    if map_name     == "Flat": normalized_terrain       = generate_flat_terrain(width, height)
    elif map_name   == "MatLab": normalized_terrain     = generate_matlab_terrain(width, height)
    elif map_name   == "Mountain": normalized_terrain   = generate_mountain_terrain(width, height)
    elif map_name   == "Default": normalized_terrain    = generate_noise_terrain(width, height, 2.0, 2, 0.5, 1.5, 50) * 0.3
    elif map_name   == "Hills": normalized_terrain      = generate_noise_terrain(width, height, 3.0, 4, 0.4, 2.0, 100) * 0.7
    elif map_name   == "Plain": normalized_terrain      = generate_noise_terrain(width, height, 5.0, 1, 0.5, 2.0, 73) * 0.15
    else: normalized_terrain                            = generate_noise_terrain(width, height, 2.0, 2, 0.5, 1.5, 50)

    return _adjust_height(normalized_terrain, game_settings)