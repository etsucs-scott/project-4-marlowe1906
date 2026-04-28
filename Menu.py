"""
menu.py
Renders and handles input for the main menu screen.
Returns action strings to the main loop rather than calling game logic directly.
"""

import pygame


class MainMenu:
    """
    Draws a simple main menu with New Game, Continue, and Quit options.
    Communicates back to the caller via string actions returned from handle_event().
    """

    _OPTIONS = ["new_game", "continue", "quit"]
    _LABELS  = ["New Game", "Continue", "Quit"]

    def __init__(self, screen: pygame.Surface, save_manager):
        self.screen = screen
        self.save_manager = save_manager
        self._selected = 0
        self._font_title = pygame.font.SysFont(None, 80)
        self._font_item  = pygame.font.SysFont(None, 48)
        self._font_sub   = pygame.font.SysFont(None, 28)
        W, H = screen.get_size()
        self._center_x = W // 2
        self._start_y  = H // 2 - 60

    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """
        Process a single pygame event.
        Returns an action string when the user confirms a selection, else None.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(self._OPTIONS)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(self._OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                action = self._OPTIONS[self._selected]
                # 'continue' only works if a save exists
                if action == "continue" and not self.save_manager.has_save():
                    return None
                return action
        return None

    def draw(self):
        """Draw the menu background and option list."""
        self.screen.fill((15, 15, 30))
        self._draw_title()
        self._draw_options()
        self._draw_footer()

    # ------------------------------------------------------------------

    def _draw_title(self):
        title = self._font_title.render("PLATFORMER", True, (80, 200, 120))
        shadow = self._font_title.render("PLATFORMER", True, (20, 80, 40))
        self.screen.blit(shadow, (self._center_x - title.get_width() // 2 + 3,
                                  self._start_y - 130 + 3))
        self.screen.blit(title,  (self._center_x - title.get_width() // 2,
                                  self._start_y - 130))

    def _draw_options(self):
        for i, label in enumerate(self._LABELS):
            # Grey out Continue if no save exists
            if label == "Continue" and not self.save_manager.has_save():
                color = (80, 80, 80)
            elif i == self._selected:
                color = (255, 220, 50)
            else:
                color = (180, 180, 180)

            prefix = "> " if i == self._selected else "  "
            text = self._font_item.render(prefix + label, True, color)
            y = self._start_y + i * 60
            self.screen.blit(text, (self._center_x - text.get_width() // 2, y))

    def _draw_footer(self):
        hint = self._font_sub.render("UP/DOWN to navigate   ENTER to select", True, (80, 80, 100))
        self.screen.blit(hint, (self._center_x - hint.get_width() // 2,
                                self.screen.get_height() - 40))