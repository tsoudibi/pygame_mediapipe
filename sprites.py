import pygame
import random
import math 

# import other files 
import mediapipe_thread as mp_thread
import spritesheet 

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
        self.distence_tip = 0
        self.distence_mcp = 0

    def kill(self):
        self.kill = True
    
    def is_push_down(self):
        return self.distence_tip < self.distence_mcp

    def update(self, results):
        # make sure there is hand detected and weather each landmarks exist
        if results != None:
            if results.multi_hand_landmarks :
                for hands_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    if hand_landmarks:
                        for idx, landmark in enumerate(hand_landmarks.landmark):
                            if idx == 2: # THUMB_MCP
                                THUMB_MCP_x, THUMB_MCP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                            elif idx == 4: # THUMB_TIP
                                THUMB_TIP_x, THUMB_TIP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                            elif idx == 5: # INDEX_FINGER_MCP
                                INDEX_FINGER_MCP_x, INDEX_FINGER_MCP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                            elif idx == 8: # INDEX_FINGER_TIP
                                INDEX_FINGER_TIP_x, INDEX_FINGER_TIP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                        if hands_idx == self.idx :
                            self.distence_tip = math.isqrt((THUMB_TIP_x - INDEX_FINGER_TIP_x)**2 + (THUMB_TIP_y - INDEX_FINGER_TIP_y)**2)
                            self.distence_mcp = math.isqrt((THUMB_MCP_x - INDEX_FINGER_MCP_x)**2 + (THUMB_MCP_y - INDEX_FINGER_MCP_y)**2)
                            # redraw the circle
                            radius = int(self.distence_tip * 0.15) #change size
                            self.image = pygame.Surface([radius*2, radius*2])  # create canvas
                            self.image.set_colorkey((0,0,0))
                            self.radius = radius # set radius for circle sprite (for collide_circle)
                            self.rect = self.image.get_rect() # create rect for collide detection 
                            self.rect.center = (round((THUMB_TIP_x + INDEX_FINGER_TIP_x)/2-radius/2), round((THUMB_TIP_y + INDEX_FINGER_TIP_y)/2-radius/2))

                            # test
                            if self.is_push_down():
                                self.color = (0,255,0)
                            else:
                                self.color = (0,0,255)
                            pygame.draw.circle(self.image, self.color, [radius,radius], radius, 0)


class fish(pygame.sprite.Sprite):
    def __init__(self, x = SCREEN_WIDTH/2, y = SCREEN_HEIGHT/2, color = (0,0,0),
                type = 'doux', speed = 3, scale = 10) :
        # init by parent
        pygame.sprite.Sprite.__init__(self)

        ## sprite sheet
        if type == 'doux':
            dino_ss = spritesheet.spritesheet('.\pygame_mediapipe\images\dino_sheets\Dino_doux.png')
        elif type == 'mort':
            dino_ss = spritesheet.spritesheet('.\pygame_mediapipe\images\dino_sheets\Dino_mort.png')
        elif type == 'tard':
            dino_ss = spritesheet.spritesheet('.\pygame_mediapipe\images\dino_sheets\Dino_tard.png')
        elif type == 'vita':
            dino_ss = spritesheet.spritesheet('.\pygame_mediapipe\images\dino_sheets\Dino_vita.png')
        self.idle_frame_R = []
        self.move_frame_R = []
        self.idle_frame_R = dino_ss.images_at( ((4, 4, 15, 17), (28, 4, 15, 17),(52, 4, 15, 17),(76, 4, 15, 17)), scale = scale)
        self.move_frame_R = dino_ss.images_at( ((76, 4, 15, 17), (100, 4, 15, 17),(124, 4, 15, 17),(148, 4, 15, 17),
                                            (172, 4, 15, 17),(196, 4, 15, 17),(220, 4, 15, 17),(244, 4, 15, 17)), scale = scale)
        self.idle_frame_L = spritesheet.flip_images(self.idle_frame_R)
        self.move_frame_L = spritesheet.flip_images(self.move_frame_R)

        self.image = self.move_frame_R[0]  # create canvas
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect() # create rect for collide detection 
        self.rect.center = (x, y)  # set initial position
        self.kill = False

        #pygame.draw.circle(self.image, color, [radius,radius], radius, 0)

        # fish setting 
        self.color = color
        self.speed = speed
        self.forced = False # weather the fish is forced to move
        self.dir = (random.randint(self.speed * -1,self.speed),random.randint(self.speed * -1,self.speed)) # moving direction \
        self.excite = 200 # the smaller, the fasterthe fish will change its dir
        self.excite_timer = self.excite
        self.facing = 'R'
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255,0,0), self.rect, 2)

    def update(self, mouse):
        if  pygame.sprite.collide_rect(self, mouse) and mouse.is_push_down():
            self.forced = True
            # forced to move
            self.rect.y = mouse.rect.y - self.rect.height / 2
            self.rect.x = mouse.rect.x - self.rect.width / 2
        else:
            self.forced = False
            # free swimming
            if self.excite_timer <= 0:
                # out of excite, change dir
                self.dir = (random.randint(self.speed * -1,self.speed),random.randint(self.speed * -1,self.speed))
                self.excite_timer = self.excite
            else:
                # set the range of the fish to move
                border = 100
                # horizontal
                if self.rect.y <=  SCREEN_HEIGHT - self.rect.height - border and self.rect.y >=  border:
                    self.rect.y += self.dir[1]
                else :
                    # if out of border, change direction 
                    if self.rect.y > SCREEN_HEIGHT/2 : self.rect.y = SCREEN_HEIGHT - self.rect.height - border
                    else: self.rect.y =  border
                    self.dir =  (self.dir[0], self.dir[1] * -1)
                # vertical
                if self.rect.x <=  SCREEN_WIDTH - self.rect.width - border and self.rect.x >=  border:
                    self.rect.x += self.dir[0]
                else:
                    # if out of border, change direction 
                    if self.rect.x > SCREEN_WIDTH/2 : self.rect.x =  SCREEN_WIDTH - self.rect.width - border
                    else: self.rect.x =  border
                    self.dir =  (self.dir[0] * -1, self.dir[1])
            # changing frame by facing
            if self.dir[0] > 0:
                self.facing = 'R'
                frame = (self.rect.x // 30) % len(self.move_frame_R)
                self.image = self.move_frame_R[frame]
            elif self.dir[0] < 0:
                self.facing = 'L'
                frame = (self.rect.x // 30) % len(self.move_frame_L)
                self.image = self.move_frame_L[frame]
            self.excite_timer -= 1