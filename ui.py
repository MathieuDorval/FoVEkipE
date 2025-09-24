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
                'large': pygame.transform.scale(img, (60, 60)),
                'small': pygame.transform.scale(img, (40, 40))
            }
        except pygame.error as e:
            print(f"Warning: Could not load image for {animal['name']}: {e}")
            large_placeholder = pygame.Surface((60, 60), pygame.SRCALPHA); large_placeholder.fill((50, 50, 50))
            small_placeholder = pygame.Surface((40, 40), pygame.SRCALPHA); small_placeholder.fill((50, 50, 50))
            ANIMAL_IMAGES[animal['name']] = {'large': large_placeholder, 'small': small_placeholder}

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
            # Animal Image
            animal_name = predator.animal['name']
            if animal_name in ANIMAL_IMAGES:
                img = ANIMAL_IMAGES[animal_name]['small']
                img_y_pos = y_offset_pred + (img_size - bar_height) / 2 - img_size / 2 # Centrer l'image verticalement
                screen.blit(img, (pred_rect.right - bar_width - img_size - img_padding, img_y_pos))
            
            # WAC Bar
            wac_ratio = predator.Wac / predator.stats['WacMax'] if predator.stats.get('WacMax', 0) > 0 else 0
            wac_ratio = min(1.0, max(0.0, wac_ratio))
            
            bar_y = y_offset_pred
            bar_x = pred_rect.right - bar_width
            
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            remaining_wac_width = bar_width * (1 - wac_ratio)
            pygame.draw.rect(screen, predator.color, (bar_x, bar_y, remaining_wac_width, bar_height))
            pygame.draw.rect(screen, settings.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            y_offset_pred += img_size + bar_spacing

    y_offset_prey = prey_rect.bottom + bar_spacing
    for prey in preys:
        if prey.is_active:
            # Animal Image
            animal_name = prey.animal['name']
            if animal_name in ANIMAL_IMAGES:
                img = ANIMAL_IMAGES[animal_name]['small']
                img_y_pos = y_offset_prey + (img_size - bar_height) / 2 - img_size / 2 # Centrer l'image verticalement
                screen.blit(img, (prey_rect.left + bar_width + img_padding, img_y_pos))

            # WAC Bar
            wac_ratio = prey.Wac / prey.stats['WacMax'] if prey.stats.get('WacMax', 0) > 0 else 0
            wac_ratio = min(1.0, max(0.0, wac_ratio))

            bar_y = y_offset_prey
            bar_x = prey_rect.left
            
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            remaining_wac_width = bar_width * (1 - wac_ratio)
            pygame.draw.rect(screen, prey.color, (bar_x, bar_y, remaining_wac_width, bar_height))
            pygame.draw.rect(screen, settings.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            y_offset_prey += img_size + bar_spacing


def draw_player_panel(screen, player_id, base_rect, game_settings, is_ready, focused_item_index=None, cursor_pos_index=None):
    font_medium = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 22)
    font_tiny = pygame.font.Font(None, 20)
    ready_color = (100, 255, 100)
    highlight_color = (255, 255, 255, 40)
    cursor_highlight_color = (255, 255, 255)
    separator_color = (80, 80, 80)

    player_colors = [settings.COLOR_PLAYER1, settings.COLOR_PLAYER2, settings.COLOR_PLAYER3, settings.COLOR_PLAYER4]
    title_color = player_colors[player_id - 1]

    pygame.draw.rect(screen, (20, 20, 20), base_rect, border_radius=10)
    pygame.draw.rect(screen, separator_color, base_rect, width=1, border_radius=10)

    section_player_height = base_rect.height * 0.15
    section_role_height = base_rect.height * 0.15
    section_character_height = base_rect.height * 0.70

    section_player_rect = pygame.Rect(base_rect.left, base_rect.top, base_rect.width, section_player_height)
    section_role_rect = pygame.Rect(base_rect.left, section_player_rect.bottom, base_rect.width, section_role_height)
    section_character_rect = pygame.Rect(base_rect.left, section_role_rect.bottom, base_rect.width, section_character_height)

    # --- Section 1 : Statut du joueur ---
    status = game_settings.get(f'p{player_id}_status', "INACTIVE")
    title_str = f"Player {player_id} ({status})"
    title_surf = font_medium.render(title_str, True, title_color)
    title_rect = title_surf.get_rect(center=section_player_rect.center)
    if not is_ready and focused_item_index == 0:
        highlight_surf = pygame.Surface(section_player_rect.size, pygame.SRCALPHA); highlight_surf.fill(highlight_color)
        screen.blit(highlight_surf, section_player_rect.topleft)
    screen.blit(title_surf, title_rect)
    pygame.draw.line(screen, separator_color, section_player_rect.bottomleft, section_player_rect.bottomright, 1)

    # --- Section 2 : Rôle ---
    role = game_settings.get(f'p{player_id}_role', 'prey')
    role_color = settings.COLOR_PREDATOR if role == 'predator' else settings.COLOR_PREY
    role_str = "Predator" if role == 'predator' else "Prey"
    role_surf = font_small.render(role_str, True, role_color)
    role_rect = role_surf.get_rect(center=section_role_rect.center)
    if not is_ready and focused_item_index == 1:
        highlight_surf = pygame.Surface(section_role_rect.size, pygame.SRCALPHA); highlight_surf.fill(highlight_color)
        screen.blit(highlight_surf, section_role_rect.topleft)
    screen.blit(role_surf, role_rect)
    pygame.draw.line(screen, separator_color, section_role_rect.bottomleft, section_role_rect.bottomright, 1)

    # --- Section 3 : Personnage ---
    if not is_ready and focused_item_index == 2:
        highlight_surf = pygame.Surface(section_character_rect.size, pygame.SRCALPHA); highlight_surf.fill(highlight_color)
        screen.blit(highlight_surf, section_character_rect.topleft)
    
    # --- Sous-sections pour le personnage ---
    character_preview_height = section_character_height * (25 / 90)
    character_grid_height = section_character_height * (65 / 90)
    character_preview_rect = pygame.Rect(section_character_rect.left, section_character_rect.top, section_character_rect.width, character_preview_height)
    character_grid_rect = pygame.Rect(section_character_rect.left, character_preview_rect.bottom, section_character_rect.width, character_grid_height)
    
    confirmed_animal_idx = game_settings.get(f'p{player_id}_animal_index', 0)
    preview_animal_idx = cursor_pos_index if not is_ready and focused_item_index == 2 and cursor_pos_index is not None else confirmed_animal_idx
    preview_animal_name = ANIMALS[preview_animal_idx]['name']

    if preview_animal_name in ANIMAL_IMAGES:
        large_img = ANIMAL_IMAGES[preview_animal_name]['large']
        name_surf = font_tiny.render(preview_animal_name, True, settings.WHITE)
        total_height = large_img.get_height() + name_surf.get_height() + 2
        
        img_rect = large_img.get_rect(centerx=character_preview_rect.centerx)
        img_rect.centery = character_preview_rect.centery - (total_height - large_img.get_height()) / 2
        
        name_rect = name_surf.get_rect(centerx=character_preview_rect.centerx)
        name_rect.top = img_rect.bottom + 2
        
        screen.blit(large_img, img_rect)
        screen.blit(name_surf, name_rect)

    icon_size, padding = 40, 5
    icons_per_row = 5
    num_rows = (len(ANIMALS) - 1) // icons_per_row + 1
    
    grid_block_width = icons_per_row * (icon_size + padding) - padding
    grid_block_height = num_rows * (icon_size + padding) - padding
    
    grid_start_x = character_grid_rect.centerx - grid_block_width / 2
    grid_start_y = character_grid_rect.centery - grid_block_height / 2

    for i, animal in enumerate(ANIMALS):
        row, col = i // icons_per_row, i % icons_per_row
        pos_x = grid_start_x + col * (icon_size + padding)
        pos_y = grid_start_y + row * (icon_size + padding)
        icon_rect = pygame.Rect(pos_x, pos_y, icon_size, icon_size)
        
        if animal['name'] in ANIMAL_IMAGES:
            screen.blit(ANIMAL_IMAGES[animal['name']]['small'], icon_rect)
        
        if i == confirmed_animal_idx:
            pygame.draw.rect(screen, title_color, icon_rect, 2)
        
        if not is_ready and focused_item_index == 2 and i == cursor_pos_index:
            pygame.draw.rect(screen, cursor_highlight_color, icon_rect.inflate(2,2), 1)

    if is_ready and status != "AI":
        font_large_ready = pygame.font.Font(None, int(base_rect.height * 0.4))
        text_surf = font_large_ready.render("READY", True, ready_color)
        rotated_surf = pygame.transform.rotate(text_surf, 30); rotated_surf.set_alpha(100)
        rotated_rect = rotated_surf.get_rect(center=base_rect.center)
        screen.blit(rotated_surf, rotated_rect)


def draw_menu(screen, game_settings, p_ready, player_focus, player_cursors, role_error_message=""):
    load_animal_images()
    font_large = pygame.font.Font(None, 74)
    
    title_text = font_large.render("FoVEkipE", True, settings.WHITE)
    title_rect = title_text.get_rect(midtop=(screen.get_width() // 2, 20))
    screen.blit(title_text, title_rect)

    # --- Dimensions et positions des panneaux ---
    screen_w, screen_h = screen.get_size()
    panel_width = screen_w * 0.20
    panel_height = screen_h * 0.40
    margin_x = screen_w * 0.05
    margin_y = screen_h * 0.05

    positions = [
        pygame.Rect(margin_x, margin_y, panel_width, panel_height), # Haut-gauche
        pygame.Rect(screen_w - panel_width - margin_x, margin_y, panel_width, panel_height), # Haut-droite
        pygame.Rect(margin_x, screen_h - panel_height - margin_y, panel_width, panel_height), # Bas-gauche
        pygame.Rect(screen_w - panel_width - margin_x, screen_h - panel_height - margin_y, panel_width, panel_height) # Bas-droite
    ]
    
    max_players = 4 if pygame.joystick.get_count() >= 2 else 2

    for i in range(max_players):
        player_id = i + 1
        if game_settings.get(f'p{player_id}_status') == "INACTIVE": continue
            
        is_ready = p_ready.get(player_id, False)
        focused_item = player_focus.get(player_id)
        cursor_pos = player_cursors.get(player_id)
        draw_player_panel(screen, player_id, positions[i], game_settings, is_ready, focused_item, cursor_pos)

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
        "Round Duration": f"{game_settings['round_duration']}s",
        "Winning Score": f"{game_settings['winning_score']}",
        "Map Width": f"{game_settings['map_width']}m",
        "Slope Correction": "On" if game_settings.get('slope_correction') else "Off",
        "Brake Correction": "On" if game_settings.get('brake_correction') else "Off"
    }
    
    for i, key in enumerate(option_keys):
        option_text = f"{key}: {options.get(key, '')}"
        color = (255, 255, 100) if i == selected_index else settings.WHITE
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