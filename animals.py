#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______     __   __     __     __    __     ______     __         ______    
#   /\  __ \   /\ "-.\ \   /\ \   /\ "-./  \   /\  __ \   /\ \       /\  ___\   
#   \ \  __ \  \ \ \-.  \  \ \ \  \ \ \-./\ \  \ \  __ \  \ \ \____  \ \___  \  
#    \ \_\ \_\  \ \_\\"\_\  \ \_\  \ \_\ \ \_\  \ \_\ \_\  \ \_____\  \/\_____\ 
#     \/_/\/_/   \/_/ \/_/   \/_/   \/_/  \/_/   \/_/\/_/   \/_____/   \/_____/ 
#   (version 14/09)
#   -> Stores FoVE's animal data

import math

ANIMALS_DATA = [
    {
        "name":             "Wolf",
        "image_path":       "ressources/wolf.png",
        "base_stats": {
            "F0i":          500,
            "V0i":          16,
            "F0c_ratio":    0.259,
            "V0c_ratio":    0.259,
            "Tau":          40,
            "mass":         20,
            "k":            0.4,
            "Ff":           100,
            "slopeOpt":     math.atan(0.05),
            "Fbrake_ratio": 0.1
        }
    },
    {
        "name":             "Deer",
        "image_path":       "ressources/deer.png",
        "base_stats": {
            "F0i":          7000,
            "V0i":          4,
            "F0c_ratio":    0.85,
            "V0c_ratio":    0.85,
            "Tau":          20,
            "mass":         20,
            "k":            0.4,
            "Ff":           200,
            "slopeOpt":     math.atan(0.1),
            "Fbrake_ratio": 0.3
        }
    },
    {
        "name":             "Giga Wolf",
        "image_path":       "ressources/giga_wolf.png",
        "base_stats": {
            "F0i":          1000,
            "V0i":          16,
            "F0c_ratio":    0.25,
            "V0c_ratio":    0.25,
            "Tau":          40,
            "mass":         20,
            "k":            0.4,
            "Ff":           100,
            "slopeOpt":     math.atan(0.15),
            "Fbrake_ratio": 0.5
        } 
    }
]

def create_animal_from_data(data):
    """
    Créer la structure qui contient les data des animaux.
    """
    pre_stats = data["base_stats"].copy()
    stats = {}
    stats["F0i"]        = pre_stats["F0i"]                                      # Newton
    stats["V0i"]        = pre_stats["V0i"]                                      # m.s
    stats["F0c"]        = pre_stats["F0i"] * pre_stats["F0c_ratio"]             # Newton
    stats["V0c"]        = pre_stats["V0i"] * pre_stats["V0c_ratio"]             # m.s
    stats["Tau"]        = pre_stats["Tau"]                                      # seconde
    stats["WacMax"]     = pre_stats["Tau"] * (pre_stats["V0i"] - stats["V0c"])  # seconde
    stats["mass"]       = pre_stats["mass"]                                     # kg
    stats["k"]          = pre_stats["k"]                                        # coef
    stats["Ff"]         = pre_stats["Ff"]                                       # Newton
    stats["slopeOpt"]   = pre_stats["slopeOpt"]                                 # radian
    stats["Fbrake"]     = pre_stats["F0i"] * pre_stats["Fbrake_ratio"]          # Newton
            
    return {
        "name": data["name"],
        "image_path": data["image_path"],
        "stats": stats
    }

ANIMALS = [create_animal_from_data(data) for data in ANIMALS_DATA]