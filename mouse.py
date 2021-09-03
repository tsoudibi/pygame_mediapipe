# ---------------------------------------------------
# this file use mediapipe hands to detect hands and 
# use the result as mouse
# ---------------------------------------------------

import cv2
import math

# other file import

# define mouse class
class Mouse():
    def __init__(self,idx = 0, x = 0, y = 0, size = 10, color = (255, 126, 79), thickness = -1, distence = 999):
        self.idx = idx
        self.x = x
        self.y = y 
        self.size = size
        self.color = color
        self.thickness = thickness
        self.distence = distence
    
    def set_position(self, x, y):
        self.x = x
        self.y = y 
    def set_color(self, color):
        self.color = color
    def set_distence(self, distence):
        self.distence = distence
    
    # draw the connection between two fingers
    def display(self, image, results):
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
                    if hands_idx == self.idx :
                        self.set_distence(math.isqrt((THUMB_TIP_x - INDEX_FINGER_TIP_x)**2 + (THUMB_TIP_y - INDEX_FINGER_TIP_y)**2))
                        self.set_position( round((THUMB_TIP_x + INDEX_FINGER_TIP_x)/2), round((THUMB_TIP_y + INDEX_FINGER_TIP_y)/2))
                        cv2.circle(image, ( self.x, self.y ), int(self.distence * 0.15), self.color, self.thickness)
        return image