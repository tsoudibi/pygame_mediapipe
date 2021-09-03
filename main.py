import pygame
from pygame.locals import QUIT
import pygame.camera
import cv2
import random

# other file import
import mouse  as ms
import mediapipe_thread as mp_thread
from mediapipe_thread import SCREEN_WIDTH, SCREEN_HEIGHT 
import sprites as sp

# intilize
pygame.init()

# create screen 
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption(('pygame with mediapipe'))

# create mediapipe_thread 
thread_POSE = mp_thread.creat_and_start()

# create sprites group
allsprite = pygame.sprite.Group()  

# set clock
clock = pygame.time.Clock() 


def main():
    # run the game
    running = True
    while running:
        # set clock do 60 times/s
        clock.tick(60)
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # status update
        # set bakground as video capture, and resize as window size if not 
        background = mp_thread.get_image()
        # if flip is needed, do :
        # background = cv2.flip(background.swapaxes(0, 1), 2) 
        background = background.swapaxes(0, 1) 

        # screen drawing
        pygame.surfarray.blit_array(screen, background)

        # create new ball and add to group
        ball = sp.ball(10, random.randint(0,SCREEN_WIDTH), 0, (0,255,0))
        allsprite.add(ball)

        # update sprites status and draw
        for spr in allsprite:
            spr.update()
            if (spr.rect.y >= SCREEN_HEIGHT):
                allsprite.remove(spr)
        allsprite.draw(screen)

        # update
        pygame.display.update()

    # kill the thread 
    mp_thread.kill_thread()
    thread_POSE.join()

    pygame.quit()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
