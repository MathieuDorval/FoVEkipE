#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
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
        "base_stats": { "F0i": 500, "V0i": 16, "F0c_ratio": 0.25, "V0c_ratio": 0.25, "Tau": 40, "mass": 20, "k": 0.4, "Ff": 100, "slopeOpt": math.atan(0.05), "Fbrake_ratio": 0.1 }
    },
    {
        "name":             "Deer",
        "image_path":       "ressources/deer.png",
        "base_stats": { "F0i": 700, "V0i": 14, "F0c_ratio": 0.85, "V0c_ratio": 0.85, "Tau": 20, "mass": 20, "k": 0.4, "Ff": 200, "slopeOpt": math.atan(0.1), "Fbrake_ratio": 0.3 }
    },
    {
        "name":             "Giga Wolf",
        "image_path":       "ressources/giga_wolf.png",
        "base_stats": { "F0i": 1000, "V0i": 16, "F0c_ratio": 0.25, "V0c_ratio": 0.25, "Tau": 40, "mass": 20, "k": 0.4, "Ff": 100, "slopeOpt": math.atan(0.15), "Fbrake_ratio": 0.5 } 
    },
    {
        "name":             "Cheetah",
        "image_path":       "ressources/cheetah.png",
        "base_stats": { "F0i": 600, "V0i": 28, "F0c_ratio": 0.20, "V0c_ratio": 0.20, "Tau": 15, "mass": 18, "k": 0.35, "Ff": 90, "slopeOpt": math.atan(0.02), "Fbrake_ratio": 0.2 }
    },
    {
        "name":             "Bear",
        "image_path":       "ressources/bear.png",
        "base_stats": { "F0i": 1200, "V0i": 10, "F0c_ratio": 0.50, "V0c_ratio": 0.50, "Tau": 50, "mass": 45, "k": 0.6, "Ff": 250, "slopeOpt": math.atan(0.12), "Fbrake_ratio": 0.8 }
    },
    {
        "name":             "Rabbit",
        "image_path":       "ressources/rabbit.png",
        "base_stats": { "F0i": 200, "V0i": 18, "F0c_ratio": 0.90, "V0c_ratio": 0.90, "Tau": 10, "mass": 5, "k": 0.2, "Ff": 40, "slopeOpt": math.atan(0.08), "Fbrake_ratio": 0.4 }
    },
    {
        "name":             "Lion",
        "image_path":       "ressources/lion.png",
        "base_stats": { "F0i": 900, "V0i": 15, "F0c_ratio": 0.30, "V0c_ratio": 0.30, "Tau": 35, "mass": 30, "k": 0.5, "Ff": 150, "slopeOpt": math.atan(0.06), "Fbrake_ratio": 0.6 }
    },
    {
        "name":             "Gazelle",
        "image_path":       "ressources/gazelle.png",
        "base_stats": { "F0i": 550, "V0i": 22, "F0c_ratio": 0.80, "V0c_ratio": 0.80, "Tau": 25, "mass": 15, "k": 0.3, "Ff": 120, "slopeOpt": math.atan(0.04), "Fbrake_ratio": 0.25 }
    },
    {
        "name":             "Boar",
        "image_path":       "ressources/boar.png",
        "base_stats": { "F0i": 1100, "V0i": 12, "F0c_ratio": 0.60, "V0c_ratio": 0.60, "Tau": 30, "mass": 35, "k": 0.55, "Ff": 220, "slopeOpt": math.atan(0.10), "Fbrake_ratio": 0.9 }
    },
    {
        "name":             "Fox",
        "image_path":       "ressources/fox.png",
        "base_stats": { "F0i": 350, "V0i": 17, "F0c_ratio": 0.4, "V0c_ratio": 0.4, "Tau": 28, "mass": 8, "k": 0.25, "Ff": 70, "slopeOpt": math.atan(0.07), "Fbrake_ratio": 0.3 }
    },
    {
        "name":             "Bison",
        "image_path":       "ressources/bison.png",
        "base_stats": { "F0i": 1500, "V0i": 9, "F0c_ratio": 0.7, "V0c_ratio": 0.7, "Tau": 60, "mass": 60, "k": 0.7, "Ff": 300, "slopeOpt": math.atan(0.05), "Fbrake_ratio": 0.7 }
    },
    {
        "name":             "Horse",
        "image_path":       "ressources/horse.png",
        "base_stats": { "F0i": 800, "V0i": 19, "F0c_ratio": 0.75, "V0c_ratio": 0.75, "Tau": 55, "mass": 25, "k": 0.45, "Ff": 180, "slopeOpt": math.atan(0.03), "Fbrake_ratio": 0.3 }
    },
    {
        "name":             "Panther",
        "image_path":       "ressources/panther.png",
        "base_stats": { "F0i": 750, "V0i": 18, "F0c_ratio": 0.22, "V0c_ratio": 0.22, "Tau": 30, "mass": 22, "k": 0.4, "Ff": 130, "slopeOpt": math.atan(0.09), "Fbrake_ratio": 0.5 }
    },
    {
        "name":             "Goat",
        "image_path":       "ressources/goat.png",
        "base_stats": { "F0i": 400, "V0i": 13, "F0c_ratio": 0.6, "V0c_ratio": 0.6, "Tau": 35, "mass": 12, "k": 0.3, "Ff": 80, "slopeOpt": math.atan(0.25), "Fbrake_ratio": 0.6 }
    },
    {
        "name":             "Antelope",
        "image_path":       "ressources/antelope.png",
        "base_stats": { "F0i": 650, "V0i": 21, "F0c_ratio": 0.82, "V0c_ratio": 0.82, "Tau": 22, "mass": 16, "k": 0.32, "Ff": 110, "slopeOpt": math.atan(0.06), "Fbrake_ratio": 0.2 }
    }
]

def create_animal_from_data(data):
    """
    Create the data structure to hold the animal data.
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