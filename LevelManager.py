"""
level_manager.py
Manages the ordered collection of levels and tracks which is active.

Data structure: collections.OrderedDict maps integer indices to Level
constructors, giving O(1) lookup while preserving level order.
"""

from collections import OrderedDict
import pygame
from Levels import FirstLevel, SecondLevel, ThirdLevel, FourthLevel, FifthLevel


class LevelManager:
    """
    Owns the level registry and tracks the currently active level.

    The registry is an OrderedDict so levels are always iterated in
    insertion order (level 0 → 1 → 2 …) while also supporting fast
    index-based access.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        start_level: int = 0,
        collected_coins: dict[int, set[str]] | None = None,
    ):
        self.screen = screen
        self.collected_coins = collected_coins if collected_coins is not None else {}
        self._total_coin_count = None

        # Registry: index → Level constructor (not instance, to allow lazy init)
        self._registry: OrderedDict[int, type] = OrderedDict([
            (0, FirstLevel),
            (1, SecondLevel),
            (2, ThirdLevel),
            (3, FourthLevel),
            (4, FifthLevel)
        ])

        self.current_index = max(0, min(start_level, len(self._registry) - 1))
        self._current_level = None
        self._load_level(self.current_index)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_current_floor(self) -> list:
        """Return the platform rects for the active level."""
        return self._current_level.get_floor()

    def get_current_coins(self) -> list:
        """Return the collectible coins for the active level."""
        return self._current_level.get_coins()

    def get_current_trampolines(self) -> list:
        """Return the trampoline rects for the active level."""
        return self._current_level.get_trampolines()

    def collect_current_coins(self, player_rect: pygame.Rect) -> list[str]:
        """Collect coins overlapping the player and persist their ids."""
        collected_ids = self._current_level.collect_coins(player_rect)
        if collected_ids:
            saved = self.collected_coins.setdefault(self.current_index, set())
            saved.update(collected_ids)
        return collected_ids

    def draw(self):
        """Draw the active level."""
        self._current_level.draw()

    def next_level(self) -> bool:
        """
        Advance to the next level.
        Returns True if successful, False if already on the last level.
        """
        next_index = self.current_index + 1
        if next_index not in self._registry:
            return False
        self._load_level(next_index)
        return True
    
    def previous_level(self) -> bool:
        """
        Go back to the previous level.
        Returns True if successful, False if already on the first level.
        """
        prev_index = self.current_index - 1
        if prev_index not in self._registry:
            return False
        self._load_level(prev_index)
        return True
    
    def get_current_level(self) -> int:
        """Return the current level instance (for testing or advanced use)."""
        return self._current_level

    def total_levels(self) -> int:
        """Return the total number of registered levels."""
        return len(self._registry)

    def total_coin_count(self) -> int:
        """Return the total number of coins placed across all levels."""
        if self._total_coin_count is None:
            self._total_coin_count = 0
            for level_class in self._registry.values():
                level = level_class(self.screen)
                self._total_coin_count += len(level.get_coins())
        return self._total_coin_count

    def _load_level(self, level_index: int):
        """Instantiate the requested level and reapply collected coin state."""
        self.current_index = level_index
        self._current_level = self._registry[level_index](self.screen)
        collected_ids = self.collected_coins.get(level_index, set())
        self._current_level.apply_collected_coin_ids(collected_ids)
