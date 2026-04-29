"""
Coin.py
Collectible coin objects used by platformer levels.
"""

import math

import pygame


class Coin:
    """A collectible coin that can be drawn and picked up once."""

    SIZE = 18

    def __init__(self, x: int, y: int, coin_id: str, size: int = SIZE):
        self.coin_id = coin_id
        self.collected = False
        self.rect = pygame.Rect(x, y, size, size)

        try:
            image = pygame.image.load("Files/Coin.png").convert_alpha()
            self._sprite = pygame.transform.scale(image, (size, size))
        except (pygame.error, FileNotFoundError):
            self._sprite = None

    def try_collect(self, player_rect: pygame.Rect) -> bool:
        """Mark the coin as collected if the player overlaps it."""
        if self.collected:
            return False
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the coin with a subtle bob so it reads as collectible."""
        if self.collected:
            return

        bob_y = int(math.sin(pygame.time.get_ticks() / 180 + self.rect.x * 0.03) * 3)
        draw_y = self.rect.y + bob_y

        if self._sprite:
            screen.blit(self._sprite, (self.rect.x, draw_y))
            return

        center = (self.rect.centerx, draw_y + self.rect.height // 2)
        radius = self.rect.width // 2
        pygame.draw.circle(screen, (205, 140, 20), center, radius)
        pygame.draw.circle(screen, (245, 210, 70), center, radius - 2)
        pygame.draw.circle(screen, (255, 240, 160), center, max(2, radius - 7))
