from cmath import rect

import pygame

class FirstLevel:
    def __init__(self, screen):
        self.screen = screen
        self.floor = []
        self.ground = pygame.image.load("Files/GrassTile.png")
        self.sign = pygame.image.load("Files/StartSign.png")
        pygame.rect.Rect(50, self.screen.get_height() - self.ground.get_height() - self.sign.get_height(), self.sign.get_width(), self.sign.get_height())
        
        for i in range(0, self.screen.get_width(), self.ground.get_width()):
            self.floor.append(pygame.Rect(i, self.screen.get_height() - self.ground.get_height(), self.ground.get_width(), self.ground.get_height()))

        platform1 = pygame.rect.Rect(200, 580, self.ground.get_width(), self.ground.get_height())  # Example platform
        platform2 = pygame.rect.Rect(300, 520, self.ground.get_width(), self.ground.get_height())  # Example platform
        platform3 = pygame.rect.Rect(400, 460, self.ground.get_width(), self.ground.get_height())  # Example platform

        self.floor.append(platform1)
        self.floor.append(platform2)
        self.floor.append(platform3)

    def draw(self):
        for rect in self.floor:
            self.screen.blit(self.ground, rect)

    def get_floor(self):
        return self.floor
