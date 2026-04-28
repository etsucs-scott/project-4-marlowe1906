"""
Trampoline.py
A Trampoline object that any level can place.
When the player lands on it, they receive a boosted upward velocity.
"""

import pygame


class Trampoline:
    """
    A single trampoline tile. Behaves like a platform for collision purposes
    but applies a strong upward impulse instead of a normal landing.
    """

    BOUNCE_VELOCITY = -22       # strong enough to reach ~H - T*4 from ground
    STRETCH_FRAMES  = 8         # how many frames the squash animation plays

    # Visual colours (fallback if no image)
    COLOUR_BASE    = (200, 60,  60)   # red frame
    COLOUR_SURFACE = (240, 120, 80)   # orange trampoline bed
    COLOUR_SPRING  = (160, 160, 160)  # grey legs

    def __init__(self, x: int, y: int, width: int = 64):
        self.rect   = pygame.Rect(x, y, width, 16)
        self._timer = 0          # countdown for squash animation

        # Try to load a sprite; fall back to procedural drawing
        try:
            img = pygame.image.load("Files/Trampoline.png").convert_alpha()
            self._sprite = pygame.transform.scale(img, (width, 32))
        except (pygame.error, FileNotFoundError):
            self._sprite = None

    # ------------------------------------------------------------------

    def apply_bounce(self, player) -> None:
        """
        Call this when the player collides from above.
        Sets the player's vertical velocity to the bounce value and
        starts the squash animation.
        """
        player.vel_y = self.BOUNCE_VELOCITY
        player.on_ground  = False
        self._timer       = self.STRETCH_FRAMES

    def update(self) -> None:
        """Tick down the animation timer each frame."""
        if self._timer > 0:
            self._timer -= 1

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the trampoline, squashing vertically when activated."""
        if self._sprite:
            self._draw_sprite(screen)
        else:
            self._draw_procedural(screen)

    # ------------------------------------------------------------------
    # Internal drawing helpers
    # ------------------------------------------------------------------

    def _squash(self) -> float:
        """Return a 0-1 squash factor (1 = fully stretched, 0 = normal)."""
        return self._timer / self.STRETCH_FRAMES

    def _draw_sprite(self, screen: pygame.Surface) -> None:
        x = self.rect.x
        y = self.rect.y - 16        # sprite sits 16px above the collision rect
        squash = self._squash()
        if squash > 0:
            # Compress the sprite vertically when bouncing
            h      = max(4, int(32 * (1 - squash * 0.4)))
            scaled = pygame.transform.scale(self._sprite, (self.rect.width, h))
            screen.blit(scaled, (x, y + (32 - h)))
        else:
            screen.blit(self._sprite, (x, y))

    def _draw_procedural(self, screen: pygame.Surface) -> None:
        """Draws a simple but readable trampoline without any image asset."""
        rx  = self.rect.x
        ry  = self.rect.y
        rw  = self.rect.width
        squash = self._squash()

        leg_h  = max(4, int(14 * (1 - squash * 0.5)))   # legs compress on bounce
        bed_y  = ry - 6
        bed_h  = max(3, int(10 * (1 - squash * 0.3)))   # bed flattens on bounce

        # Legs (two vertical rectangles)
        leg_w = 6
        pygame.draw.rect(screen, self.COLOUR_SPRING,
                         (rx + 4,        ry - leg_h, leg_w, leg_h))
        pygame.draw.rect(screen, self.COLOUR_SPRING,
                         (rx + rw - 10,  ry - leg_h, leg_w, leg_h))

        # Frame bar
        pygame.draw.rect(screen, self.COLOUR_BASE,
                         (rx, ry, rw, 8), border_radius=3)

        # Trampoline bed (sits above the frame)
        pygame.draw.rect(screen, self.COLOUR_SURFACE,
                         (rx + 4, bed_y - bed_h + 6, rw - 8, bed_h),
                         border_radius=2)

        # Highlight line across the bed
        pygame.draw.line(screen, (255, 200, 160),
                         (rx + 6,      bed_y - bed_h + 8),
                         (rx + rw - 6, bed_y - bed_h + 8), 1)