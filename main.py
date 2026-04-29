"""
main.py
Entry point for the platformer game. Initializes pygame, manages the
top-level game state machine (menu, playing, game over, win), and runs
the main game loop.
"""

import math
import sys

import pygame

from EventLog import EventLog
from Hud import HUD
from LevelManager import LevelManager
from Menu import MainMenu
from Player import Player
from SaveManager import SaveManager

SCREEN_WIDTH = 924
SCREEN_HEIGHT = 690
FPS = 60
TITLE = "Platformer"


def _load_coin_progress(raw_data) -> dict[int, set[str]]:
    """Convert saved JSON coin progress into in-memory sets keyed by level."""
    if not isinstance(raw_data, dict):
        return {}

    coin_progress: dict[int, set[str]] = {}
    for level_key, coin_ids in raw_data.items():
        try:
            level_index = int(level_key)
        except (TypeError, ValueError):
            continue
        if isinstance(coin_ids, list):
            coin_progress[level_index] = {
                coin_id for coin_id in coin_ids if isinstance(coin_id, str)
            }
    return coin_progress


def _serialize_coin_progress(coin_progress: dict[int, set[str]]) -> dict[str, list[str]]:
    """Convert in-memory coin progress into a JSON-safe dictionary."""
    return {
        str(level_index): sorted(coin_ids)
        for level_index, coin_ids in coin_progress.items()
        if coin_ids
    }


def _draw_win_animation(
    screen: pygame.Surface,
    elapsed_ms: int,
    total_coins: int,
    total_possible_coins: int,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    hint_font: pygame.font.Font,
):
    """Draw a simple animated celebration shown after the final finish."""
    t = elapsed_ms / 1000.0
    pulse = math.sin(t * 2.5)
    screen.fill(
        (
            int(26 + 12 * pulse),
            int(74 + 28 * pulse),
            int(32 + 18 * pulse),
        )
    )

    glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(
        glow,
        (255, 248, 180, 40),
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20),
        150,
    )
    screen.blit(glow, (0, 0))

    confetti_colors = [
        (255, 225, 90),
        (255, 120, 120),
        (120, 220, 170),
        (120, 190, 255),
        (255, 255, 255),
    ]
    confetti_count = max(12, min(60, total_coins * 2))
    lane_width = SCREEN_WIDTH / confetti_count
    for index in range(confetti_count):
        x = int(index * lane_width + (lane_width * 0.25))
        y = int((elapsed_ms * (0.10 + (index % 4) * 0.02) + index * 38) % (SCREEN_HEIGHT + 80)) - 40
        drift = int(math.sin(t * 2.0 + index) * 12)
        width = 6 + (index % 3)
        height = 10 + (index % 4)
        rect = pygame.Rect(x + drift, y, width, height)
        pygame.draw.rect(screen, confetti_colors[index % len(confetti_colors)], rect, border_radius=2)

    bounce_y = int(math.sin(t * 4.0) * 8)
    title_shadow = title_font.render("YOU WIN!", True, (22, 75, 36))
    title_text = title_font.render("YOU WIN!", True, (250, 255, 220))
    title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    title_y = 210 - title_text.get_height() // 2 + bounce_y
    screen.blit(title_shadow, (title_x + 4, title_y + 4))
    screen.blit(title_text, (title_x, title_y))

    subtitle = body_font.render("You made it to the finish!", True, (230, 245, 230))
    subtitle_x = SCREEN_WIDTH // 2 - subtitle.get_width() // 2
    screen.blit(subtitle, (subtitle_x, 300))

    coins_text = body_font.render(f"Coins Collected: {total_coins}", True, (255, 233, 120))
    coins_shadow = body_font.render(f"Coins Collected: {total_coins}", True, (30, 50, 20))
    coins_x = SCREEN_WIDTH // 2 - coins_text.get_width() // 2
    screen.blit(coins_shadow, (coins_x + 2, 350))
    screen.blit(coins_text, (coins_x, 348))

    if total_possible_coins > 0 and total_coins >= total_possible_coins:
        special_text = body_font.render("Perfect run! Every coin collected!", True, (255, 250, 170))
        special_shadow = body_font.render("Perfect run! Every coin collected!", True, (40, 60, 25))
        special_x = SCREEN_WIDTH // 2 - special_text.get_width() // 2
        screen.blit(special_shadow, (special_x + 2, 392))
        screen.blit(special_text, (special_x, 390))

    hint = hint_font.render("R = Play Again   ESC = Menu", True, (230, 236, 230))
    hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
    screen.blit(hint, (hint_x, SCREEN_HEIGHT - 90))


def main():
    """Initialize pygame and run the main game loop."""
    pygame.init()
    background = pygame.image.load("Files/Background.png")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    win_title_font = pygame.font.SysFont(None, 92)
    win_body_font = pygame.font.SysFont(None, 38)
    win_hint_font = pygame.font.SysFont(None, 34)

    save_manager = SaveManager("saves/progress.json")
    event_log = EventLog(max_size=50)
    menu = MainMenu(screen, save_manager)
    hud = None
    player = None
    level_manager = None
    coin_progress: dict[int, set[str]] = {}
    win_started_at = 0

    # Game states: "menu", "playing", "game_over", "win"
    state = "menu"

    try:
        game_over_img = pygame.image.load("Files/GameOver.png")
        game_over_img = pygame.transform.scale(game_over_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except (pygame.error, FileNotFoundError):
        game_over_img = None

    def save_progress():
        """Persist the current level, coins, and collected pickups."""
        current_level = level_manager.current_index if level_manager else 0
        current_coins = player.coins if player else 0
        save_manager.save(
            {
                "level": current_level,
                "coins": current_coins,
                "collected_coins": _serialize_coin_progress(coin_progress),
            }
        )

    def start_game(level_index=0, coins=0):
        """Initialize or restart the game from a given level."""
        nonlocal player, level_manager, hud, win_started_at
        level_manager = LevelManager(
            screen,
            start_level=level_index,
            collected_coins=coin_progress,
        )
        player = Player(screen, level_manager.get_current_floor())
        player.coins = coins
        hud = HUD(screen, player, level_manager)
        win_started_at = 0
        event_log.push(f"Started level {level_index + 1}")

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "menu":
                action = menu.handle_event(event)
                if action == "new_game":
                    save_manager.reset()
                    coin_progress.clear()
                    start_game(0, 0)
                    state = "playing"
                elif action == "continue":
                    saved = save_manager.load()
                    coin_progress.clear()
                    coin_progress.update(_load_coin_progress(saved.get("collected_coins", {})))
                    start_game(saved.get("level", 0), saved.get("coins", 0))
                    state = "playing"
                elif action == "quit":
                    running = False

            elif state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        save_progress()
                        state = "menu"
                    if event.key == pygame.K_r:
                        start_game(level_manager.current_index, player.coins)

            elif state in ("game_over", "win"):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        start_game(level_manager.current_index, player.coins)
                        state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        save_progress()
                        state = "menu"

        if state == "menu":
            menu.draw()

        elif state == "playing":
            keys = pygame.key.get_pressed()
            player.update(
                keys,
                level_manager.get_current_floor(),
                level_manager.get_current_trampolines(),
            )

            collected_ids = level_manager.collect_current_coins(player.rect)
            if collected_ids:
                player.coins += len(collected_ids)
                if len(collected_ids) == 1:
                    event_log.push("Collected 1 coin")
                else:
                    event_log.push(f"Collected {len(collected_ids)} coins")

            if player.rect.x >= SCREEN_WIDTH - 40:
                event_log.push(f"Completed level {level_manager.current_index + 1}")
                advanced = level_manager.next_level()
                if advanced:
                    player.reset(level_manager.get_current_floor())
                    save_progress()
                else:
                    save_progress()
                    win_started_at = pygame.time.get_ticks()
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
            elapsed_ms = pygame.time.get_ticks() - win_started_at if win_started_at else 0
            _draw_win_animation(
                screen,
                elapsed_ms,
                player.coins if player else 0,
                level_manager.total_coin_count() if level_manager else 0,
                win_title_font,
                win_body_font,
                win_hint_font,
            )

        pygame.display.flip()

    save_progress()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
