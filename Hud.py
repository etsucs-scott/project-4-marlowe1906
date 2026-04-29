"""
hud.py
Heads-Up Display drawn on top of the game world each frame.
Shows current level number and a hint bar at the bottom.
"""

import pygame


class HUD:
    """
    Draws game information on screen without owning game logic.

    Receives references to Player and LevelManager so it can read
    whatever stats it needs without coupling them to drawing code.
    """

    def __init__(self, screen: pygame.Surface, player, level_manager):
        self.screen = screen
        self.player = player
        self.level_manager = level_manager
        self._font_large = pygame.font.SysFont(None, 36)
        self._font_small = pygame.font.SysFont(None, 24)

    def draw(self):
        """Render the HUD layer. Call after drawing the world."""
        self._draw_level_indicator()
        self._draw_coin_counter()
        self._draw_hints()

    def _draw_level_indicator(self):
        lvl = self.level_manager.current_index + 1
        total = self.level_manager.total_levels()
        text = self._font_large.render(f"Level {lvl} / {total}", True, (255, 255, 255))
        # Drop shadow for readability over any background
        shadow = self._font_large.render(f"Level {lvl} / {total}", True, (0, 0, 0))
        self.screen.blit(shadow, (12, 12))
        self.screen.blit(text,   (10, 10))

    def _draw_coin_counter(self):
        coins = self.player.coins
        current_level_coins = self.level_manager.get_current_coins()
        collected_here = sum(1 for coin in current_level_coins if coin.collected)
        total_here = len(current_level_coins)

        total_text = self._font_large.render(f"Coins: {coins}", True, (255, 230, 90))
        total_shadow = self._font_large.render(f"Coins: {coins}", True, (0, 0, 0))
        total_x = self.screen.get_width() - total_text.get_width() - 18
        self.screen.blit(total_shadow, (total_x + 2, 12))
        self.screen.blit(total_text, (total_x, 10))

        level_text = self._font_small.render(
            f"Level coins: {collected_here}/{total_here}",
            True,
            (240, 240, 200),
        )
        level_shadow = self._font_small.render(
            f"Level coins: {collected_here}/{total_here}",
            True,
            (0, 0, 0),
        )
        level_x = self.screen.get_width() - level_text.get_width() - 18
        self.screen.blit(level_shadow, (level_x + 1, 46))
        self.screen.blit(level_text, (level_x, 44))

    def _draw_hints(self):
        hint = "Arrow keys / WASD = move   SPACE = jump   R = restart   ESC = menu"
        text = self._font_small.render(hint, True, (220, 220, 220))
        x = self.screen.get_width() // 2 - text.get_width() // 2
        y = self.screen.get_height() - 28
        self.screen.blit(text, (x, y))
