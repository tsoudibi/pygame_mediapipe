# ---------------------------------------------------
# this file create a thred to do mediapipe in 
# background, use the result to update mouse or other
# object.
# after drawing, save the image as image_main, others
# can use this to display.
# ---------------------------------------------------

import cv2
import mediapipe as mp
import time
import threading
import mouse  as ms

# create mouse class
mouse_1 = ms.Mouse(idx = 0)
mouse_2 = ms.Mouse(idx = 1, color = (0,0,255))

# create mediapipe object
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# active camera, use cv2 rather then pygame
camera = cv2.VideoCapture(0)
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

# dynamic settings of mediapipe thread
MP_MODE = 'hands'
MP_LOOP = True

# cap images, contain main image and backup regard of video capture fail
_, image_main = camera.read()
image_backup = image_main

# funtion to run mediapipe and create image 
def mediapipe_pose():
    global image_main, image_backup, camera 
    if MP_MODE == 'pose':
        pose = mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5)
    elif MP_MODE == 'hands':
        hands = mp_hands.Hands(min_detection_confidence = 0.6, min_tracking_confidence = 0.5)
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
            # display mouse
            image = mouse_1.display(image, results)
            image = mouse_2.display(image, results)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image,hand_landmarks,mp_hands.HAND_CONNECTIONS)
        # after drawing, change color back tp rgb
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # save image to global and backup
        image_main = image
        image_backup = image
        print('success' + str(time.time()-time1))
    # if anything wrong happend, use backup image
    image_main = image_backup
    # https://google.github.io/mediapipe/solutions/pose#static_image_mode
        

def creat_and_start():
    # create a thread to run mediapipe, than start it 
    thread_POSE = threading.Thread(target = mediapipe_pose)
    thread_POSE.start()
    return thread_POSE

def get_image():
    return image_main

def kill_thread():
    global MP_LOOP
    MP_LOOP = False
