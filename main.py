from datetime import time
import sys
import pygame
from pygame.locals import QUIT
import pygame.camera
import cv2
import mediapipe as mp
import time
import threading

# intilize
pygame.init()
width, height = 640, 480

# create mediapipe object
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# active camera, use cv2 rather then pygame
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# take first image 
_, background = camera.read()
background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
background = cv2.flip(background, 1) # swap axis and flip image

# create screen 
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('pygame with mediapipe')

# cap images, contain main image and backup regard of video capture fail
image_main = background
image_backup = background

# bool to kill looping
loop_pose = True

# notify the target mode of mediapipe
MP_MODE = 'hands'

# funtion to run mediapipe and create image 
def mediapipe_pose():
    global image_main, image_backup, camera 
    if MP_MODE == 'pose':
        pose = mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)
    elif MP_MODE == 'hands':
        hands = mp_hands.Hands(min_detection_confidence=0.5,min_tracking_confidence=0.5)
    while  camera.isOpened() and loop_pose:
        time1 = time.time()
        success, image = camera.read()
        if not success:
            print("Ignoring empty camera frame.")
            # video capture fail, use backup image
            image_main = image_backup

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        if MP_MODE == 'pose':
            results = pose.process(image)
        elif MP_MODE == 'hands':
            results = hands.process(image)
        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # drawing landmarks
        if MP_MODE == 'pose':
            mp_drawing.draw_landmarks( 
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        elif MP_MODE == 'hands':
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmark_style(),
                        mp_drawing_styles.get_default_hand_connection_style())
            
        # after drawing, change color back tp rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # backup image 
        image_backup = image
        # save image to global
        image_main = image
        print('success' + str(time.time()-time1))
    # if anything wrong happend, use backup image
    image_main = image_backup
    # https://google.github.io/mediapipe/solutions/pose#static_image_mode
        


# create a thread to run mediapipe, than start it 
thread_POSE = threading.Thread(target = mediapipe_pose)
thread_POSE.start()

def main():
    global image_main
    # run the game
    running = True
    while running:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # status update
        # set bakground as video capture, and resize as window size if not 
        background = image_main
        # if flip is needed, do :
        # background = cv2.flip(background.swapaxes(0, 1), 2) 
        background = background.swapaxes(0, 1) 

        pygame.surfarray.blit_array(screen, background)


        # screen drawing
        pygame.display.update()

    # kill the thread 
    global loop_pose
    loop_pose = False
    thread_POSE.join()

    pygame.quit()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
