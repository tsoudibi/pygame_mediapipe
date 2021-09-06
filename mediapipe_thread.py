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

class mediapipe_data(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self )
        # dynamic settings of mediapipe thread
        self.MP_MODE = 'hands'
        self.MP_LOOP = True
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
            time1 = time.time()
            success, image = camera.read()
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

def caculate_mouse(mouse_1, mouse_2, image, results):
        SCREEN_HEIGHT, SCREEN_WIDTH, _ = image.shape
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
                        mouse_1.set_distence(math.isqrt((THUMB_TIP_x - INDEX_FINGER_TIP_x)**2 + (THUMB_TIP_y - INDEX_FINGER_TIP_y)**2))
                        mouse_1.set_position( round((THUMB_TIP_x + INDEX_FINGER_TIP_x)/2), round((THUMB_TIP_y + INDEX_FINGER_TIP_y)/2))
                        cv2.circle(image, ( mouse_1.x, mouse_1.y ), int(mouse_1.distence * 0.15), mouse_1.color, mouse_1.thickness)
                    elif hands_idx == 1 :
                        mouse_2.set_distence(math.isqrt((THUMB_TIP_x - INDEX_FINGER_TIP_x)**2 + (THUMB_TIP_y - INDEX_FINGER_TIP_y)**2))
                        mouse_2.set_position( round((THUMB_TIP_x + INDEX_FINGER_TIP_x)/2), round((THUMB_TIP_y + INDEX_FINGER_TIP_y)/2))
                        cv2.circle(image, ( mouse_2.x, mouse_2.y ), int(mouse_2.distence * 0.15), mouse_2.color, mouse_2.thickness)
                    else:
                        print("unexpected hands")



        
