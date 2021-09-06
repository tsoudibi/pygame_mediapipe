import pygame
from pygame.locals import QUIT
import pygame.camera
import cv2
import random

# other file import
import mediapipe_thread as mp_thread
from mediapipe_thread import SCREEN_WIDTH, SCREEN_HEIGHT 
import sprites as sp

# intilize
pygame.init()

# create screen 
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption(('pygame with mediapipe'))

# create mediapipe_thread 
thread_obj = mp_thread.mediapipe_data()
thread_obj.start()

# create sprites groups
allsprite = pygame.sprite.Group()  
allmouse = pygame.sprite.Group()  

# create new mouse and add to group
mouse_1 = sp.mouse(idx = 0, radius = 10, x = 0, y = 0, color = (0,0,255))
allmouse.add(mouse_1)

# create new ball and add to group
ball = sp.ball(50, random.randint(0,SCREEN_WIDTH), 0, (0,255,0))
allsprite.add(ball)

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
        background = thread_obj.get_image()
        # if flip is needed, do :
        # background = cv2.flip(background.swapaxes(0, 1), 2) 
        background = background.swapaxes(0, 1) 

        # screen drawing
        pygame.surfarray.blit_array(screen, background)

        # update sprites status and draw
        for spr in allsprite:
            spr.update()
            if (spr.kill == True):
                allsprite.remove(spr)
        allsprite.draw(screen)
        for mouse in allmouse:
            mouse.update(thread_obj.get_results())
            if (mouse.kill == True):
                allmouse.remove(mouse)
        allmouse.draw(screen)

        # update
        pygame.display.update()

    # kill the thread 
    thread_obj.kill_thread()

    pygame.quit()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
