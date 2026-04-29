"""
Levels.py
Defines the abstract Level base class and all concrete level layouts.

Each level is built from a list of pygame.Rect platforms plus a list of
Trampoline objects. The routes are designed around the current player
physics so normal climbs stay within a one-tile rise unless a trampoline
is intentionally used to launch the player higher.
"""

from abc import ABC, abstractmethod

import pygame

from Coin import Coin
from Trampoline import Trampoline


class Level(ABC):
    """Abstract base class for all levels."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.floor: list[pygame.Rect] = []
        self.coins: list[Coin] = []
        self.trampolines: list[Trampoline] = []
        self._coin_counter = 0

        try:
            self.ground = pygame.image.load("Files/GrassTile.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.ground = pygame.Surface((64, 64))
            self.ground.fill((80, 160, 60))

        self.TILE = self.ground.get_width()
        self.H = screen.get_height()
        self.W = screen.get_width()

        self.build_floor()

    @abstractmethod
    def build_floor(self):
        """Populate self.floor and self.trampolines."""

    def draw(self):
        """Draw ground tiles and trampoline props for the active level."""
        tile = self.TILE
        for rect in self.floor:
            for x in range(rect.x, rect.x + rect.width, tile):
                self.screen.blit(self.ground, (x, rect.y))

        for coin in self.coins:
            coin.draw(self.screen)

        for trampoline in self.trampolines:
            trampoline.draw(self.screen)

    def get_floor(self) -> list:
        return self.floor

    def get_coins(self) -> list:
        return self.coins

    def get_trampolines(self) -> list:
        return self.trampolines

    def apply_collected_coin_ids(self, collected_ids: set[str]):
        """Hide any coins that were already collected in this level."""
        for coin in self.coins:
            coin.collected = coin.coin_id in collected_ids

    def collect_coins(self, player_rect: pygame.Rect) -> list[str]:
        """Collect overlapping coins and return their ids."""
        collected_ids: list[str] = []
        for coin in self.coins:
            if coin.try_collect(player_rect):
                collected_ids.append(coin.coin_id)
        return collected_ids

    def _add_ground_run(self, start_x: int, end_x: int):
        """Add a horizontal run of full-height ground tiles."""
        tile = self.TILE
        y = self.H - tile
        for x in range(start_x, end_x, tile):
            self.floor.append(pygame.Rect(x, y, tile, tile))

    def _add_platform(self, x: int, y: int, tiles_wide: int):
        """Add an elevated platform using the shared tile width."""
        self.floor.append(pygame.Rect(x, y, self.TILE * tiles_wide, 28))

    def _add_trampoline(self, x: int, y: int, width: int | None = None):
        """Add a trampoline that sits over a gap or void."""
        self.trampolines.append(Trampoline(x=x, y=y, width=width or self.TILE))

    def _add_coin(self, x: int, y: int, coin_id: str | None = None):
        """Add a collectible coin to the level."""
        if coin_id is None:
            coin_id = f"coin_{self._coin_counter}"
        self._coin_counter += 1
        self.coins.append(Coin(x=x, y=y, coin_id=coin_id))


class FirstLevel(Level):
    """Level 1: A friendly hillside route that teaches the first bounce."""

    def __init__(self, screen: pygame.Surface):
        try:
            self.sign = pygame.image.load("Files/StartSign.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.sign = None

        super().__init__(screen)

        tile = self.TILE
        self.sign_rect = pygame.Rect(
            50,
            self.H - tile - (self.sign.get_height() if self.sign else tile),
            self.sign.get_width() if self.sign else tile,
            self.sign.get_height() if self.sign else tile,
        )

    def build_floor(self):
        tile = self.TILE
        h = self.H

        # Warm-up staircase.
        self._add_ground_run(0, tile * 3)
        self._add_platform(230, h - tile * 2, 2)
        self._add_platform(390, h - tile * 3, 2)
        self._add_coin(120, h - tile - 36)
        self._add_coin(255, h - tile * 2 - 28)
        self._add_coin(332, h - tile * 2 - 52)
        self._add_coin(415, h - tile * 3 - 28)

        # Dip down before the first spring jump.
        self._add_platform(550, h - tile * 2, 1)
        self._add_trampoline(690, 590)
        self._add_coin(575, h - tile * 2 - 28)
        self._add_coin(708, 540)
        self._add_coin(730, 470)

        # Long finish bridge so the player can carry speed into the exit.
        self._add_platform(693, h - tile * 4, 3)
        self._add_coin(770, h - tile * 4 - 36)
        self._add_coin(850, h - tile * 4 - 20)

    def draw(self):
        super().draw()
        if self.sign:
            self.screen.blit(self.sign, self.sign_rect)


class SecondLevel(Level):
    """Level 2: Broken terraces that end in a rooftop trampoline launch."""

    def build_floor(self):
        tile = self.TILE
        h = self.H

        # A staggered climb with one bigger transfer into the spring lane.
        self._add_ground_run(0, tile * 2)
        self._add_platform(190, h - tile * 2, 1)
        self._add_platform(310, h - tile * 3, 2)
        self._add_platform(500, h - tile * 4, 1)
        self._add_platform(620, h - tile * 3, 1)
        self._add_coin(90, h - tile - 40)
        self._add_coin(215, h - tile * 2 - 28)
        self._add_coin(365, h - tile * 3 - 36)
        self._add_coin(525, h - tile * 4 - 30)
        self._add_coin(645, h - tile * 3 - 28)

        # Bounce out of a pit and onto the high finish route.
        self._add_trampoline(730, 580)
        self._add_platform(693, h - tile * 5, 3)
        self._add_coin(748, 530)
        self._add_coin(760, h - tile * 5 - 50)
        self._add_coin(845, h - tile * 5 - 24)


class ThirdLevel(Level):
    """Level 3: A rhythm course with two spring wells and narrow landings."""

    def __init__(self, screen: pygame.Surface):
        try:
            self.bg_tint = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self.bg_tint.fill((180, 100, 20, 30))
        except Exception:
            self.bg_tint = None
        super().__init__(screen)

    def build_floor(self):
        tile = self.TILE
        h = self.H

        # Tight staircase to establish the tempo.
        self._add_ground_run(0, tile * 2)
        self._add_platform(180, h - tile * 2, 1)
        self._add_platform(290, h - tile * 3, 1)
        self._add_platform(400, h - tile * 4, 1)
        self._add_coin(96, h - tile - 42)
        self._add_coin(205, h - tile * 2 - 28)
        self._add_coin(315, h - tile * 3 - 28)
        self._add_coin(425, h - tile * 4 - 28)

        # First spring sends the player into the middle route.
        self._add_trampoline(520, 560)
        self._add_platform(600, h - tile * 5, 1)
        self._add_platform(700, h - tile * 4, 1)
        self._add_coin(545, 510)
        self._add_coin(625, h - tile * 5 - 28)
        self._add_coin(725, h - tile * 4 - 28)

        # Second spring launches to the finish bridge.
        self._add_trampoline(800, 500)
        self._add_platform(770, h - tile * 6, 2)
        self._add_coin(815, 455)
        self._add_coin(815, h - tile * 6 - 44)
        self._add_coin(875, h - tile * 6 - 22)

    def draw(self):
        if self.bg_tint:
            self.screen.blit(self.bg_tint, (0, 0))
        super().draw()


class FourthLevel(Level):
    """Level 4: Sky ruins with two void jumps and a high suspended exit."""

    def __init__(self, screen: pygame.Surface):
        try:
            self.bg_tint = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self.bg_tint.fill((20, 20, 80, 40))
        except Exception:
            self.bg_tint = None
        super().__init__(screen)

    def build_floor(self):
        tile = self.TILE
        h = self.H

        # Early floating stones lead into the first spring gap.
        self._add_ground_run(0, tile * 2)
        self._add_platform(180, h - tile * 2, 1)
        self._add_platform(290, h - tile * 3, 1)
        self._add_trampoline(400, 580)
        self._add_coin(85, h - tile - 42)
        self._add_coin(205, h - tile * 2 - 28)
        self._add_coin(315, h - tile * 3 - 28)
        self._add_coin(425, 532)

        # Mid-air ruins.
        self._add_platform(500, h - tile * 5, 1)
        self._add_platform(610, h - tile * 6, 1)
        self._add_platform(710, h - tile * 5, 1)
        self._add_coin(525, h - tile * 5 - 34)
        self._add_coin(635, h - tile * 6 - 34)
        self._add_coin(735, h - tile * 5 - 34)

        # Final spring vaults the player up to the last island.
        self._add_trampoline(820, 500)
        self._add_platform(770, h - tile * 6, 2)
        self._add_coin(845, 450)
        self._add_coin(805, h - tile * 6 - 44)
        self._add_coin(875, h - tile * 6 - 20)

    def draw(self):
        if self.bg_tint:
            self.screen.blit(self.bg_tint, (0, 0))
        super().draw()


class FifthLevel(Level):
    """Level 5: A summit run with a chained bounce finish and crown perch."""

    def __init__(self, screen: pygame.Surface):
        try:
            self.bg_tint = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self.bg_tint.fill((80, 0, 80, 35))
        except Exception:
            self.bg_tint = None

        try:
            self.crown = pygame.image.load("Files/Crown.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.crown = None

        self.crown_pos = (832, 72)
        super().__init__(screen)

    def build_floor(self):
        tile = self.TILE
        h = self.H

        # Opening climb.
        self._add_ground_run(0, tile * 3)
        self._add_platform(230, h - tile * 2, 1)
        self._add_platform(340, h - tile * 3, 1)
        self._add_platform(450, h - tile * 4, 1)
        self._add_coin(120, h - tile - 42)
        self._add_coin(255, h - tile * 2 - 28)
        self._add_coin(365, h - tile * 3 - 28)
        self._add_coin(475, h - tile * 4 - 28)

        # First spring breaks into the upper mountain route.
        self._add_trampoline(560, 580)
        self._add_platform(640, h - tile * 6, 1)
        self._add_platform(720, h - tile * 7, 1)
        self._add_platform(770, h - tile * 6, 1)
        self._add_coin(585, 532)
        self._add_coin(665, h - tile * 6 - 30)
        self._add_coin(745, h - tile * 7 - 30)
        self._add_coin(795, h - tile * 6 - 30)

        # Final spring sends the player to the summit bridge.
        self._add_trampoline(820, 420)
        self._add_platform(770, h - tile * 7, 2)
        self._add_coin(845, 375)
        self._add_coin(815, h - tile * 7 - 44)
        self._add_coin(885, h - tile * 7 - 18)

    def draw(self):
        if self.bg_tint:
            self.screen.blit(self.bg_tint, (0, 0))
        super().draw()
        if self.crown:
            self.screen.blit(self.crown, self.crown_pos)
