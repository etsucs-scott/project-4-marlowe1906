"""
main.py
Entry point for the platformer game. Initializes pygame, manages the
top-level game state machine (menu, playing, game over, win), and runs
the main game loop.
"""

import pygame
import sys
from LevelManager import LevelManager
from Player import Player
from SaveManager import SaveManager
from Hud import HUD
from Menu import MainMenu
from EventLog import EventLog

SCREEN_WIDTH = 924
SCREEN_HEIGHT = 690
FPS = 60
TITLE = "Platformer"


def main():
    """Initialize pygame and run the main game loop."""
    pygame.init()
    background = pygame.image.load("Files/Background.png")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    save_manager = SaveManager("saves/progress.json")
    event_log = EventLog(max_size=50)
    menu = MainMenu(screen, save_manager)
    hud = None
    player = None
    level_manager = None

    # Game states: "menu", "playing", "game_over", "win"
    state = "menu"

    try:
        game_over_img = pygame.image.load("Files/GameOver.png")
        game_over_img = pygame.transform.scale(game_over_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except (pygame.error, FileNotFoundError):
        # Fallback if image missing
        game_over_img = None

    def start_game(level_index=0):
        """Helper to initialize or restart the game from a given level."""
        nonlocal player, level_manager, hud
        level_manager = LevelManager(screen, start_level=level_index)
        player = Player(screen, level_manager.get_current_floor())
        hud = HUD(screen, player, level_manager)
        event_log.push(f"Started level {level_index + 1}")

    running = True
    while running:
        dt = clock.tick(FPS)

        # ---- Event handling ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "menu":
                action = menu.handle_event(event)
                if action == "new_game":
                    save_manager.reset()
                    start_game(0)
                    state = "playing"
                elif action == "continue":
                    saved = save_manager.load()
                    start_game(saved.get("level", 0))
                    state = "playing"
                elif action == "quit":
                    running = False

            elif state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        save_manager.save({"level": level_manager.current_index})
                        state = "menu"
                    if event.key == pygame.K_r:
                        start_game(level_manager.current_index)

            elif state in ("game_over", "win"):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        start_game(level_manager.current_index)
                        state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"

        # ---- Update & Draw ----
        if state == "menu":
            menu.draw()

        elif state == "playing":
            keys = pygame.key.get_pressed()
            player.update(keys, level_manager.get_current_floor(), level_manager.get_current_trampolines())

            # Check level completion (reached right edge)
            if player.rect.x >= SCREEN_WIDTH - 40:
                event_log.push(f"Completed level {level_manager.current_index + 1}")
                save_manager.save({"level": level_manager.current_index + 1})
                advanced = level_manager.next_level()
                if advanced:
                    player.reset(level_manager.get_current_floor())
                else:
                    state = "win"
            if player.rect.x <= 0 and level_manager.current_index == 0:
                event_log.push("Player walked off the start")
                state = "game_over"
            if player.rect.x <= 0 and level_manager.current_index > 0:
                event_log.push("Player walked off the left edge")
                previous_level = level_manager.previous_level()
                if previous_level:
                    player.reset(level_manager.get_current_floor())
                else:
                    state = "game_over"

            # Check fell off map
            if not player.check_on_map(SCREEN_WIDTH, SCREEN_HEIGHT, level_manager.current_index):
                event_log.push("Player fell off the map")
                state = "game_over"

            screen.blit(background, (0, 0))
            level_manager.draw()
            player.draw()
            hud.draw()

        elif state == "game_over":
            if game_over_img:
                screen.blit(game_over_img, (0, 0))
            else:
                screen.fill((20, 20, 20))
                font = pygame.font.SysFont(None, 72)
                text = font.render("GAME OVER", True, (220, 50, 50))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 280))

            font_sm = pygame.font.SysFont(None, 36)
            hint = font_sm.render("R = Retry   ESC = Menu", True, (200, 200, 200))
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))

        elif state == "win":
            screen.fill((20, 40, 20))
            font = pygame.font.SysFont(None, 72)
            text = font.render("YOU WIN!", True, (80, 220, 80))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 260))
            font_sm = pygame.font.SysFont(None, 36)
            hint = font_sm.render("R = Play Again   ESC = Menu", True, (180, 180, 180))
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))

        pygame.display.flip()

    save_manager.save({"level": level_manager.current_index if level_manager else 0})
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()