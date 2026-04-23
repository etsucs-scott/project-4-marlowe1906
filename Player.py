import pygame 

class Player:
    def __init__(self, screen):
        self.screen = screen
        self.player = pygame.image.load("Files/Player.png")
        self.x = 100
        self.y = self.screen.get_height() - self.player.get_height() - 28
        self.speed = 5
        self.velocity = 0
        self.gravity = 0.8
        self.on_ground = False

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.velocity = -12        # negative = upward
            self.on_ground = False

    def apply_gravity(self):
        self.velocity += self.gravity  # pull down every frame
        self.y += self.velocity

    def check_collision(self, platforms):
        self.on_ground = False

        for platform in platforms:
            if self.get_rect().colliderect(platform):
                # Falling down — land on top
                if self.velocity > 0:
                    self.y = platform.top - self.player.get_height()
                    self.velocity = 0
                    self.on_ground = True
                # Moving up — hit ceiling
                

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.player.get_width(), self.player.get_height())
    
    def draw(self):
        self.screen.blit(self.player, (self.x, self.y))