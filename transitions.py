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
#   -> Manages round transitions

import pygame
import settings
from ui import ANIMAL_IMAGES, load_animal_images

def _get_menu_panel_rects(screen, game_settings):
    """
    Calcule les rectangles des panneaux de joueurs tels qu'ils sont affichés dans le menu.
    Cette fonction reproduit la logique de positionnement de ui.py pour que l'animation
    commence à la bonne position.
    """
    screen_w, screen_h = screen.get_size()

    # --- Constantes approximées de ui.py ---
    # Ces valeurs sont basées sur le rendu des polices dans le menu pour trouver le point de départ en Y.
    title_top_margin = 10
    title_font_height = 74
    title_bottom_margin = 15
    role_title_font_height = 48
    role_title_bottom_margin = 15
    
    start_y = (title_top_margin + title_font_height + title_bottom_margin + 
               role_title_font_height + role_title_bottom_margin)

    panel_width = screen_w * 0.45
    panel_height = screen_h * 0.20
    v_spacing = 5

    pred_x = screen_w * 0.25 - panel_width / 2
    prey_x = screen_w * 0.75 - panel_width / 2

    rects = {}
    for player_id in range(1, 5):
        status = game_settings.get(f'p{player_id}_status', "INACTIVE")
        if status == "INACTIVE":
            continue
        
        y_pos = start_y + (player_id - 1) * (panel_height + v_spacing)
        
        role = game_settings.get(f'p{player_id}_role', 'prey')
        x_pos = pred_x if role == 'predator' else prey_x
        
        rects[player_id] = pygame.Rect(x_pos, y_pos, panel_width, panel_height)
        
    return rects


def play_start_transition(screen, clock, players, map_renderer, map_rotation_angle, game_settings):
    """
    Joue l'animation de départ.
    """
    load_animal_images()
    duration = 3.0
    start_time = pygame.time.get_ticks()

    panel_rects = _get_menu_panel_rects(screen, game_settings)
    player_animations = []

    for player in players:
        panel_rect = panel_rects.get(player.id)
        
        start_pos = pygame.Vector2(0,0)
        initial_size = 100 # Taille par défaut

        if panel_rect:
            # Le point de départ est le centre de la zone d'aperçu de l'animal dans le panneau du menu
            top_rect_h = panel_rect.height * 0.25
            bottom_rect_h = panel_rect.height * 0.75
            bottom_rect_top = panel_rect.top + top_rect_h
            preview_rect_w = panel_rect.width * 0.33
            preview_rect_left = panel_rect.left

            start_pos = pygame.Vector2(
                preview_rect_left + preview_rect_w / 2,
                bottom_rect_top + bottom_rect_h / 2
            )

            # Calcule la taille initiale de l'image pour qu'elle corresponde à celle du menu
            preview_area_h = panel_rect.height * 0.75 * 0.7
            preview_area_w = panel_rect.width * 0.33 * 0.9
            initial_size = int(min(preview_area_w, preview_area_h))
        else:
            # Fallback si le panneau n'est pas trouvé (ne devrait pas arriver)
            start_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

        player_z = (map_renderer.get_z(player.x, player.y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
        end_pos_tuple = map_renderer._project_isometric(player.x, player.y, player_z, map_rotation_angle)
        end_pos = pygame.Vector2(end_pos_tuple)

        animal_name = player.animal['name']
        image = ANIMAL_IMAGES.get(animal_name, {}).get('source')
        if not image: continue

        player_animations.append({
            'player': player,
            'image': image,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'initial_size': initial_size
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

            current_size = int(anim['initial_size'] * (1 - eased_progress))
            
            if current_size > 1:
                scaled_image = pygame.transform.scale(anim['image'], (current_size, current_size))
                alpha = int(255 * (1 - progress))
                scaled_image.set_alpha(alpha)
                img_rect = scaled_image.get_rect(center=current_pos)
                screen.blit(scaled_image, img_rect)

            dot_alpha = int(255 * progress)
            dot_surface = pygame.Surface((settings.POINT_SCALE * 2, settings.POINT_SCALE * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, (*anim['player'].color, dot_alpha), (settings.POINT_SCALE, settings.POINT_SCALE), settings.POINT_SCALE)
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
    Joue l'animation entre les manches.
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
        eased_progress = progress * progress * (3 - 2 * progress)

        screen.fill(settings.BLACK)
        map_renderer.draw_map(map_rotation_angle, map_renderer.game_settings)

        for anim in player_animations:
            current_pos = anim['start_pos'].lerp(anim['end_pos'], eased_progress)
            pygame.draw.circle(screen, anim['player'].color, current_pos, settings.POINT_SCALE)

        pygame.display.flip()
        clock.tick(settings.FPS)

        if progress >= 1.0:
            running = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
