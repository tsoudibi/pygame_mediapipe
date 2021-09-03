import pygame
import random

class ball(pygame.sprite.Sprite):
    def __init__(self, radius, x, y, color) :
        # init by parent
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([radius*2, radius*2])  # create canvas
        self.image.set_colorkey((0,0,0))

        self.radius = radius # set radius for circle sprite (for collide_circle)
        self.rect = self.image.get_rect() # create rect for collide detection 
        self.rect.center = (x, y)  # set initial position

        self.color = color

        pygame.draw.circle(self.image, color, [radius,radius], radius, 0)

    def update(self):
        self.rect.y += 2
        self.rect.x += random.randint(-5,5)