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
allfish = pygame.sprite.Group()  
allmouse = pygame.sprite.Group() 
fishtank = pygame.sprite.Group() 


# create new mouse and add to group
mouse_1 = sp.mouse(idx = 0, radius = 10, x = 0, y = 0, color = (0,0,255))
allmouse.add(mouse_1)

# create new fish and add to group
doux = sp.fish( type = 'doux', scale = 10, speed = 3)
tard = sp.fish( type = 'tard', scale = 10, speed = 2)
allfish.add(doux)
allfish.add(tard)

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
        for stuff in fishtank:
            stuff.update()
            if (stuff.kill == True):
                fishtank.remove(stuff)
        fishtank.draw(screen)

        for fish in allfish:
            fish.draw(screen)
            fish.update(mouse_1)
            if (fish.kill == True):
                allfish.remove(fish)
        allfish.draw(screen)

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
