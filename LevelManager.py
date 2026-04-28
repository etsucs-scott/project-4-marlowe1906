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

    def __init__(self, screen: pygame.Surface, start_level: int = 0):
        self.screen = screen

        # Registry: index → Level constructor (not instance, to allow lazy init)
        self._registry: OrderedDict[int, type] = OrderedDict([
            (0, FirstLevel),
            (1, SecondLevel),
            (2, ThirdLevel),
            (3, FourthLevel),
            (4, FifthLevel)
        ])

        self.current_index = max(0, min(start_level, len(self._registry) - 1))
        self._current_level = self._registry[self.current_index](screen)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_current_floor(self) -> list:
        """Return the platform rects for the active level."""
        return self._current_level.get_floor()

    def get_current_trampolines(self) -> list:
        """Return the trampoline rects for the active level."""
        return self._current_level.get_trampolines()

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
        self.current_index = next_index
        self._current_level = self._registry[next_index](self.screen)
        return True
    
    def previous_level(self) -> bool:
        """
        Go back to the previous level.
        Returns True if successful, False if already on the first level.
        """
        prev_index = self.current_index - 1
        if prev_index not in self._registry:
            return False
        self.current_index = prev_index
        self._current_level = self._registry[prev_index](self.screen)
        return True
    
    def get_current_level(self) -> int:
        """Return the current level instance (for testing or advanced use)."""
        return self._current_level

    def total_levels(self) -> int:
        """Return the total number of registered levels."""
        return len(self._registry)

    def get_current_trampolines(self) -> list:
        return self._current_level.get_trampolines()