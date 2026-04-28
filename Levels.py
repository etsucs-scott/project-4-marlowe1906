"""
levels.py
Defines the abstract Level base class and all concrete level classes.
Each level owns its floor rects and knows how to draw itself.

Data structure highlight: platforms are stored in a list of pygame.Rect,
but the level registry in LevelManager uses an OrderedDict so level order
is both preserved and keyed by index for O(1) lookup.
"""

import pygame
from abc import ABC, abstractmethod
from Trampoline import Trampoline


class Level(ABC):
    """
    Abstract base class for all levels.
    Subclasses must implement build_floor() and optionally override draw().
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.floor: list[pygame.Rect] = []
        self.trampolines: list[pygame.Rect] = []

        # Load shared tile image — catch errors gracefully
        try:
            self.ground = pygame.image.load("Files/GrassTile.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            # Fallback: a green surface so the game still runs without assets
            self.ground = pygame.Surface((64, 64))
            self.ground.fill((80, 160, 60))

        self.TILE = self.ground.get_width()
        self.H = screen.get_height()
        self.W = screen.get_width()

        self.build_floor()

    @abstractmethod
    def build_floor(self):
        """Populate self.floor with pygame.Rect objects for this level."""

    def draw(self):
        """
        Draw every platform by tiling the ground image across the rect width.
        Subclasses can call super().draw() and then add extra decorations.
        """
        T = self.TILE
        for rect in self.floor:
            for x in range(rect.x, rect.x + rect.width, T):
                self.screen.blit(self.ground, (x, rect.y))

        for t in self.trampolines:
            t.draw(self.screen)

    def get_floor(self) -> list:
        """Return the list of platform rects for collision detection."""
        return self.floor
    
    def get_trampolines(self) -> list:
        return self.trampolines

    # ------------------------------------------------------------------
    # Helpers shared by subclasses
    # ------------------------------------------------------------------

    def _add_ground_run(self, start_x: int, end_x: int):
        """Add a horizontal run of floor tiles from start_x to end_x."""
        T = self.TILE
        H = self.H
        for x in range(start_x, end_x, T):
            self.floor.append(pygame.Rect(x, H - T, T, T))

    def _add_platform(self, x: int, y: int, tiles_wide: int):
        """Add a single elevated platform."""
        T = self.TILE
        self.floor.append(pygame.Rect(x, y, T * tiles_wide, 28))


# ======================================================================
# Level 1 — Medium staircase with gaps
# ======================================================================

class FirstLevel(Level):
    """
    Level 1: Introduces gaps and a rising staircase.
    Teaches the player the jump arc before harder platforming.
    """

    def __init__(self, screen: pygame.Surface):
        try:
            self.sign = pygame.image.load("Files/StartSign.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.sign = None

        super().__init__(screen)

        T = self.TILE
        H = self.H
        self.sign_rect = pygame.Rect(
            50,
            H - T - (self.sign.get_height() if self.sign else T),
            self.sign.get_width() if self.sign else T,
            self.sign.get_height() if self.sign else T,
        )

    def build_floor(self):
        T = self.TILE
        H = self.H
        W = self.W

        # Ground chunks (gaps force short hops)
        self._add_ground_run(0,             T * 3)
        self._add_ground_run(T * 3 + 30,    T * 5 + 30)

        # Section 1 — rising staircase (~60 px steps, within 90 px max jump)
        self._add_platform(T * 5 + 60,  H - T * 2 + 10, 2)
        self._add_platform(T * 7 + 80,  H - T * 3 + 10, 2)
        self._add_platform(T * 9 + 110, H - T * 4 + 10, 2)

        # Section 2 — peak then drop
        self._add_platform(T * 11 + 150, H - T * 5 + 10, 1)   # peak
        self._add_platform(T * 12 + 200, H - T * 3,      3)   # wide landing

        # Section 3 — gap jumps
        self._add_platform(T * 15 + 240, H - T * 4, 1)
        self._add_platform(T * 16 + 270, H - T * 6, 2)        # high point
        self._add_platform(T * 18 + 300, H - T * 4, 2)        # descend

        # Section 4 — final climb
        self._add_platform(T * 21 + 330, H - T * 5, 1)
        self._add_platform(T * 22 + 360, H - T * 7, 2)        # highest
        self._add_platform(T * 24 + 390, H - T * 5, 1)
        self._add_platform(T * 25 + 420, H - T * 3, 2)        # end platform

    def draw(self):
        super().draw()
        if self.sign:
            self.screen.blit(self.sign, self.sign_rect)


# ======================================================================
# Level 2 — Longer gaps, no staircase safety net
# ======================================================================

class SecondLevel(Level):
    """
    Level 2: Four acts — ascent, controlled drop, gap gauntlet, high-ceiling finale.
    All platforms are within physics reach; gaps increase in difficulty toward the end.
    Uses only integer tile coordinates (no float multipliers).
    """

    def build_floor(self):
        T = self.TILE   # 64
        H = self.H      # 690
        W = self.W      # 924

        # ── Ground chunks ──────────────────────────────────────────────────
        # Start pad — enough room to get moving
        self._add_ground_run(0, T * 2)                 # 0–128

        # Mid recovery ground — wide enough to catch a bad landing
        self._add_ground_run(T * 4, T * 7)             # 256–448

        # End ground — goal zone
        self._add_ground_run(T * 12, W)                # 768–924

        # ── Section 1: Gentle ascent (teaches the jump arc) ───────────────
        # Each step: ~64 px horizontal gap, ~64 px height gain — safe and readable
        self._add_platform(T * 2 + 20,  H - T * 2,      1)   # 148, y=562  step 1
        self._add_platform(T * 3 + 30,  H - T * 3,      1)   # 222, y=498  step 2
        self._add_platform(T * 5 + 10,  H - T * 4,      2)   # 330, y=434  landing (wide)

        # ── Section 2: Deliberate drop + gap challenge ─────────────────────
        # Player drops from the wide landing, must then navigate rightward gaps
        # Horizontal gaps ~110px — within reach but demanding
        self._add_platform(T * 7 + 20,  H - T * 2 + 10,  1)  # 468, y=572  low step
        self._add_platform(T * 9,       H - T * 3,        2)  # 576, y=498  recovery (wide)

# ======================================================================
# Level 3 — The Gauntlet: tight gaps, no safety ground, punishing rhythm
# ======================================================================

class ThirdLevel(Level):
    """
    Level 3: Strips away ground safety nets almost entirely.
    Forces the player to chain precise jumps in a strict rhythm.
    A small start pad and a small end pad — nothing in between.
    """

    def __init__(self, screen: pygame.Surface):
        try:
            self.bg_tint = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self.bg_tint.fill((180, 100, 20, 30))   # warm amber tint
        except Exception:
            self.bg_tint = None
        super().__init__(screen)

    def build_floor(self):
        T = self.TILE   # 64
        H = self.H      # 690
        W = self.W      # 924

        # Tiny start pad — just enough to land on
        self._add_ground_run(0, T * 2)                          # 0–128

        # ── Act 1: Rapid low staircase (px gaps ~80, height ~64) ──────────
        self._add_platform(T * 2 + 50,  H - T * 2,       1)    # 178,  y=562
        self._add_platform(T * 3 + 70,  H - T * 3,       1)    # 262,  y=498
        self._add_platform(T * 4 + 80,  H - T * 4,       1)    # 336,  y=434
        self._add_platform(T * 5 + 90,  H - T * 5,       1)    # 410,  y=370  peak of act 1

        # ── Act 2: Drop into a zigzag — alternating low/high ──────────────
        # Player must consciously aim downward then up; no coasting
        self._add_platform(T * 6 + 100, H - T * 3,       1)    # 484,  y=498  drop
        self._add_platform(T * 8 + 115, H - T * 3,       1)    # 627,  y=498  drop again

        # ── Act 3: Wide gap, single tile targets — no margin for error ────
        # Horizontal gaps ~115–125px — near the player's max reach
        self._add_platform(T * 10 + 100, H - T * 3,       1)    # 754,  y=434

    def draw(self):
        if self.bg_tint:
            self.screen.blit(self.bg_tint, (0, 0))
        super().draw()


# ======================================================================
# Level 4 — The Abyss: pure floating platforms, no ground at all
# ======================================================================

class FourthLevel(Level):
    """
    Level 4: The floor is lava (or rather, the void).
    No ground chunks except a tiny start and end island.
    Platforms are arranged in three waves: a long crossing, 
    a descending slope, and a tight vertical finale.
    """
    
    def __init__(self, screen: pygame.Surface):
        try:
            self.bg_tint = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self.bg_tint.fill((20, 20, 80, 40))   # deep blue/void tint
        except Exception:
            self.bg_tint = None
        super().__init__(screen)

    def build_floor(self):
        T = self.TILE   # 64
        H = self.H      # 690
        W = self.W      # 924

        # Tiny start island
        self._add_ground_run(0, T * 2)                            # 0–128

        # ── Wave 1: Long mid-height crossing ──────────────────────────────
        # Consistent height, gaps ~100px — tests horizontal precision
        self._add_platform(T * 2 + 40,  H - T * 4,       2)     # 168,  y=434  wide first step
        self._add_platform(T * 4 + 60,  H - T * 4,       1)     # 316,  y=434
        self._add_platform(T * 5 + 70,  H - T * 4,       1)     # 390,  y=434
        self._add_platform(T * 6 + 80,  H - T * 4,       1)     # 464,  y=434

        # ── Wave 2: Descending slope — each step ~64px lower ──────────────
        # Player must control descent without falling past the next platform
        self._add_platform(T * 7 + 90,  H - T * 5,       1)     # 538,  y=370  (one step up for rhythm break)
        self._add_platform(T * 8 + 100, H - T * 3,       1)     # 612,  y=498  big drop
        self._add_platform(T * 9 + 110, H - T * 2,       2)     # 686,  y=562  near-ground wide catch

        # ── Wave 3: Tight vertical finale ─────────────────────────────────
        # Player climbs rapidly from near-ground to near-ceiling
        # Each jump is ~80–85px up — within max height but demanding
        self._add_platform(T * 11 + 50, H - T * 4,       1)     # 754,  y=434  relaunch
        self._add_platform(T * 12 + 60, H - T * 6,       1)     # 828,  y=306  climb
        self._add_platform(T * 13 + 70, H - T * 8,       2)     # 902,  y=178  near-ceiling wide finish

        # Tiny end island at screen right — player walks off the top platform
        # and lands on the end ground below while advancing right
        self._add_ground_run(T * 13 + 70, W)                     # 902–924 (ground under finale)

        self.trampolines.append(Trampoline(x=90, y=H - self.TILE, width=self.TILE))
        
    def draw(self):
        if self.bg_tint:
            self.screen.blit(self.bg_tint, (0, 0))
        super().draw()


# ======================================================================
# Level 5 — The Summit: vertical climb with punishing drops
# ======================================================================

class FifthLevel(Level):
    """
    Level 5: The final level. A brutal vertical climb to the very top,
    then a harrowing rightward traverse near the ceiling with tiny platforms.
    Falling from the top sends the player almost all the way back down.
    Three distinct zones: base climb, mid-traverse, summit sprint.
    """

    def __init__(self, screen: pygame.Surface):
        try:
            self.bg_tint = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self.bg_tint.fill((80, 0, 80, 35))   # dark purple tint — feels final
        except Exception:
            self.bg_tint = None

        try:
            self.crown = pygame.image.load("Files/Crown.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.crown = None

        super().__init__(screen)

    def build_floor(self):
        T = self.TILE   # 64
        H = self.H      # 690
        W = self.W      # 924

        # Ground start — generous, let the player breathe before the climb
        self._add_ground_run(0, T * 3)                            # 0–192

        # ── Zone 1: Base climb — staggered left/right ascent ──────────────
        # Platforms alternate sides so player weaves upward
        # Height gain ~80px per jump — near the cap
        self._add_platform(T * 3 + 20,  H - T * 2,       2)     # 212,  y=562  low right
        self._add_platform(T * 1 + 10,  H - T * 4,       2)     # 74,   y=434  back left (backtrack forces rhythm)
        self._add_platform(T * 3 + 30,  H - T * 6,       2)     # 222,  y=306  right again
        self._add_platform(T * 1 + 10,  H - T * 8,       2)     # 74,   y=178  left — near ceiling

        # ── Zone 2: Mid traverse — rightward run at mid-height ────────────
        # After the climb the player must cover horizontal distance quickly
        # Platforms at ~H - T*6 = 306px, gaps ~100–120px — demanding spacing
        self._add_platform(T * 4 + 40,  H - T * 6,       1)     # 296,  y=306
        self._add_platform(T * 5 + 60,  H - T * 7,       1)     # 380,  y=242  step up
        self._add_platform(T * 6 + 80,  H - T * 6,       1)     # 464,  y=306  step down
        self._add_platform(T * 7 + 100, H - T * 8,       1)     # 548,  y=178  high point
        self._add_platform(T * 8 + 110, H - T * 6,       2)     # 622,  y=306  wide recovery

        # ── Zone 3: Summit sprint — tiny platforms near ceiling ───────────
        # Single-tile targets, ~115px apart, near H - T*8 = 178px from top
        # A miss here is a long fall back to zone 2 or lower
        self._add_platform(T * 10 + 80, H - T * 8,       1)     # 720,  y=178
        self._add_platform(T * 11 + 90, H - T * 9,       1)     # 794,  y=114  near ceiling
        self._add_platform(T * 12 + 100,H - T * 8,       1)     # 868,  y=178

        # End ground — final sprint to the finish line
        self._add_ground_run(T * 13 + 60, W)                     # 892–924

    def draw(self):
        if self.bg_tint:
            self.screen.blit(self.bg_tint, (0, 0))
        super().draw()
        # Draw a small crown above the finish area as a visual reward cue
        if self.crown:
            T = self.TILE
            cx = T * 13 + 60
            cy = self.H - T * 2
            self.screen.blit(self.crown, (cx, cy))