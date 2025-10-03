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
#   (version 03/10)
#   -> Manages round transitions

import pygame
import settings
from ui import ANIMAL_IMAGES, load_animal_images

def play_start_transition(screen, clock, players, map_renderer, map_rotation_angle, game_settings, panel_rects):
    """
    Joue l'animation de départ : les panneaux de joueurs volent du menu vers leur point de départ
    en se transformant en pion.
    """
    load_animal_images()
    duration = 3.0
    start_time = pygame.time.get_ticks()

    player_animations = []

    for player in players:
        start_rect = panel_rects.get(player.id)
        if not start_rect: continue

        player_z = (map_renderer.get_z(player.x, player.y) + settings.PLAYER_Z_OFFSET) * settings.Z_BOOST_FACTOR
        end_pos_tuple = map_renderer._project_isometric(player.x, player.y, player_z, map_rotation_angle)
        
        animal_name = player.animal['name']
        image = ANIMAL_IMAGES.get(animal_name, {}).get('source')
        if not image: continue

        # Calcul de la taille de l'image de l'animal dans le menu pour l'animation
        preview_area_h = start_rect.height * 0.75 * 0.7
        preview_area_w = start_rect.width * 0.33 * 0.9
        initial_image_size = int(min(preview_area_w, preview_area_h))

        player_animations.append({
            'player': player,
            'image': image,
            'start_rect': start_rect,
            'end_pos': pygame.Vector2(end_pos_tuple),
            'initial_image_size': initial_image_size
        })

    running = True
    while running:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
        progress = min(elapsed_time / duration, 1.0)
        eased_progress = progress * progress * (3 - 2 * progress) # ease-in-out

        screen.fill(settings.BLACK)
        map_renderer.draw_map(map_rotation_angle, map_renderer.game_settings)

        for anim in player_animations:
            start_pos = pygame.Vector2(anim['start_rect'].center)
            current_center = start_pos.lerp(anim['end_pos'], eased_progress)

            # --- Animer la "carte" du joueur ---
            if progress < 1.0:
                # La carte rétrécit et s'estompe
                current_width = int(anim['start_rect'].width * (1 - eased_progress))
                current_height = int(anim['start_rect'].height * (1 - eased_progress))
                
                if current_width > 1 and current_height > 1:
                    panel_rect = pygame.Rect(0, 0, current_width, current_height)
                    panel_rect.center = current_center
                    
                    # Crée une surface temporaire pour la carte pour gérer la transparence
                    panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
                    
                    # Dessine une version simplifiée de la carte
                    bg_color = (*anim['player'].color, int(100 * (1 - progress)))
                    border_color = (*anim['player'].color, int(255 * (1 - progress)))
                    pygame.draw.rect(panel_surf, bg_color, panel_surf.get_rect(), border_radius=10)
                    pygame.draw.rect(panel_surf, border_color, panel_surf.get_rect(), width=2, border_radius=10)
                    
                    screen.blit(panel_surf, panel_rect.topleft)

                    # L'image de l'animal rétrécit et s'estompe avec la carte
                    current_img_size = int(anim['initial_image_size'] * (1 - eased_progress))
                    if current_img_size > 1:
                        scaled_image = pygame.transform.scale(anim['image'], (current_img_size, current_img_size))
                        scaled_image.set_alpha(int(255 * (1 - progress)))
                        img_rect = scaled_image.get_rect(center=current_center)
                        screen.blit(scaled_image, img_rect)

            # --- Animer le pion du joueur ---
            # Le pion apparaît à la destination finale
            dot_alpha = int(255 * eased_progress)
            dot_surface = pygame.Surface((settings.POINT_SCALE * 2, settings.POINT_SCALE * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, (*anim['player'].color, dot_alpha), (settings.POINT_SCALE, settings.POINT_SCALE), settings.POINT_SCALE)
            dot_rect = dot_surface.get_rect(center=anim['end_pos'])
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
        end_pos_tuple = new_screen_positions.get(player_id)
        if not end_pos_tuple: continue
        current_player = player_map.get(player_id)
        if not current_player: continue

        player_animations.append({
            'player': current_player,
            'start_pos': pygame.Vector2(start_pos_tuple),
            'end_pos': pygame.Vector2(end_pos_tuple),
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