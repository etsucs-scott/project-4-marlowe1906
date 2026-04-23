import pygame 
from FirstLevel import FirstLevel
from Player import Player

pygame.init()

bg = pygame.image.load("Files/Background.png")
clock = pygame.time.Clock()
height = bg.get_height()
width = bg.get_width()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Platformer Game")
running = True

first = FirstLevel(screen)
player = Player(screen)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.handle_input()
    player.apply_gravity()
    player.check_collision(first.get_floor())  # ✅ Check against platforms

    screen.blit(bg, (0, 0))
    first.draw()
    player.draw()
    pygame.display.flip()
    clock.tick(60)