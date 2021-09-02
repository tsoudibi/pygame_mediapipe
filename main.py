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
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

# create mediapipe object
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# active camera, use cv2 rather then pygame
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

# take first image 
_, background = camera.read()
background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
background = cv2.flip(background, 1) # swap axis and flip image

# create screen 
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('pygame with mediapipe')

# cap images, contain main image and backup regard of video capture fail
image_main = background
image_backup = background

# define mouse class
class Mouse:
    def __init__(self, x = 0, y = 0, size = 10, color = (255, 126, 79), thickness = -1):
        self.x = x
        self.y = y 
        self.size = size
        self.color = color
        self.thickness = thickness
    
    def set_position(self, x, y):
        self.x = x
        self.y = y 
    def set_color(self, color):
        self.color = color
mouse_1 = Mouse()
mouse_2 = Mouse(color = (0,0,255))

# draw the connection between two fingers
def mouse_display(image, results):
    # make sure there is hand detected and weather each landmarks exist
    if results.multi_hand_landmarks:
        for hands_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            if hand_landmarks:
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    if idx == 4: # THUMB_TIP
                        THUMB_TIP_x, THUMB_TIP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                    if idx == 8: # INDEX_FINGER_TIP
                        INDEX_FINGER_TIP_x, INDEX_FINGER_TIP_y = int(landmark.x * SCREEN_WIDTH), int(landmark.y * SCREEN_HEIGHT)
                if hands_idx == 0 :
                    mouse_1.set_position( round((THUMB_TIP_x + INDEX_FINGER_TIP_x)/2), round((THUMB_TIP_y + INDEX_FINGER_TIP_y)/2))
                    cv2.circle(image, ( mouse_1.x, mouse_1.y ), mouse_1.size, mouse_1.color, mouse_1.thickness)
                elif hands_idx == 1 :
                    mouse_2.set_position( round((THUMB_TIP_x + INDEX_FINGER_TIP_x)/2), round((THUMB_TIP_y + INDEX_FINGER_TIP_y)/2))
                    cv2.circle(image, ( mouse_2.x, mouse_2.y ), mouse_2.size, mouse_2.color, mouse_2.thickness)
    return image

# dynamic settings of mediapipe thread
MP_MODE = 'hands'
MP_LOOP = True

# funtion to run mediapipe and create image 
def mediapipe_pose():
    global image_main, image_backup, camera 
    if MP_MODE == 'pose':
        pose = mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)
    elif MP_MODE == 'hands':
        hands = mp_hands.Hands(min_detection_confidence=0.5,min_tracking_confidence=0.5)
    while  camera.isOpened() and MP_LOOP:
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
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        elif MP_MODE == 'hands':
            image = mouse_display(image, results)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image,hand_landmarks,mp_hands.HAND_CONNECTIONS)
            
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
    global MP_LOOP
    MP_LOOP = False
    thread_POSE.join()

    pygame.quit()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
