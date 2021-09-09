# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)

import pygame

class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as message:
            self.sheet = pygame.image.load(filename).convert_alpha()
            print ('Unable to load spritesheet image:' + filename)
            raise SystemExit (message)
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None , scale = 1):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        #image = pygame.Surface((int(rect.size[0]*scale),int(rect.size[1]*scale))).convert()
        image = pygame.Surface(rect.size).convert()
        size = image.get_size()
        image.blit(self.sheet, (0, 0), rect)
        image = pygame.transform.scale(image,(int(size[0]*scale),int(size[1]*scale)))
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        else:
            image.set_colorkey((0,0,0), pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None, scale = 1):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey, scale = scale) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

def flip_images(images):
    new_images = []
    for image in images:
        new_images.append(pygame.transform.flip(image, True, False))
    return new_images
