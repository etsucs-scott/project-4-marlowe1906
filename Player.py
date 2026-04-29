"""
player.py
Defines the Player class, which handles movement, gravity, jumping,
collision detection with floor rects, and drawing.
"""

import pygame

GRAVITY = 0.8
JUMP_VELOCITY = -12
MOVE_SPEED = 5


class Player:
    """
    Represents the player character.

    Attributes:
        rect      -- pygame.Rect for position and collision
        vel_y     -- current vertical velocity (positive = falling)
        on_ground -- True when standing on a platform
        coins     -- number of coins collected (tracked for HUD/save)
    """

    def __init__(self, screen: pygame.Surface, floor: list):
        self.screen = screen
        self.width = 20
        self.height = 35

        spawn_y = screen.get_height() - 64 - self.height
        self.rect = pygame.Rect(60, spawn_y, self.width, self.height)
        self.vel_y = 0.0
        self.on_ground = False
        self.coins = 0
        self.facing = "right"
        self.is_moving = False

        self._idle_image = pygame.image.load("Files/Player.png").convert_alpha()
        self._run_right_image = pygame.image.load("Files/RunningRight.png").convert_alpha()
        self._run_left_image = pygame.image.load("Files/RunningLeft.png").convert_alpha()

    def reset(self, floor: list):
        """Reset player to spawn position for a new level."""
        spawn_y = self.screen.get_height() - 64 - self.height
        self.rect.x = 60
        self.rect.y = spawn_y
        self.vel_y = 0.0
        self.on_ground = False
        self.is_moving = False

    def update(self, keys: pygame.key.ScancodeWrapper, floor: list, trampoline: list):
        """
        Apply input, gravity, movement, and resolve collisions.
        Called once per frame from the main loop.
        """
        self._handle_input(keys)
        self._apply_gravity()
        self._move_and_collide(floor)
        self._on_trampoline(trampoline)

    def _handle_input(self, keys):
        """Read keyboard state and move horizontally / initiate jump."""
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.is_moving = moving_left or moving_right

        if moving_left:
            self.rect.x -= MOVE_SPEED
            self.facing = "left"
        if moving_right:
            self.rect.x += MOVE_SPEED
            self.facing = "right"
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False

    def _apply_gravity(self):
        """Add gravity to vertical velocity each frame."""
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)

    def _move_and_collide(self, floor: list):
        """Resolve collisions against the current level floor."""
        self.on_ground = False

        for platform in floor:
            if self.rect.colliderect(platform):
                if self.vel_y > 0 and self.rect.bottom > platform.top and self.rect.top < platform.top:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True

        # Keep the player grounded when they are resting exactly on a platform.
        if not self.on_ground and self.vel_y >= 0:
            foot_probe = self.rect.move(0, 1)
            for platform in floor:
                if foot_probe.colliderect(platform):
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                    break

    def _on_trampoline(self, trampolines):
        """Bounce the player when they land on a trampoline."""
        for trampoline in trampolines:
            trampoline.update()
            if (
                self.vel_y > 0
                and self.rect.colliderect(trampoline.rect)
                and self.rect.bottom <= trampoline.rect.bottom + 10
            ):
                trampoline.apply_bounce(self)

    def check_on_map(self, width: int, height: int, level_index: int = 0) -> bool:
        if self.rect.y > height:
            return False
        if self.rect.x < -self.width and level_index == 0:
            return False
        return True

    def draw(self):
        """Draw the player using idle and running sprites."""
        if self.is_moving and self.on_ground:
            if self.facing == "left":
                player_image = self._run_left_image
            else:
                player_image = self._run_right_image
        else:
            player_image = self._idle_image

        self.screen.blit(player_image, (self.rect.x, self.rect.y))
