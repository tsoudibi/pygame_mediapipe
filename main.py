from datetime import time
import sys
import pygame
from pygame.locals import QUIT
import pygame.camera
import cv2
import mediapipe as mp
import time

# intilize
pygame.init()
width, height = 640, 480

# create mediapipe object
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# active camera, use cv2 rather then pygame
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
ret, background = camera.read()

# create screen 
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('pygame with mediapipe')

# image backup regard of video capture fail
image_backup = background

# funtion to run mediapipe and create image 
def mediapipe_pose():
    global image_backup
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        global camera
        if camera.isOpened():
            success, image = camera.read()
            if not success:
                print("Ignoring empty camera frame.")
                # video capture fail, use backup image
                return image_backup

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            results = pose.process(image)

            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks( 
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # after drawing, change color back tp rgb
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # backup image 
            image_backup = image
            #return to pygame
            return image
        return image_backup
        # https://google.github.io/mediapipe/solutions/pose#static_image_mode

# run the game
running = True
while running:
    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # status update
    # set bakground as video capture, and resize as window size if not 
    background = mediapipe_pose()
    background = cv2.flip(background.swapaxes(0, 1), 0) # swap axis and flip image
    pygame.surfarray.blit_array(screen, background)


    # screen drawing
    pygame.display.update()

pygame.quit()
cv2.destroyAllWindows()

