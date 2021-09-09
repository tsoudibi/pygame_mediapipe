# ---------------------------------------------------
# this file create a thred to do mediapipe in 
# background, use the result to update mouse or other
# object.
# after drawing, save the image as image_main, others
# can use this to display.
# result_main is passing to mouse.py to caculate pos
# ---------------------------------------------------

import cv2
import mediapipe as mp
import numpy as np
import threading



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

class mediapipe_data(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self )
        # dynamic settings of mediapipe thread
        self.MP_MODE = 'hands'
        self.MP_LOOP = True
        self.results_main = None
        _, image = camera.read()
        self.image_main = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def kill_thread(self):
        self.MP_LOOP = False

    def get_image(self):
        return self.image_main
    def get_results(self):
        if self.results_main:
            return self.results_main
        else:
            return None
    
    # funtion to run mediapipe and create image 
    def run(self):
        global camera
        if self.MP_MODE == 'pose':
            pose = mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5)
        elif self.MP_MODE == 'hands':
            hands = mp_hands.Hands(min_detection_confidence = 0.8, min_tracking_confidence = 0.5)
        while  camera.isOpened() and self.MP_LOOP:
            success, image = camera.read()
             # image = fish_eye_fix(image)
            if not success:
                print("Ignoring empty camera frame.")
                # video capture fail, use backup image
                self.image_main = self.image_backup

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            if self.MP_MODE == 'pose':
                results = pose.process(image)
                self.results_main = results 
            elif self.MP_MODE == 'hands':
                results = hands.process(image)
                self.results_main = results 
            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # drawing landmarks
            if self.MP_MODE == 'pose':
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            elif self.MP_MODE == 'hands':
                # display mouse
                #image = mouse_1.display(image, results)
                #image = mouse_2.display(image, results)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image,hand_landmarks,mp_hands.HAND_CONNECTIONS)
            # after drawing, change color back tp rgb
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # save image to global and backup
            self.image_main = image
            self.image_backup = image
        # if anything wrong happend, use backup image
        self.image_main = self.image_backup
        # https://google.github.io/mediapipe/solutions/pose#static_image_mode

# fix matrix to correct fisheye
DIM = (2560, 1440)
K = np.array([[1694.7801205342007, 0.0, 1363.235424743914], [0.0, 1694.4106664109822, 686.0493220616949], [0.0, 0.0, 1.0]])
D = np.array([[-0.010547721322285927], [0.02576312669611254], [-0.1546810103404629], [0.15853057545495458]])

def fish_eye_fix(image):
    # this program is quoted from others, see more information in fisheye_fix.py
    dim1 = image.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    if dim1[0]!=DIM[0]:
        image = cv2.resize(image,DIM,interpolation=cv2.INTER_AREA)
    Knew = K.copy()
    Knew[(0,1), (0,1)] = 0.6 * Knew[(0,1), (0,1)] #scaling
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), Knew, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    img_valid  = cut(undistorted_img)
    return img_valid

def cut(img):
    x,y,w,h = 475,254,1536,864
    img_valid = img[y:y+h, x:x+w]
    img_valid = cv2.resize(img_valid, (1280, 720), interpolation=cv2.INTER_AREA)
    return img_valid
