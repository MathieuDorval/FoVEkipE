#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    ______   ______     ______     __   __     ______     __     ______   __     ______     __   __     ______    
#   /\__  _\ /\  == \   /\  __ \   /\ "-.\ \   /\  ___\   /\ \   /\__  _\ /\ \   /\  __ \   /\ "-.\ \   /\  ___\   
#   \/_/\ \/ \ \  __<   \ \  __ \  \ \ \-.  \  \ \___  \  \ \ \  \/_/\ \/ \ \ \  \ \ \/\ \  \ \ \-.  \  \ \___  \  
#      \ \_\  \ \_\ \_\  \ \_\ \_\  \ \_\\"\_\  \/\_____\  \ \_\    \ \_\  \ \_\  \ \_____\  \ \_\\"\_\  \/\_____\ 
#       \/_/   \/_/ /_/   \/_/\/_/   \/_/ \/_/   \/_____/   \/_/     \/_/   \/_/   \/_____/   \/_/ \/_/   \/_____/
#   (version 24/09)
#   -> Manages game transitions

import pygame
import settings
from ui import ANIMAL_IMAGES, load_animal_images

def get_player_panel_rects(screen):
    """
    Calcule les positions des pannels joueurs, en miroir de ui.
    """
    screen_w, screen_h = screen.get_size()
    panel_width = screen_w * 0.20
    panel_height = screen_h * 0.40
    margin_x = screen_w * 0.05
    margin_y = screen_h * 0.05
    return [
        pygame.Rect(margin_x, margin_y, panel_width, panel_height), # P1
        pygame.Rect(screen_w - panel_width - margin_x, margin_y, panel_width, panel_height), # P2
        pygame.Rect(margin_x, screen_h - panel_height - margin_y, panel_width, panel_height), # P3
        pygame.Rect(screen_w - panel_width - margin_x, screen_h - panel_height - margin_y, panel_width, panel_height) # P4
    ]

def play_start_transition(screen, clock, players, map_renderer, map_rotation_angle):
    """
    Joue l'animation de départ de 3 secondes pour tous les joueurs.
    L'image du personnage sélectionné se déplace de son pannel vers sa position de départ
    sur la carte, tout en se transformant en un point de couleur.
    """
    load_animal_images()
    duration = 3.0
    start_time = pygame.time.get_ticks()

    panel_rects = get_player_panel_rects(screen)
    player_animations = []

    for player in players:
        panel_rect = panel_rects[player.id - 1]
        section_player_height = panel_rect.height * 0.15
        section_role_height = panel_rect.height * 0.15
        char_preview_top = panel_rect.top + section_player_height + section_role_height
        char_preview_height = panel_rect.height * 0.70 * (25 / 90)
        start_pos_center_x = panel_rect.centerx
        start_pos_center_y = char_preview_top + char_preview_height / 2
        start_pos = pygame.Vector2(start_pos_center_x, start_pos_center_y)

        player_z = (map_renderer.get_z(player.x, player.y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
        end_pos_tuple = map_renderer._project_isometric(player.x, player.y, player_z, map_rotation_angle)
        end_pos = pygame.Vector2(end_pos_tuple)

        animal_name = player.animal['name']
        image = ANIMAL_IMAGES.get(animal_name, {}).get('large')
        if not image: continue

        player_animations.append({
            'player': player,
            'image': image,
            'start_pos': start_pos,
            'end_pos': end_pos
        })

    running = True
    while running:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
        progress = min(elapsed_time / duration, 1.0)
        eased_progress = progress * progress * (3 - 2 * progress)

        screen.fill(settings.BLACK)
        map_renderer.draw_map(map_rotation_angle, map_renderer.game_settings)

        for anim in player_animations:
            current_pos = anim['start_pos'].lerp(anim['end_pos'], eased_progress)

            initial_size = anim['image'].get_width()
            current_size = int(initial_size * (1 - eased_progress))
            
            if current_size > 1:
                scaled_image = pygame.transform.scale(anim['image'], (current_size, current_size))
                alpha = int(255 * (1 - progress))
                scaled_image.set_alpha(alpha)
                img_rect = scaled_image.get_rect(center=current_pos)
                screen.blit(scaled_image, img_rect)

            dot_alpha = int(255 * progress)
            dot_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, (*anim['player'].color, dot_alpha), (5, 5), 5)
            dot_rect = dot_surface.get_rect(center=current_pos)
            screen.blit(dot_surface, dot_rect)

        pygame.display.flip()
        clock.tick(settings.FPS)

        if progress >= 1.0:
            running = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def play_round_reset_transition(screen, clock, players, map_renderer, map_rotation_angle, last_screen_positions, new_screen_positions):
    """
    Joue l'animation de réinitialisation entre les manches.
    Le point du joueur se déplace de sa dernière position (dans la killcam) vers sa nouvelle position.
    """
    duration = 2.0
    start_time = pygame.time.get_ticks()

    player_animations = []
    
    player_map = {p.id: p for p in players}

    for player_id, start_pos_tuple in last_screen_positions.items():
        if not start_pos_tuple: continue

        start_pos = pygame.Vector2(start_pos_tuple)

        end_pos_tuple = new_screen_positions.get(player_id)
        if not end_pos_tuple: continue
        
        end_pos = pygame.Vector2(end_pos_tuple)

        current_player = player_map.get(player_id)
        if not current_player: continue

        player_animations.append({
            'player': current_player,
            'start_pos': start_pos,
            'end_pos': end_pos,
        })

    running = True
    while running:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
        progress = min(elapsed_time / duration, 1.0)
        eased_progress = progress * progress * (3 - 2 * progress) # ease-in-out

        screen.fill(settings.BLACK)
        map_renderer.draw_map(map_rotation_angle, map_renderer.game_settings)

        for anim in player_animations:
            current_pos = anim['start_pos'].lerp(anim['end_pos'], eased_progress)
            pygame.draw.circle(screen, anim['player'].color, current_pos, 5)

        pygame.display.flip()
        clock.tick(settings.FPS)

        if progress >= 1.0:
            running = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()