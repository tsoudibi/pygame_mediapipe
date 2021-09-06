import pygame
import random
import math 

# import other files 
import mediapipe_thread as mp_thread

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

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
        self.forced = False # weather the ball is forced to move

        pygame.draw.circle(self.image, color, [radius,radius], radius, 0)

        self.kill = False

    def update(self):
        self.rect.y += 2
        self.rect.x += random.randint(-5,5)
        if self.rect.y >=  SCREEN_HEIGHT:
            self.kill = True

class mouse(pygame.sprite.Sprite):
    def __init__(self, idx, radius, x, y, color) :
        # init by parent
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([radius*2, radius*2])  # create canvas
        self.image.set_colorkey((0,0,0))
        self.radius = radius # set radius for circle sprite (for collide_circle)
        self.rect = self.image.get_rect() # create rect for collide detection 
        self.rect.center = (x, y)  # set initial position
        self.color = color

        pygame.draw.circle(self.image, color, [radius,radius], radius, 0)

        self.kill = False
        self.idx = idx
        self.distence = 0

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y
    
    def set_distence(self, distence):
        self.distence = distence

    def kill(self):
        self.kill = True

    def update(self, results):
        # make sure there is hand detected and weather each landmarks exist
        if results.multi_hand_landmarks:
            for hands_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if hand_landmarks:
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        if idx == 4: # THUMB_TIP
                            THUMB_TIP_x, THUMB_TIP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                        if idx == 8: # INDEX_FINGER_TIP
                            INDEX_FINGER_TIP_x, INDEX_FINGER_TIP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                    if hands_idx == self.idx :
                        self.set_distence(math.isqrt((THUMB_TIP_x - INDEX_FINGER_TIP_x)**2 + (THUMB_TIP_y - INDEX_FINGER_TIP_y)**2))
                        radius = int(self.distence * 0.15) #change size
                        self.image = pygame.Surface([radius*2, radius*2])  # create canvas
                        self.image.set_colorkey((0,0,0))
                        self.radius = radius # set radius for circle sprite (for collide_circle)
                        self.rect = self.image.get_rect() # create rect for collide detection 
                        self.rect.center = (round((THUMB_TIP_x + INDEX_FINGER_TIP_x)/2-radius/2), round((THUMB_TIP_y + INDEX_FINGER_TIP_y)/2-radius/2))
                        pygame.draw.circle(self.image, self.color, [radius,radius], radius, 0)


    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y