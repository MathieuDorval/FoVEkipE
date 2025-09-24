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

def draw_game_info(screen, scores, round_time, players, round_duration):
    """
    Dessine les informations de jeu à l'écran.
    """
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

    # --- Wac ---
    bar_width = 150
    bar_height = 15
    bar_spacing = 5

    for i, predator in enumerate(predators):
        if predator.is_active:
            wac_ratio = predator.Wac / predator.stats['WacMax'] if predator.stats.get('WacMax', 0) > 0 else 0
            wac_ratio = min(1.0, max(0.0, wac_ratio))
            
            bar_y = pred_rect.bottom + bar_spacing + i * (bar_height + bar_spacing)
            bar_x = pred_rect.right - bar_width
            
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            remaining_wac_width = bar_width * (1 - wac_ratio)
            pygame.draw.rect(screen, predator.color, (bar_x, bar_y, remaining_wac_width, bar_height))
            pygame.draw.rect(screen, settings.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    for i, prey in enumerate(preys):
        if prey.is_active:
            wac_ratio = prey.Wac / prey.stats['WacMax'] if prey.stats.get('WacMax', 0) > 0 else 0
            wac_ratio = min(1.0, max(0.0, wac_ratio))

            bar_y = prey_rect.bottom + bar_spacing + i * (bar_height + bar_spacing)
            bar_x = prey_rect.left
            
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            remaining_wac_width = bar_width * (1 - wac_ratio)
            pygame.draw.rect(screen, prey.color, (bar_x, bar_y, remaining_wac_width, bar_height))
            pygame.draw.rect(screen, settings.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)


def draw_player_panel(screen, player_id, base_rect, game_settings, is_ready):
    """
    Dessine le panneau d'information pour un joueur dans le menu.
    """
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 20)
    ready_color = (100, 255, 100)

    player_colors = [settings.COLOR_PLAYER1, settings.COLOR_PLAYER2, settings.COLOR_PLAYER3, settings.COLOR_PLAYER4]
    title_color = player_colors[player_id - 1]

    pygame.draw.rect(screen, (20, 20, 20), base_rect, border_radius=10)
    pygame.draw.rect(screen, (80, 80, 80), base_rect, width=1, border_radius=10)

    status_key = f'p{player_id}_status'
    status = game_settings.get(status_key, "INACTIVE")
    
    role = game_settings.get(f'p{player_id}_role', 'prey')
    is_predator = (role == 'predator')
    role_text = "Predator" if is_predator else "Prey"
    role_color = settings.COLOR_PREDATOR if is_predator else (settings.COLOR_PREY)
    
    # --- Title ---
    title_str = f"Player {player_id} ({status})"
    title_text = font_medium.render(title_str, True, title_color)
    title_rect = title_text.get_rect(midtop=(base_rect.centerx, base_rect.top + 10))
    screen.blit(title_text, title_rect)
    
    # --- Prey / Pred ---
    role_surf = font_small.render(role_text, True, role_color)
    role_rect = role_surf.get_rect(midtop=(base_rect.centerx, title_rect.bottom + 8))
    screen.blit(role_surf, role_rect)

    # --- Animal ---
    animal_index_key = f'p{player_id}_animal_index'
    animal_name = ANIMALS[game_settings.get(animal_index_key, 0)]["name"]
    animal_text = font_tiny.render(animal_name, True, settings.WHITE)
    animal_rect = animal_text.get_rect(midtop=(base_rect.centerx, role_rect.bottom + 8))
    screen.blit(animal_text, animal_rect)

    if is_ready and status != "AI":
        font_large_ready = pygame.font.Font(None, int(base_rect.height * 0.5))
        
        text_surf = font_large_ready.render("READY", True, ready_color)
        rotated_surf = pygame.transform.rotate(text_surf, 30)
        rotated_surf.set_alpha(100)
        
        rotated_rect = rotated_surf.get_rect(center=base_rect.center)
        screen.blit(rotated_surf, rotated_rect)


def draw_menu(screen, game_settings, p_ready, role_error_message=""):
    """
    Dessine les informations pour l'écran de menu.
    """
    font_large = pygame.font.Font(None, 74)
    
    # --- Title ---
    title_text = font_large.render("FoVEkipE", True, settings.WHITE)
    title_rect = title_text.get_rect(midtop=(screen.get_width() // 2, 20))
    screen.blit(title_text, title_rect)

    # --- Player Pannel ---
    panel_width = screen.get_width() * 0.22
    panel_height = screen.get_height() * 0.25
    
    positions = [
        pygame.Rect(10, 10, panel_width, panel_height),
        pygame.Rect(screen.get_width() - panel_width - 10, 10, panel_width, panel_height),
        pygame.Rect(10, screen.get_height() - panel_height - 10, panel_width, panel_height),
        pygame.Rect(screen.get_width() - panel_width - 10, screen.get_height() - panel_height - 10, panel_width, panel_height)
    ]
    
    num_joysticks = pygame.joystick.get_count()
    max_players = 4 if num_joysticks > 1 else 2

    for i in range(max_players):
        player_id = i + 1
        status = game_settings.get(f'p{player_id}_status', 'INACTIVE')
        
        if player_id > 2 and status == "INACTIVE":
            continue
            
        is_ready = p_ready.get(player_id, False)
        draw_player_panel(screen, player_id, positions[i], game_settings, is_ready)

    # --- Error Message ---
    if role_error_message:
        font_error = pygame.font.Font(None, 40)
        error_text = font_error.render(role_error_message, True, (255, 80, 80))
        
        bg_rect = error_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50)).inflate(20, 10)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 180))
        
        screen.blit(bg_surf, bg_rect)
        screen.blit(error_text, error_text.get_rect(center=bg_rect.center))


def draw_settings_menu(screen, game_settings, selected_index, option_keys):
    """
    Dessine le menu des paramètres.
    """
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
        "Map Width": f"{game_settings['map_width']}m"
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
    """
    Dessine l'écran de fin de partie avec les scores finaux par équipe.
    """
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
    """
    Dessine le HUD de la killcam.
    """
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