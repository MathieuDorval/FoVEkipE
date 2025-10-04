#    ______     __  __     __   __     ______   ______     __   __   ______     __  __     ______     __  __     ______     __         __     ______   ______    
#   /\  == \   /\ \/\ \   /\ "-.\ \   /\  ___\ /\  __ \   /\ \ / /  /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\  == \   /\ \       /\ \   /\  ___\ /\  ___\   
#   \ \  __<   \ \ \_\ \  \ \ \-.  \  \ \  __\ \ \ \/\ \  \ \ \'/   \ \  __\   \ \____ \  \ \ \/\ \  \ \ \_\ \  \ \  __<   \ \ \____  \ \ \  \ \  __\ \ \  __\   
#    \ \_\ \_\  \ \_____\  \ \_\\"\_\  \ \_\    \ \_____\  \ \__|    \ \_____\  \/\_____\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\  \ \_\    \ \_____\ 
#     \/_/ /_/   \/_____/   \/_/ \/_/   \/_/     \/_____/   \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/   \/_/   \/_/     \/_____/
#    __  __     __    
#   /\ \/\ \   /\ \   
#   \ \ \_\ \  \ \ \  
#    \ \_____\  \ \_\ 
#     \/_____/   \/_/
#   (version 04/10)
#   → Manages the on-screen display

import pygame
import settings
from animals import ANIMALS
from commands import get_confirm_action
import math
from language import get_text
from renderer import draw_background

ANIMAL_IMAGES = {}

def load_animal_images():
    """
    Load and pre-cache the animal textures to prevent reloading them on each frame.
    """
    if ANIMAL_IMAGES:
        return

    # Load each animal image from its file path
    for animal in ANIMALS:
        try:
            img = pygame.image.load(animal['image_path']).convert_alpha()
            ANIMAL_IMAGES[animal['name']] = {
                'source': img,
                'small': pygame.transform.scale(img, (50, 50))
            }
        except pygame.error as e:
            # If an image fails to load, print a warning and use a placeholder
            print(f"Warning: Could not load image for {animal['name']}: {e}")
            source_placeholder = pygame.Surface((100, 100), pygame.SRCALPHA); source_placeholder.fill((50, 50, 50))
            small_placeholder = pygame.Surface((50, 50), pygame.SRCALPHA); small_placeholder.fill((50, 50, 50))
            ANIMAL_IMAGES[animal['name']] = {'source': source_placeholder, 'small': small_placeholder}

def draw_game_info(screen, scores, round_time, players, game_settings):
    """
    Show the game details (time, WAC, scores).
    """
    load_animal_images()
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Define layout zones for the top info bar
    info_bar_height = screen_height * 0.1
    left_zone_rect = pygame.Rect(0, 0, screen_width / 4, info_bar_height)
    center_zone_rect = pygame.Rect(left_zone_rect.right, 0, screen_width / 2, info_bar_height)
    right_zone_rect = pygame.Rect(center_zone_rect.right, 0, screen_width / 4, info_bar_height)

    round_duration = game_settings.get('round_duration', 30)
    winning_score = game_settings.get('winning_score', 3)

    # --- Draw Round Timer ---
    time_left = max(0, round_duration - round_time)
    time_ratio = time_left / round_duration if round_duration > 0 else 0
    bar_max_width = center_zone_rect.width * 0.8
    bar_height_time = info_bar_height * 0.2
    current_bar_width = bar_max_width * time_ratio
    
    # Draw timer background bar
    bg_bar_rect = pygame.Rect(
        center_zone_rect.centerx - bar_max_width / 2,
        center_zone_rect.top + info_bar_height * 0.15,
        bar_max_width,
        bar_height_time
    )
    pygame.draw.rect(screen, (40, 40, 40), bg_bar_rect)
    
    # Calculate the color gradient for the timer bar (green -> yellow -> red)
    elapsed_ratio = 1.0 - time_ratio
    if elapsed_ratio < 0.5:
        interp_ratio = elapsed_ratio * 2 
        r = settings.TIME_BAR_COLOR_START[0] * (1 - interp_ratio) + settings.TIME_BAR_COLOR_MIDDLE[0] * interp_ratio
        g = settings.TIME_BAR_COLOR_START[1] * (1 - interp_ratio) + settings.TIME_BAR_COLOR_MIDDLE[1] * interp_ratio
        b = settings.TIME_BAR_COLOR_START[2] * (1 - interp_ratio) + settings.TIME_BAR_COLOR_MIDDLE[2] * interp_ratio
    else:
        interp_ratio = (elapsed_ratio - 0.5) * 2
        r = settings.TIME_BAR_COLOR_MIDDLE[0] * (1 - interp_ratio) + settings.TIME_BAR_COLOR_END[0] * interp_ratio
        g = settings.TIME_BAR_COLOR_MIDDLE[1] * (1 - interp_ratio) + settings.TIME_BAR_COLOR_END[1] * interp_ratio
        b = settings.TIME_BAR_COLOR_MIDDLE[2] * (1 - interp_ratio) + settings.TIME_BAR_COLOR_END[2] * interp_ratio
    time_bar_color = (int(r), int(g), int(b))

    # Draw timer foreground bar (the part that shrinks)
    fg_bar_rect = pygame.Rect(
        center_zone_rect.centerx - current_bar_width / 2,
        bg_bar_rect.y,
        current_bar_width,
        bar_height_time
    )
    pygame.draw.rect(screen, time_bar_color, fg_bar_rect)
    pygame.draw.rect(screen, settings.WHITE, bg_bar_rect, 2) # Draw border

    # --- Draw Score Display ---
    predators = sorted([p for p in players if p.role == 'predator'], key=lambda p: p.id)
    preys = sorted([p for p in players if p.role == 'prey'], key=lambda p: p.id)
    predator_score = scores.get(predators[0].id, 0) if predators else 0
    prey_score = scores.get(preys[0].id, 0) if preys else 0

    score_y = bg_bar_rect.bottom + 25
    center_x = screen_width // 2
    num_side_circles = winning_score - 1
    victory_radius = 12
    score_radius = 10
    spacing = 8
    font_score_label = pygame.font.Font(None, 28)

    # Draw central victory circle
    if predator_score >= winning_score:
        pygame.draw.circle(screen, settings.COLOR_PREDATOR, (center_x, score_y), victory_radius)
    elif prey_score >= winning_score:
        pygame.draw.circle(screen, settings.COLOR_PREY, (center_x, score_y), victory_radius)
    else:
        pygame.draw.circle(screen, settings.WHITE, (center_x, score_y), victory_radius, 2)
    
    # Draw Predators score (left side)
    outermost_pred_circle_x = center_x - (victory_radius + spacing + score_radius + (num_side_circles - 1) * (score_radius * 2 + spacing))
    pred_text_surf = font_score_label.render(get_text('predators_label'), True, settings.COLOR_PREDATOR)
    pred_text_rect = pred_text_surf.get_rect(midright=(outermost_pred_circle_x - score_radius - spacing, score_y))
    screen.blit(pred_text_surf, pred_text_rect)

    # Draw predator score circles (filling from outside in)
    for i in range(num_side_circles):
        offset = victory_radius + spacing + score_radius + i * (score_radius * 2 + spacing)
        circle_x = center_x - offset
        if predator_score >= (num_side_circles - i):
            pygame.draw.circle(screen, settings.COLOR_PREDATOR, (circle_x, score_y), score_radius)
        else:
            pygame.draw.circle(screen, settings.COLOR_PREDATOR, (circle_x, score_y), score_radius, 2)

    # Draw Preys score (right side)
    outermost_prey_circle_x = center_x + (victory_radius + spacing + score_radius + (num_side_circles - 1) * (score_radius * 2 + spacing))
    prey_text_surf = font_score_label.render(get_text('preys_label'), True, settings.COLOR_PREY)
    prey_text_rect = prey_text_surf.get_rect(midleft=(outermost_prey_circle_x + score_radius + spacing, score_y))
    screen.blit(prey_text_surf, prey_text_rect)
    
    # Draw prey score circles (filling from outside in)
    for i in range(num_side_circles):
        offset = victory_radius + spacing + score_radius + i * (score_radius * 2 + spacing)
        circle_x = center_x + offset
        if prey_score >= (num_side_circles - i):
            pygame.draw.circle(screen, settings.COLOR_PREY, (circle_x, score_y), score_radius)
        else:
            pygame.draw.circle(screen, settings.COLOR_PREY, (circle_x, score_y), score_radius, 2)

    # --- Draw Player WAC Bars ---
    # This is a nested function to avoid code duplication for predators and preys
    def draw_wac_bars(player_list, zone_rect, align_right=False):
        if not player_list: return
        # Calculate dimensions for WAC bars based on number of players
        num_players = len(player_list)
        total_bar_area_height = zone_rect.height * 0.9
        single_item_height = total_bar_area_height / num_players
        bar_height = single_item_height * 0.7
        bar_spacing = single_item_height - bar_height
        img_size = int(bar_height * 1.2)
        img_padding = 8
        bar_width = zone_rect.width * 0.7 - img_size - img_padding
        total_block_height = num_players * (bar_height + bar_spacing) - bar_spacing
        start_y = zone_rect.centery - total_block_height / 2

        for i, player in enumerate(player_list):
            if not player.is_active: continue
            
            # Calculate WAC ratio
            wac_max = player.stats.get('WacMax', 1)
            wac_ratio = player.Wac / wac_max if wac_max > 0 else 0
            remaining_wac_ratio = 1.0 - min(1.0, max(0.0, wac_ratio))
            fg_wac_width = bar_width * remaining_wac_ratio
            bar_y = start_y + i * (bar_height + bar_spacing)
            img_y_pos = bar_y + (bar_height - img_size) / 2

            # Align left for predators, right for preys
            if align_right:
                img_x_pos = zone_rect.right - (zone_rect.width * 0.05) - img_size
                bar_x = img_x_pos - img_padding - bar_width
            else:
                img_x_pos = zone_rect.left + (zone_rect.width * 0.05)
                bar_x = img_x_pos + img_size + img_padding

            # Draw animal icon
            animal_name = player.animal['name']
            if animal_name in ANIMAL_IMAGES:
                img = pygame.transform.scale(ANIMAL_IMAGES[animal_name]['source'], (img_size, img_size))
                screen.blit(img, (img_x_pos, img_y_pos))
            
            # Draw WAC bar background and foreground
            wac_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(screen, (40, 40, 40), wac_bg_rect)

            if align_right:
                wac_fg_rect = pygame.Rect(wac_bg_rect.right - fg_wac_width, bar_y, fg_wac_width, bar_height)
            else:
                wac_fg_rect = pygame.Rect(bar_x, bar_y, fg_wac_width, bar_height)
            
            pygame.draw.rect(screen, player.color, wac_fg_rect)
            pygame.draw.rect(screen, settings.WHITE, wac_bg_rect, 1) # Border

    draw_wac_bars(predators, left_zone_rect, align_right=False)
    draw_wac_bars(preys, right_zone_rect, align_right=True)


def draw_player_panel(screen, player_id, base_rect, game_settings, is_ready, focus_level, cursor_pos, num_gamepads=0):
    font_large = pygame.font.Font(None, 32)
    
    # --- Draw Panel Background and Border ---
    status = game_settings.get(f'p{player_id}_status', "INACTIVE")
    role = game_settings.get(f'p{player_id}_role', 'prey')
    player_colors = settings.PLAYER_COLORS[player_id]
    border_color = player_colors[role]
    bg_color = (*border_color, 100) # Semi-transparent background
    
    panel_surface = pygame.Surface(base_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, bg_color, panel_surface.get_rect(), border_radius=10)
    screen.blit(panel_surface, base_rect.topleft)
    pygame.draw.rect(screen, border_color, base_rect, width=2, border_radius=10)

    # --- Draw Panel Header ---
    top_rect = pygame.Rect(base_rect.left, base_rect.top, base_rect.width, base_rect.height * 0.25)
    title_str = f"{get_text('player_label')} {player_id}"
    if status == "AI": title_str += f" ({get_text('ai_label')})"
    title_surf = font_large.render(title_str, True, settings.WHITE)
    title_pos = title_surf.get_rect(center=top_rect.center)
    screen.blit(title_surf, title_pos)

    # --- Draw Role Selection Arrows ---
    is_human_player = status == "PLAYER"
    if not (is_human_player and is_ready) and focus_level == 0:
        arrow_color = settings.WHITE
        arrow_size = title_surf.get_height() * 0.4
        arrow_padding = 10
        screen_width = screen.get_width()

        if base_rect.centerx > screen_width / 2: # Panel is on the right (prey)
            left_arrow_points = [
                (title_pos.left - arrow_padding - arrow_size, title_pos.centery),
                (title_pos.left - arrow_padding, title_pos.centery - arrow_size / 2),
                (title_pos.left - arrow_padding, title_pos.centery + arrow_size / 2)
            ]
            pygame.draw.polygon(screen, arrow_color, left_arrow_points)
        else: # Panel is on the left (predator)
            right_arrow_points = [
                (title_pos.right + arrow_padding + arrow_size, title_pos.centery),
                (title_pos.right + arrow_padding, title_pos.centery - arrow_size / 2),
                (title_pos.right + arrow_padding, title_pos.centery + arrow_size / 2)
            ]
            pygame.draw.polygon(screen, arrow_color, right_arrow_points)

    # --- Draw Focus Highlight ---
    if not (is_human_player and is_ready):
        highlight_rect = top_rect if focus_level == 0 else bottom_rect
        highlight_surf = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 40))
        screen.blit(highlight_surf, highlight_rect.topleft)

    # --- Draw Animal Preview ---
    bottom_rect = pygame.Rect(base_rect.left, top_rect.bottom, base_rect.width, base_rect.height * 0.75)
    preview_rect = pygame.Rect(bottom_rect.left, bottom_rect.top, bottom_rect.width * 0.33, bottom_rect.height)
    confirmed_animal_idx = game_settings.get(f'p{player_id}_animal_index', 0)
    preview_animal_idx = cursor_pos if focus_level == 1 and not (is_human_player and is_ready) else confirmed_animal_idx
    preview_animal = ANIMALS[preview_animal_idx]
    
    if preview_animal['name'] in ANIMAL_IMAGES:
        image_area_h = preview_rect.height * 0.7
        preview_img_size = int(min(preview_rect.width * 0.9, image_area_h))
        font_size = int(preview_rect.height * 0.15); font_size = max(12, min(font_size, 30))
        font_animal_name = pygame.font.Font(None, font_size)

        source_img = ANIMAL_IMAGES[preview_animal['name']]['source']
        scaled_preview_img = pygame.transform.scale(source_img, (preview_img_size, preview_img_size))
        translated_name = get_text(preview_animal['name'])
        name_surf = font_animal_name.render(translated_name, True, settings.WHITE)
        
        total_h = scaled_preview_img.get_height() + 5 + name_surf.get_height()
        start_y = preview_rect.centery - total_h / 2
        img_rect = scaled_preview_img.get_rect(centerx=preview_rect.centerx, top=start_y)
        screen.blit(scaled_preview_img, img_rect)
        name_rect = name_surf.get_rect(centerx=preview_rect.centerx, top=img_rect.bottom + 5)
        screen.blit(name_surf, name_rect)

    # --- Draw Animal Selection Grid ---
    grid_rect = pygame.Rect(preview_rect.right, bottom_rect.top, bottom_rect.width * 0.67, bottom_rect.height)
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
            
            is_hovered = not (is_human_player and is_ready) and focus_level == 1 and i == cursor_pos

            # Draw animal icon or confirm button prompt
            if is_hovered:
                confirm_button_text = "" # Determine prompt based on controller
                if num_gamepads == 0:
                    if player_id == 1: confirm_button_text = "SPACE"
                    elif player_id == 2: confirm_button_text = "ENT"
                elif num_gamepads == 1:
                    if player_id == 1: confirm_button_text = "LT"
                    elif player_id == 2: confirm_button_text = "RT"
                # ... (rest of controller logic)
                if confirm_button_text:
                    font_size_button = int(icon_size * 0.6) if len(confirm_button_text) <= 2 else int(icon_size * 0.4)
                    font_button_small = pygame.font.Font(None, font_size_button)
                    text_surf = font_button_small.render(confirm_button_text, True, settings.WHITE)
                    text_rect = text_surf.get_rect(center=icon_rect.center)
                    screen.blit(text_surf, text_rect)
                else: # Fallback if no button text is defined
                    if animal['name'] in ANIMAL_IMAGES:
                        source_icon = ANIMAL_IMAGES[animal['name']]['source']
                        scaled_icon = pygame.transform.scale(source_icon, (icon_size, icon_size))
                        screen.blit(scaled_icon, icon_rect.topleft)
            else:
                if animal['name'] in ANIMAL_IMAGES:
                    source_icon = ANIMAL_IMAGES[animal['name']]['source']
                    scaled_icon = pygame.transform.scale(source_icon, (icon_size, icon_size))
                    screen.blit(scaled_icon, icon_rect.topleft)
            
            # Draw borders for selected and hovered icons
            if i == confirmed_animal_idx:
                pygame.draw.rect(screen, border_color, icon_rect, 2)
            if is_hovered:
                pygame.draw.rect(screen, settings.WHITE, icon_rect, 2)

    # --- Draw "Ready" Overlay ---
    if is_human_player and is_ready:
        overlay = pygame.Surface(base_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, base_rect.topleft)
        font_ready = pygame.font.Font(None, 60)
        text_surf = font_ready.render(get_text('ready_label').upper(), True, (100, 255, 100))
        text_rect = text_surf.get_rect(center=base_rect.center)
        screen.blit(text_surf, text_rect)


def draw_menu(screen, game_settings, p_ready, player_focus, player_cursors, role_error_message="", num_gamepads=0):
    load_animal_images()
    font_large = pygame.font.Font(None, 74)
    font_role_title = pygame.font.Font(None, 48)

    # --- Draw Game Title ---
    title_text = font_large.render(get_text('game_name'), True, settings.WHITE)
    title_rect = title_text.get_rect(midtop=(screen.get_width() // 2, 10))
    screen.blit(title_text, title_rect)

    # --- Draw Team Titles (Predators/Preys) ---
    predator_title = font_role_title.render(get_text('predators_label').upper(), True, settings.COLOR_PREDATOR)
    prey_title = font_role_title.render(get_text('preys_label').upper(), True, settings.COLOR_PREY)
    pred_title_rect = predator_title.get_rect(centerx=screen.get_width() * 0.25, y=title_rect.bottom + 15)
    prey_title_rect = prey_title.get_rect(centerx=screen.get_width() * 0.75, y=title_rect.bottom + 15)
    screen.blit(predator_title, pred_title_rect)
    screen.blit(prey_title, prey_title_rect)

    # --- Draw Player Panels ---
    screen_w, screen_h = screen.get_size()
    panel_width = screen_w * 0.45
    panel_height = screen_h * 0.20
    v_spacing = 5
    start_y = pred_title_rect.bottom + 15
    pred_x = screen_w * 0.25 - panel_width / 2
    prey_x = screen_w * 0.75 - panel_width / 2
    
    panel_rects_to_return = {}
    for player_id in range(1, 5):
        if game_settings.get(f'p{player_id}_status', "INACTIVE") == "INACTIVE": continue
        role = game_settings.get(f'p{player_id}_role', 'prey')
        x_pos = pred_x if role == 'predator' else prey_x
        y_pos = start_y + (player_id - 1) * (panel_height + v_spacing) # Position depends on ID to stack them
        panel_rect = pygame.Rect(x_pos, y_pos, panel_width, panel_height)
        panel_rects_to_return[player_id] = panel_rect
        draw_player_panel(screen, player_id, panel_rect, game_settings, p_ready.get(player_id, False), player_focus.get(player_id), player_cursors.get(player_id), num_gamepads)

    # --- Draw Error Messages ---
    if role_error_message:
        font_error = pygame.font.Font(None, 40)
        error_text = font_error.render(role_error_message, True, (255, 80, 80))
        bg_rect = error_text.get_rect(center=(screen.get_width()//2, screen.get_height() - 50)).inflate(20, 10)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((0, 0, 0, 180))
        screen.blit(bg_surf, bg_rect)
        screen.blit(error_text, error_text.get_rect(center=bg_rect.center))

    # --- Draw "Press to Join" Prompts ---
    prompts = []
    font_prompt = pygame.font.Font(None, 28)
    prompt_color = (200, 200, 200)
    # This logic determines which join prompts to show based on connected gamepads
    if num_gamepads == 1:
        if game_settings.get('p1_status') == 'INACTIVE': prompts.append(get_text('p1_join_prompt'))
        if game_settings.get('p2_status') == 'INACTIVE': prompts.append(get_text('p2_join_prompt_1pad'))
    # ... (rest of gamepad prompt logic)
    
    if prompts:
        base_y = screen.get_height() - 30 - (len(prompts) - 1) * 30
        for i, text in enumerate(prompts):
            prompt_surf = font_prompt.render(text, True, prompt_color)
            prompt_rect = prompt_surf.get_rect(centerx=screen.get_width() / 2, y=base_y + i * 30)
            screen.blit(prompt_surf, prompt_rect)

    return panel_rects_to_return

def draw_settings_menu(screen, game_settings, selected_index, option_keys, key_map, num_gamepads):
    font_title = pygame.font.Font(None, 50)
    font_option = pygame.font.Font(None, 36)
    
    # Draw dark background
    draw_background(screen, dark=True)
    
    # Draw settings title
    title_text = font_title.render(get_text('settings_title'), True, settings.WHITE)
    title_rect = title_text.get_rect(centerx=screen.get_width() // 2, y=50)
    screen.blit(title_text, title_rect)
    
    # Dictionary of current setting values to display
    options_values = {
        "language": f"{'English' if game_settings.get('language') == 'en' else 'Français'}",
        "round_duration": f"{game_settings.get('round_duration', 30)}s",
        # ... (rest of settings values)
        "quit_game": ""
    }
    
    # Loop through and draw each setting option
    for i, key_label in enumerate(option_keys):
        key = key_map[key_label]
        value = options_values[key]
        text_label = get_text(key_label)
        
        option_text = f"{text_label}: {value}" if key != "quit_game" else text_label
            
        # Highlight the selected option
        color = (255, 255, 100) if i == selected_index else settings.WHITE
        if key == "vibration_mode" and num_gamepads < 2: color = (100, 100, 100) # Grey out if not available
        elif key == "quit_game": color = (255, 100, 100) if i == selected_index else (200, 50, 50)
            
        text_surf = font_option.render(option_text, True, color)
        text_rect = text_surf.get_rect(centerx=screen.get_width() // 2, y=150 + i * 50)
        screen.blit(text_surf, text_rect)
        
    # Draw help text at the bottom
    help_text = font_option.render(get_text('settings_close_prompt'), True, (150, 150, 150))
    help_rect = help_text.get_rect(centerx=screen.get_width() // 2, bottom=screen.get_height() - 40)
    screen.blit(help_text, help_rect)

def draw_game_over_screen(screen, clock, gamepads, players, scores, game_settings):
    font_winner = pygame.font.Font(None, 100)
    font_score = pygame.font.Font(None, 60)
    font_prompt = pygame.font.Font(None, 40)

    # Determine the winner
    predators = [p for p in players if p.role == 'predator']
    preys = [p for p in players if p.role == 'prey']
    predators_final_score = scores.get(predators[0].id, 0) if predators else 0
    preys_final_score = scores.get(preys[0].id, 0) if preys else 0
    winning_score = game_settings.get('winning_score', 3)

    winner_text_str = get_text('equality_label').upper()
    winner_color = settings.WHITE
    if predators_final_score >= winning_score:
        winner_text_str = get_text('predators_win_label').upper() if len(predators) > 1 else get_text('predator_wins_label').upper()
        winner_color = settings.COLOR_PREDATOR
    elif preys_final_score >= winning_score:
        winner_text_str = get_text('preys_win_label').upper() if len(preys) > 1 else get_text('prey_wins_label').upper()
        winner_color = (settings.COLOR_PREY)

    # Draw winner text, final score, and prompt to return to menu
    winner_text = font_winner.render(winner_text_str, True, winner_color)
    score_text_str = f"{get_text('predators_label')} : {predators_final_score}   |   {get_text('preys_label')} : {preys_final_score}"
    score_text = font_score.render(score_text_str, True, settings.WHITE)
    prompt_string = get_text('return_to_menu_prompt_keyboard') if not gamepads else get_text('return_to_menu_prompt_gamepad')
    prompt_text = font_prompt.render(prompt_string, True, (200, 200, 200))

    winner_rect = winner_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 60))

    # This loop keeps the game over screen visible until the player confirms
    running = True
    while running:
        # ... event handling ...
        draw_background(screen, dark=True)
        screen.blit(winner_text, winner_rect)
        screen.blit(score_text, score_rect)
        screen.blit(prompt_text, prompt_rect)
        pygame.display.flip()
        clock.tick(settings.FPS)

def draw_pause_menu(screen, selected_index):
    """
    Draws the pause menu over the screen.
    """
    font_title = pygame.font.Font(None, 70)
    font_option = pygame.font.Font(None, 50)
    
    # Draw a semi-transparent overlay to dim the game
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Draw pause menu title
    title_text = font_title.render(get_text('pause_title'), True, settings.WHITE)
    title_rect = title_text.get_rect(centerx=screen.get_width() // 2, y=screen.get_height() * 0.25)
    screen.blit(title_text, title_rect)
    
    # Draw menu options, highlighting the selected one
    option_keys = ['resume_label', 'return_to_menu_label', 'quit_game_label']
    for i, key in enumerate(option_keys):
        color = (255, 255, 100) if i == selected_index else settings.WHITE
        if key == 'quit_game_label':
            color = (255, 100, 100) if i == selected_index else (200, 50, 50)
            
        text_surf = font_option.render(get_text(key), True, color)
        text_rect = text_surf.get_rect(centerx=screen.get_width() // 2, y=title_rect.bottom + 80 + i * 60)
        screen.blit(text_surf, text_rect)


def draw_killcam_hud(screen, top_text, bottom_text, bottom_text_color):
    """
    Draws the "Killcam" and "Catch!"/"Escape!" text during the replay.
    """
    top_font = pygame.font.Font(None, 80)
    bottom_font = pygame.font.Font(None, 120)
    
    # Draw "Killcam" text at the top
    top_surf = top_font.render(top_text, True, settings.WHITE)
    top_rect = top_surf.get_rect(center=(screen.get_width() // 2, 60))
    screen.blit(top_surf, top_rect)
    
    # Draw the main event text (e.g., "Catch!") in the center
    bottom_surf = bottom_font.render(bottom_text, True, bottom_text_color)
    bottom_rect = bottom_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    bg_rect = bottom_rect.inflate(20, 20)
    bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surf.fill((0, 0, 0, 150))
    screen.blit(bg_surf, bg_rect)
    screen.blit(bottom_surf, bottom_rect)