import pygame

class End(pygame.sprite.Sprite):

    def __init__(self, pos, size):
        super().__init__()
        self.image=pygame.Surface((size,size))
        self.image = pygame.image.load("graphics/background/ending_game.png")
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift
