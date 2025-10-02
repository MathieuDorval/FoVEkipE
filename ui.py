#    ______   ______     __   __   ______     __  __     __     ______   ______    
#   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \/ /    /\ \   /\  == \ /\  ___\   
#   \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \  _"-.  \ \ \  \ \  _-/ \ \  __\   
#    \ \_\    \ \_____\  \ \__|    \ \_____\  \ \_\ \_\  \ \_\  \ \_\    \ \_____\ 
#     \/_/     \/_____/   \/_/      \/_____/   \/_/\/_/   \/_/   \/_/     \/_____/ 
#    __  __     __    
#   /\ \/\ \   /\ \   
#   \ \ \_\ \  \ \ \  
#    \ \_____\  \ \_\ 
#     \/_____/   \/_/
#   (version 14/09)
#   -> Manages the on-screen display

import pygame
import settings
from animals import ANIMALS
from commands import get_confirm_action
import math

ANIMAL_IMAGES = {}

def load_animal_images():
    """
    Charge et met en cache les images des animaux pour éviter de les recharger à chaque frame.
    """
    if ANIMAL_IMAGES:
        return

    for animal in ANIMALS:
        try:
            img = pygame.image.load(animal['image_path']).convert_alpha()
            ANIMAL_IMAGES[animal['name']] = {
                'source': img, # Garde l'image originale pour un redimensionnement de qualité
                'small': pygame.transform.scale(img, (50, 50))
            }
        except pygame.error as e:
            print(f"Warning: Could not load image for {animal['name']}: {e}")
            source_placeholder = pygame.Surface((100, 100), pygame.SRCALPHA); source_placeholder.fill((50, 50, 50))
            small_placeholder = pygame.Surface((50, 50), pygame.SRCALPHA); small_placeholder.fill((50, 50, 50))
            ANIMAL_IMAGES[animal['name']] = {'source': source_placeholder, 'small': small_placeholder}

def draw_game_info(screen, scores, round_time, players, round_duration):
    load_animal_images()
    font_score = pygame.font.Font(None, 42)
    font_timer = pygame.font.Font(None, 50)
    
    # --- Timer ---
    time_left = max(0, round_duration - round_time)
    timer_text = font_timer.render(f"{time_left:.1f}", True, settings.WHITE)
    timer_rect = timer_text.get_rect(midtop=(screen.get_width() // 2, 15))
    screen.blit(timer_text, timer_rect)

    # --- Scores ---
    predators = sorted([p for p in players if p.role == 'predator'], key=lambda p: p.id)
    preys = sorted([p for p in players if p.role == 'prey'], key=lambda p: p.id)
    
    predator_score = scores.get(predators[0].id, 0) if predators else 0
    prey_score = scores.get(preys[0].id, 0) if preys else 0

    pred_label = "PREDATORS" if len(predators) > 1 else "PREDATOR"
    prey_label = "PREYS" if len(preys) > 1 else "PREY"

    pred_text_str = f"{pred_label}: {predator_score}"
    prey_text_str = f"{prey_label}: {prey_score}"

    pred_text = font_score.render(pred_text_str, True, settings.COLOR_PREDATOR)
    prey_text = font_score.render(prey_text_str, True, settings.COLOR_PREY)

    pred_rect = pred_text.get_rect(topright=(timer_rect.left - 50, 20))
    prey_rect = prey_text.get_rect(topleft=(timer_rect.right + 50, 20))

    screen.blit(pred_text, pred_rect)
    screen.blit(prey_text, prey_rect)

    # --- Wac & Player Images ---
    bar_width = 150
    bar_height = 15
    bar_spacing = 5
    img_size = 40
    img_padding = 10

    y_offset_pred = pred_rect.bottom + bar_spacing
    for predator in predators:
        if predator.is_active:
            animal_name = predator.animal['name']
            if animal_name in ANIMAL_IMAGES:
                img = pygame.transform.scale(ANIMAL_IMAGES[animal_name]['small'], (img_size, img_size))
                img_y_pos = y_offset_pred + (bar_height - img.get_height()) / 2
                screen.blit(img, (pred_rect.right - bar_width - img.get_width() - img_padding, img_y_pos))
            
            wac_ratio = predator.Wac / predator.stats['WacMax'] if predator.stats.get('WacMax', 0) > 0 else 0
            wac_ratio = min(1.0, max(0.0, wac_ratio))
            
            bar_y = y_offset_pred
            bar_x = pred_rect.right - bar_width
            
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            remaining_wac_width = bar_width * (1 - wac_ratio)
            pygame.draw.rect(screen, predator.color, (bar_x, bar_y, remaining_wac_width, bar_height))
            pygame.draw.rect(screen, settings.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            y_offset_pred += bar_height + bar_spacing

    y_offset_prey = prey_rect.bottom + bar_spacing
    for prey in preys:
        if prey.is_active:
            animal_name = prey.animal['name']
            if animal_name in ANIMAL_IMAGES:
                img = pygame.transform.scale(ANIMAL_IMAGES[animal_name]['small'], (img_size, img_size))
                img_y_pos = y_offset_prey + (bar_height - img.get_height())/2
                screen.blit(img, (prey_rect.left + bar_width + img_padding, img_y_pos))

            wac_ratio = prey.Wac / prey.stats['WacMax'] if prey.stats.get('WacMax', 0) > 0 else 0
            wac_ratio = min(1.0, max(0.0, wac_ratio))

            bar_y = y_offset_prey
            bar_x = prey_rect.left
            
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            remaining_wac_width = bar_width * (1 - wac_ratio)
            pygame.draw.rect(screen, prey.color, (bar_x, bar_y, remaining_wac_width, bar_height))
            pygame.draw.rect(screen, settings.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            y_offset_prey += bar_height + bar_spacing


def draw_player_panel(screen, player_id, base_rect, game_settings, is_ready, focus_level, cursor_pos):
    font_large = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    
    status = game_settings.get(f'p{player_id}_status', "INACTIVE")
    role = game_settings.get(f'p{player_id}_role', 'prey')
    player_colors = settings.PLAYER_COLORS[player_id]
    border_color = player_colors[role]
    
    bg_color = (*border_color, 100) # Teinte sombre de la couleur du joueur avec transparence
    
    # Create a temporary surface for transparency
    panel_surface = pygame.Surface(base_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, bg_color, panel_surface.get_rect(), border_radius=10)
    screen.blit(panel_surface, base_rect.topleft)
    pygame.draw.rect(screen, border_color, base_rect, width=2, border_radius=10)


    top_rect = pygame.Rect(base_rect.left, base_rect.top, base_rect.width, base_rect.height * 0.25)
    bottom_rect = pygame.Rect(base_rect.left, top_rect.bottom, base_rect.width, base_rect.height * 0.75)
    preview_rect = pygame.Rect(bottom_rect.left, bottom_rect.top, bottom_rect.width * 0.33, bottom_rect.height)
    grid_rect = pygame.Rect(preview_rect.right, bottom_rect.top, bottom_rect.width * 0.67, bottom_rect.height)

    title_str = f"Player {player_id}"
    if status == "AI": title_str += " (AI)"
    title_surf = font_large.render(title_str, True, settings.WHITE)
    title_pos = title_surf.get_rect(center=top_rect.center)
    screen.blit(title_surf, title_pos)

    # --- Highlight focus area ---
    is_human_player = status == "PLAYER"
    if not (is_human_player and is_ready):
        highlight_rect = top_rect if focus_level == 0 else bottom_rect
        highlight_surf = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 40))
        screen.blit(highlight_surf, highlight_rect.topleft)

    confirmed_animal_idx = game_settings.get(f'p{player_id}_animal_index', 0)
    preview_animal_idx = cursor_pos
    preview_animal = ANIMALS[preview_animal_idx]
    
    if preview_animal['name'] in ANIMAL_IMAGES:
        image_area_h = preview_rect.height * 0.7
        preview_img_size = int(min(preview_rect.width * 0.9, image_area_h))
        
        font_size = int(preview_rect.height * 0.15); font_size = max(12, min(font_size, 30))
        font_animal_name = pygame.font.Font(None, font_size)

        source_img = ANIMAL_IMAGES[preview_animal['name']]['source']
        scaled_preview_img = pygame.transform.scale(source_img, (preview_img_size, preview_img_size))
        name_surf = font_animal_name.render(preview_animal['name'], True, settings.WHITE)
        
        total_h = scaled_preview_img.get_height() + 5 + name_surf.get_height()
        start_y = preview_rect.centery - total_h / 2
        img_rect = scaled_preview_img.get_rect(centerx=preview_rect.centerx, top=start_y)
        screen.blit(scaled_preview_img, img_rect)
        name_rect = name_surf.get_rect(centerx=preview_rect.centerx, top=img_rect.bottom + 5)
        screen.blit(name_surf, name_rect)

    # --- Animal Grid ---
    num_rows = 2
    icons_per_row = math.ceil(len(ANIMALS) / num_rows)
    cell_w = grid_rect.width / icons_per_row
    cell_h = grid_rect.height / num_rows
    icon_size = int(min(cell_w, cell_h) * 0.9)

    if icon_size > 0:
        total_grid_w = icons_per_row * cell_w; total_grid_h = num_rows * cell_h
        grid_start_x = grid_rect.centerx - total_grid_w / 2
        grid_start_y = grid_rect.centery - total_grid_h / 2

        for i, animal in enumerate(ANIMALS):
            row, col = i // icons_per_row, i % icons_per_row
            cell_x, cell_y = grid_start_x + col * cell_w, grid_start_y + row * cell_h
            icon_rect = pygame.Rect(0, 0, icon_size, icon_size)
            icon_rect.center = (cell_x + cell_w / 2, cell_y + cell_h / 2)
            
            if animal['name'] in ANIMAL_IMAGES:
                source_icon = ANIMAL_IMAGES[animal['name']]['source']
                scaled_icon = pygame.transform.scale(source_icon, (icon_size, icon_size))
                screen.blit(scaled_icon, icon_rect.topleft)
            
            # Draw confirmed animal border for everyone
            if i == confirmed_animal_idx:
                pygame.draw.rect(screen, border_color, icon_rect, 2)
            
            # Draw cursor for players who are not locked in
            if not (is_human_player and is_ready):
                if focus_level == 1 and i == cursor_pos:
                    pygame.draw.rect(screen, settings.WHITE, icon_rect, 2)

    if is_human_player and is_ready:
        overlay = pygame.Surface(base_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, base_rect.topleft)
        font_ready = pygame.font.Font(None, 60)
        text_surf = font_ready.render("READY", True, (100, 255, 100))
        text_rect = text_surf.get_rect(center=base_rect.center)
        screen.blit(text_surf, text_rect)


def draw_menu(screen, game_settings, p_ready, player_focus, player_cursors, role_error_message=""):
    load_animal_images()
    font_large = pygame.font.Font(None, 74)
    font_role_title = pygame.font.Font(None, 48)

    title_text = font_large.render("FoVEkipE", True, settings.WHITE)
    title_rect = title_text.get_rect(midtop=(screen.get_width() // 2, 10))
    screen.blit(title_text, title_rect)

    predator_title = font_role_title.render("PREDATORS", True, settings.COLOR_PREDATOR)
    prey_title = font_role_title.render("PREYS", True, settings.COLOR_PREY)
    pred_title_rect = predator_title.get_rect(centerx=screen.get_width() * 0.25, y=title_rect.bottom + 15)
    prey_title_rect = prey_title.get_rect(centerx=screen.get_width() * 0.75, y=title_rect.bottom + 15)
    screen.blit(predator_title, pred_title_rect)
    screen.blit(prey_title, prey_title_rect)

    screen_w, screen_h = screen.get_size()
    panel_width = screen_w * 0.45
    panel_height = screen_h * 0.20
    v_spacing = 5
    start_y = pred_title_rect.bottom + 15
    pred_x = screen_w * 0.25 - panel_width / 2
    prey_x = screen_w * 0.75 - panel_width / 2
    
    for player_id in range(1, 5):
        if game_settings.get(f'p{player_id}_status', "INACTIVE") == "INACTIVE": continue
        y_pos = start_y + (player_id - 1) * (panel_height + v_spacing)
        role = game_settings.get(f'p{player_id}_role', 'prey')
        x_pos = pred_x if role == 'predator' else prey_x
        panel_rect = pygame.Rect(x_pos, y_pos, panel_width, panel_height)
        draw_player_panel(screen, player_id, panel_rect, game_settings, p_ready.get(player_id, False), player_focus.get(player_id), player_cursors.get(player_id))

    if role_error_message:
        font_error = pygame.font.Font(None, 40)
        error_text = font_error.render(role_error_message, True, (255, 80, 80))
        bg_rect = error_text.get_rect(center=(screen.get_width()//2, screen.get_height() - 50)).inflate(20, 10)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((0, 0, 0, 180))
        screen.blit(bg_surf, bg_rect)
        screen.blit(error_text, error_text.get_rect(center=bg_rect.center))

def draw_settings_menu(screen, game_settings, selected_index, option_keys):
    font_title = pygame.font.Font(None, 50)
    font_option = pygame.font.Font(None, 36)
    
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    title_text = font_title.render("Game Settings", True, settings.WHITE)
    title_rect = title_text.get_rect(centerx=screen.get_width() // 2, y=50)
    screen.blit(title_text, title_rect)
    
    options = {
        "Round Duration": f"{game_settings.get('round_duration', 30)}s",
        "Winning Score": f"{game_settings.get('winning_score', 3)}",
        "Map Width": f"{game_settings.get('map_width', 15)}m",
        "Slope Correction": "On" if game_settings.get('slope_correction') else "Off",
        "Brake Correction": "On" if game_settings.get('brake_correction') else "Off",
        "AI": "On" if game_settings.get('ai_enabled') else "Off",
        "Quit Game": ""
    }
    
    for i, key in enumerate(option_keys):
        value = options.get(key, '')
        if key == "Quit Game":
            option_text = key
        else:
            option_text = f"{key}: {value}"
            
        color = (255, 255, 100) if i == selected_index else settings.WHITE
        if key == "Quit Game":
            color = (255, 100, 100) if i == selected_index else (200, 50, 50)
            
        text_surf = font_option.render(option_text, True, color)
        text_rect = text_surf.get_rect(centerx=screen.get_width() // 2, y=150 + i * 60)
        screen.blit(text_surf, text_rect)
        
    help_text = font_option.render("Press Select to close", True, (150, 150, 150))
    help_rect = help_text.get_rect(centerx=screen.get_width() // 2, bottom=screen.get_height() - 40)
    screen.blit(help_text, help_rect)

def draw_game_over_screen(screen, clock, gamepads, players, scores, game_settings):
    font_winner = pygame.font.Font(None, 100)
    font_score = pygame.font.Font(None, 60)
    font_prompt = pygame.font.Font(None, 40)

    predators = [p for p in players if p.role == 'predator']
    preys = [p for p in players if p.role == 'prey']
    
    predators_final_score = scores.get(predators[0].id, 0) if predators else 0
    preys_final_score = scores.get(preys[0].id, 0) if preys else 0
    winning_score = game_settings.get('winning_score', 3)

    winner_text_str = "EQUALITY"
    winner_color = settings.WHITE
    if predators_final_score >= winning_score:
        winner_text_str = "PREDATORS WIN!" if len(predators) > 1 else "PREDATOR WINS!"
        winner_color = settings.COLOR_PREDATOR
    elif preys_final_score >= winning_score:
        winner_text_str = "PREYS WIN!" if len(preys) > 1 else "PREY WINS!"
        winner_color = (settings.COLOR_PREY)

    winner_text = font_winner.render(winner_text_str, True, winner_color)
    score_text_str = f"Predators : {predators_final_score}   |   Preys : {preys_final_score}"
    score_text = font_score.render(score_text_str, True, settings.WHITE)
    
    prompt_string = "Press SPACE to return to the menu" if not gamepads else "Press RT or LT to return to the menu"
    prompt_text = font_prompt.render(prompt_string, True, (200, 200, 200))

    winner_rect = winner_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 60))

    last_confirm_press = True
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        confirm_pressed = get_confirm_action(gamepads)
        if confirm_pressed and not last_confirm_press:
            running = False
        last_confirm_press = confirm_pressed
        screen.fill(settings.BLACK)
        screen.blit(winner_text, winner_rect)
        screen.blit(score_text, score_rect)
        screen.blit(prompt_text, prompt_rect)
        pygame.display.flip()
        clock.tick(settings.FPS)


def draw_killcam_hud(screen, top_text, bottom_text, bottom_text_color):
    top_font = pygame.font.Font(None, 80)
    bottom_font = pygame.font.Font(None, 120)
    top_surf = top_font.render(top_text, True, settings.WHITE)
    top_rect = top_surf.get_rect(center=(screen.get_width() // 2, 60))
    screen.blit(top_surf, top_rect)
    bottom_surf = bottom_font.render(bottom_text, True, bottom_text_color)
    bottom_rect = bottom_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    bg_rect = bottom_rect.inflate(20, 20)
    bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surf.fill((0, 0, 0, 150))
    screen.blit(bg_surf, bg_rect)
    screen.blit(bottom_surf, bottom_rect)

